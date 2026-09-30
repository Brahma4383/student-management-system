from django.conf import settings
from django.db import models


class SchoolClass(models.Model):
    """E.g. 'Class 10' or 'BCA Year 2'."""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'School classes'

    def __str__(self):
        return self.name


class Section(models.Model):
    """E.g. Section 'A' of 'Class 10'."""
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=10)
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        limit_choices_to={'role': 'TEACHER'}, related_name='class_teacher_of',
    )

    class Meta:
        ordering = ['school_class__name', 'name']
        unique_together = ('school_class', 'name')

    def __str__(self):
        return f'{self.school_class.name} - {self.name}'


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='subjects')

    class Meta:
        ordering = ['school_class__name', 'name']
        unique_together = ('school_class', 'code')

    def __str__(self):
        return f'{self.name} ({self.code})'


class TeacherSubjectAssignment(models.Model):
    """Which teacher teaches which subject to which section."""
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        limit_choices_to={'role': 'TEACHER'}, related_name='teaching_assignments',
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teacher_assignments')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='teacher_assignments')

    class Meta:
        unique_together = ('teacher', 'subject', 'section')
        ordering = ['section__school_class__name', 'section__name', 'subject__name']

    def __str__(self):
        return f'{self.teacher} teaches {self.subject} to {self.section}'

    @staticmethod
    def teaches(teacher, subject, section):
        """True if `teacher` is assigned to teach `subject` for `section`.

        Used to stop a teacher acting on a subject/section pair they merely
        teach *something* in (e.g. via a hand-edited URL) rather than the
        specific combination requested.
        """
        return TeacherSubjectAssignment.objects.filter(teacher=teacher, subject=subject, section=section).exists()
