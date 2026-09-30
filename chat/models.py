from django.conf import settings
from django.db import models
from django.db.models import Q


class Friendship(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        DECLINED = 'DECLINED', 'Declined'

    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'{self.from_user} -> {self.to_user} ({self.status})'

    @staticmethod
    def are_friends(user_a, user_b):
        return Friendship.objects.filter(
            Q(from_user=user_a, to_user=user_b) | Q(from_user=user_b, to_user=user_a),
            status=Friendship.Status.ACCEPTED,
        ).exists()

    @staticmethod
    def friends_of(user):
        accepted = Friendship.objects.filter(
            Q(from_user=user) | Q(to_user=user), status=Friendship.Status.ACCEPTED,
        ).select_related('from_user', 'to_user')
        return [f.to_user if f.from_user_id == user.id else f.from_user for f in accepted]


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender} -> {self.recipient}: {self.body[:30]}'
