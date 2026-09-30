from django.conf import settings
from django.db import models


class Exam(models.Model):
    name = models.CharField(max_length=100)
    school_class = models.ForeignKey('academics.SchoolClass', on_delete=models.CASCADE, related_name='exams')
    date = models.DateField()

    class Meta:
        ordering = ['-date']
        unique_together = ('name', 'school_class', 'date')

    def __str__(self):
        return f'{self.name} - {self.school_class} ({self.date})'


class Result(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        limit_choices_to={'role': 'STUDENT'}, related_name='results',
    )
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='results_entered',
    )
    remarks = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('exam', 'student', 'subject')
        ordering = ['-exam__date']

    def __str__(self):
        return f'{self.student} - {self.subject} - {self.exam}: {self.marks_obtained}/{self.max_marks}'

    @property
    def percentage(self):
        if not self.max_marks:
            return 0
        return round(float(self.marks_obtained) / float(self.max_marks) * 100, 1)
