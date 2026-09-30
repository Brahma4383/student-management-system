from django.shortcuts import render
from django.utils import timezone

from accounts.decorators import student_required
from assignments.models import Assignment, AssignmentSubmission
from attendance.models import AttendanceRecord
from chat.models import Friendship, Message
from results.models import Result


@student_required
def dashboard(request):
    profile = request.user.student_profile
    now = timezone.now()

    upcoming_assignments = []
    if profile.section_id:
        submitted_ids = set(AssignmentSubmission.objects.filter(student=request.user).values_list('assignment_id', flat=True))
        upcoming_assignments = list(
            Assignment.objects.filter(section=profile.section, due_date__gte=now)
            .exclude(id__in=submitted_ids).select_related('subject').order_by('due_date')[:5]
        )

    records = AttendanceRecord.objects.filter(student=request.user)
    total = records.count()
    present = records.filter(status__in=[AttendanceRecord.Status.PRESENT, AttendanceRecord.Status.LATE]).count()
    attendance_percentage = round(100 * present / total, 1) if total else None

    results = Result.objects.filter(student=request.user).select_related('exam').order_by('exam__date')
    by_exam = {}
    for r in results:
        by_exam.setdefault(r.exam, []).append(r)
    exam_percentages = []
    for exam in sorted(by_exam.keys(), key=lambda e: e.date):
        rows = by_exam[exam]
        total_obtained = sum(float(r.marks_obtained) for r in rows)
        total_max = sum(float(r.max_marks) for r in rows)
        exam_percentages.append(round(total_obtained / total_max * 100, 1) if total_max else 0)
    latest_percentage = exam_percentages[-1] if exam_percentages else None
    improvement = round(exam_percentages[-1] - exam_percentages[-2], 1) if len(exam_percentages) >= 2 else None

    unread_messages = Message.objects.filter(recipient=request.user, is_read=False).count()
    friend_count = len(Friendship.friends_of(request.user))

    return render(request, 'student/dashboard.html', {
        'profile': profile,
        'upcoming_assignments': upcoming_assignments,
        'attendance_percentage': attendance_percentage,
        'latest_percentage': latest_percentage,
        'improvement': improvement,
        'unread_messages': unread_messages,
        'friend_count': friend_count,
    })
