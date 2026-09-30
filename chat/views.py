from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from accounts.decorators import student_required
from accounts.models import User
from chat.models import Friendship, Message


@student_required
def find_students(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        candidates = User.objects.filter(role=User.Role.STUDENT).exclude(pk=request.user.pk).filter(
            username__icontains=query) | User.objects.filter(role=User.Role.STUDENT).exclude(
            pk=request.user.pk).filter(first_name__icontains=query) | User.objects.filter(
            role=User.Role.STUDENT).exclude(pk=request.user.pk).filter(last_name__icontains=query)
        candidates = candidates.distinct().select_related('student_profile')

        outgoing = set(Friendship.objects.filter(from_user=request.user).values_list('to_user_id', 'status'))
        incoming = set(Friendship.objects.filter(to_user=request.user).values_list('from_user_id', 'status'))
        outgoing_map = dict(outgoing)
        incoming_map = dict(incoming)

        for student in candidates:
            state = None
            if student.id in outgoing_map:
                state = 'sent' if outgoing_map[student.id] == Friendship.Status.PENDING else outgoing_map[student.id].lower()
            elif student.id in incoming_map:
                state = 'incoming' if incoming_map[student.id] == Friendship.Status.PENDING else incoming_map[student.id].lower()
            results.append({'student': student, 'state': state})

    return render(request, 'chat/find_students.html', {'query': query, 'results': results})


@student_required
@require_POST
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, pk=user_id, role=User.Role.STUDENT)
    if to_user == request.user:
        messages.error(request, "You can't friend yourself.")
        return redirect('chat:find_students')

    reverse_request = Friendship.objects.filter(from_user=to_user, to_user=request.user).first()
    if reverse_request and reverse_request.status == Friendship.Status.PENDING:
        reverse_request.status = Friendship.Status.ACCEPTED
        reverse_request.save()
        messages.success(request, f'You and {to_user.get_full_name() or to_user.username} are now friends.')
        return redirect('chat:find_students')

    friendship, created = Friendship.objects.get_or_create(from_user=request.user, to_user=to_user)
    if not created and friendship.status == Friendship.Status.DECLINED:
        friendship.status = Friendship.Status.PENDING
        friendship.save()
    messages.success(request, 'Friend request sent.')
    return redirect('chat:find_students')


@student_required
def friend_requests(request):
    incoming = Friendship.objects.filter(to_user=request.user, status=Friendship.Status.PENDING).select_related('from_user')
    outgoing = Friendship.objects.filter(from_user=request.user, status=Friendship.Status.PENDING).select_related('to_user')
    return render(request, 'chat/friend_requests.html', {'incoming': incoming, 'outgoing': outgoing})


@student_required
@require_POST
def respond_friend_request(request, pk, action):
    friend_request = get_object_or_404(Friendship, pk=pk, to_user=request.user, status=Friendship.Status.PENDING)
    if action == 'accept':
        friend_request.status = Friendship.Status.ACCEPTED
    else:
        friend_request.status = Friendship.Status.DECLINED
    friend_request.save()
    messages.success(request, 'Friend request updated.')
    return redirect('chat:friend_requests')


@student_required
def inbox(request):
    friends = Friendship.friends_of(request.user)
    friend_data = []
    for friend in friends:
        last_message = Message.objects.filter(
            sender__in=[request.user, friend], recipient__in=[request.user, friend],
        ).order_by('-timestamp').first()
        unread = Message.objects.filter(sender=friend, recipient=request.user, is_read=False).count()
        friend_data.append({'friend': friend, 'last_message': last_message, 'unread': unread})
    friend_data.sort(key=lambda d: d['last_message'].timestamp if d['last_message'] else d['friend'].date_joined, reverse=True)
    return render(request, 'chat/inbox.html', {'friend_data': friend_data})


@student_required
def conversation(request, user_id):
    friend = get_object_or_404(User, pk=user_id, role=User.Role.STUDENT)
    if not Friendship.are_friends(request.user, friend):
        messages.error(request, 'You can only chat with friends.')
        return redirect('chat:find_students')

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(sender=request.user, recipient=friend, body=body)
        return redirect('chat:conversation', user_id=friend.id)

    Message.objects.filter(sender=friend, recipient=request.user, is_read=False).update(is_read=True)
    thread = Message.objects.filter(
        sender__in=[request.user, friend], recipient__in=[request.user, friend],
    ).select_related('sender')

    return render(request, 'chat/conversation.html', {'friend': friend, 'thread': thread})


@student_required
def poll_messages(request, user_id):
    """Lightweight JSON endpoint the conversation page polls for new messages."""
    friend = get_object_or_404(User, pk=user_id, role=User.Role.STUDENT)
    if not Friendship.are_friends(request.user, friend):
        return JsonResponse({'error': 'not friends'}, status=403)

    after_id = request.GET.get('after', '0')
    try:
        after_id = int(after_id)
    except ValueError:
        after_id = 0

    new_messages = Message.objects.filter(
        sender__in=[request.user, friend], recipient__in=[request.user, friend], pk__gt=after_id,
    ).select_related('sender')
    new_messages.filter(sender=friend, recipient=request.user).update(is_read=True)

    html = render_to_string('chat/_messages.html', {'thread': new_messages, 'friend': friend}, request=request)
    last_id = new_messages.last().id if new_messages else after_id
    return JsonResponse({'html': html, 'last_id': last_id, 'count': new_messages.count()})
