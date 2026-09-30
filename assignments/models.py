from django.conf import settings
from django.db import models


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='assignments')
    section = models.ForeignKey('academics.Section', on_delete=models.CASCADE, related_name='assignments')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        limit_choices_to={'role': 'TEACHER'}, related_name='assignments_created',
    )
    attachment = models.FileField(upload_to='assignments/', blank=True, null=True)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f'{self.title} ({self.subject.name})'

    def submission_for(self, student):
        return self.submissions.filter(student=student).first()


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        limit_choices_to={'role': 'STUDENT'}, related_name='submissions',
    )
    submission_text = models.TextField(blank=True)
    submitted_file = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_graded = models.BooleanField(default=False)
    grade = models.CharField(max_length=10, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.student} -> {self.assignment}'

    @property
    def is_late(self):
        return self.submitted_at > self.assignment.due_date
