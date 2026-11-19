from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from accounts.models import StudentProfile, TeacherProfile, User


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    fieldsets = AuthUserAdmin.fieldsets + (
        ('School', {'fields': ('role', 'phone_number', 'profile_photo')}),
    )
    add_fieldsets = AuthUserAdmin.add_fieldsets + (
        ('School', {'fields': ('role',)}),
    )
    list_display = ('username', 'get_full_name', 'email', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'department', 'joined_on')
    search_fields = ('employee_id', 'user__username', 'user__first_name', 'user__last_name')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'user', 'section', 'guardian_name', 'guardian_phone')
    list_filter = ('section',)
    search_fields = ('admission_number', 'user__username', 'user__first_name', 'user__last_name')
