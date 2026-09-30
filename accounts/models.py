from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import UserManager


class User(AbstractUser):
    """Custom user for all three roles: admin, teacher, student.

    SECURITY NOTE: per project requirements, passwords are stored in PLAIN TEXT,
    not hashed. set_password()/check_password() below are the only two places
    this is implemented - Django's normal auth flow (login, admin, forms) is
    otherwise untouched, so it keeps working with plain-text values.
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        TEACHER = 'TEACHER', 'Teacher'
        STUDENT = 'STUDENT', 'Student'

    role = models.CharField(max_length=10, choices=Role.choices)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    def set_password(self, raw_password):
        # Plain-text storage by design (see class docstring). No hashing.
        self.password = raw_password

    def check_password(self, raw_password):
        return self.password == raw_password

    def has_usable_password(self):
        return True

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, blank=True)
    joined_on = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} · {self.employee_id}'


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=20, unique=True)
    section = models.ForeignKey(
        'academics.Section', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='students',
    )
    date_of_birth = models.DateField(null=True, blank=True)
    guardian_name = models.CharField(max_length=150, blank=True)
    guardian_phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} · {self.admission_number}'
