from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from accounts.decorators import admin_required
from accounts.forms import (
    ChangePasswordForm, LoginForm, ProfileForm, ResetPasswordForm,
    StudentCreateForm, StudentEditForm, TeacherCreateForm, TeacherEditForm,
)
from accounts.models import User
from academics.models import SchoolClass, Section, Subject
from assignments.models import Assignment
from attendance.models import AttendanceRecord


class RoleAwareLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('accounts:dashboard')


class RoleAwareLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')


def index(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return redirect('accounts:login')


@login_required
def dashboard_redirect(request):
    user = request.user
    if user.is_admin:
        return redirect('accounts:admin_dashboard')
    if user.is_teacher:
        return redirect('teacher:dashboard')
    if user.is_student:
        return redirect('student:dashboard')
    return redirect('accounts:login')


@admin_required
def admin_dashboard(request):
    context = {
        'teacher_count': User.objects.filter(role=User.Role.TEACHER).count(),
        'student_count': User.objects.filter(role=User.Role.STUDENT).count(),
        'class_count': SchoolClass.objects.count(),
        'subject_count': Subject.objects.count(),
        'section_count': Section.objects.count(),
        'assignment_count': Assignment.objects.count(),
        'attendance_count': AttendanceRecord.objects.count(),
        'recent_teachers': User.objects.filter(role=User.Role.TEACHER).order_by('-created_at')[:5],
        'recent_students': User.objects.filter(role=User.Role.STUDENT).order_by('-created_at')[:5],
    }
    return render(request, 'accounts/admin_dashboard.html', context)


# --- Teacher management (admin only) ---------------------------------------

@admin_required
def teacher_list(request):
    query = request.GET.get('q', '').strip()
    teachers = User.objects.filter(role=User.Role.TEACHER).select_related('teacher_profile')
    if query:
        teachers = teachers.filter(username__icontains=query) | teachers.filter(
            first_name__icontains=query) | teachers.filter(last_name__icontains=query)
    return render(request, 'accounts/teacher_list.html', {'teachers': teachers, 'query': query})


@admin_required
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherCreateForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, f'Teacher account created for {teacher.get_full_name() or teacher.username}.')
            return redirect('accounts:teacher_list')
    else:
        form = TeacherCreateForm()
    return render(request, 'accounts/teacher_form.html', {'form': form, 'mode': 'create'})


@admin_required
def teacher_edit(request, pk):
    teacher = get_object_or_404(User, pk=pk, role=User.Role.TEACHER)
    if request.method == 'POST':
        form = TeacherEditForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher details updated.')
            return redirect('accounts:teacher_list')
    else:
        form = TeacherEditForm(instance=teacher)
    return render(request, 'accounts/teacher_form.html', {'form': form, 'mode': 'edit', 'teacher': teacher})


@admin_required
def teacher_delete(request, pk):
    teacher = get_object_or_404(User, pk=pk, role=User.Role.TEACHER)
    if request.method == 'POST':
        name = teacher.get_full_name() or teacher.username
        teacher.delete()
        messages.success(request, f'Removed teacher account for {name}.')
        return redirect('accounts:teacher_list')
    return render(request, 'partials/confirm_delete.html', {'object': teacher, 'cancel_url': 'accounts:teacher_list'})


# --- Student management (admin only) ---------------------------------------

@admin_required
def student_list(request):
    query = request.GET.get('q', '').strip()
    section_id = request.GET.get('section', '').strip()
    students = User.objects.filter(role=User.Role.STUDENT).select_related('student_profile', 'student_profile__section')
    if query:
        students = students.filter(username__icontains=query) | students.filter(
            first_name__icontains=query) | students.filter(last_name__icontains=query) | students.filter(
            student_profile__admission_number__icontains=query)
    if section_id:
        students = students.filter(student_profile__section_id=section_id)
    return render(request, 'accounts/student_list.html', {
        'students': students, 'query': query, 'sections': Section.objects.select_related('school_class').all(),
        'selected_section': section_id,
    })


@admin_required
def student_create(request):
    if request.method == 'POST':
        form = StudentCreateForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student account created for {student.get_full_name() or student.username}.')
            return redirect('accounts:student_list')
    else:
        form = StudentCreateForm()
    return render(request, 'accounts/student_form.html', {'form': form, 'mode': 'create'})


@admin_required
def student_edit(request, pk):
    student = get_object_or_404(User, pk=pk, role=User.Role.STUDENT)
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student details updated.')
            return redirect('accounts:student_list')
    else:
        form = StudentEditForm(instance=student)
    return render(request, 'accounts/student_form.html', {'form': form, 'mode': 'edit', 'student': student})


@admin_required
def student_delete(request, pk):
    student = get_object_or_404(User, pk=pk, role=User.Role.STUDENT)
    if request.method == 'POST':
        name = student.get_full_name() or student.username
        student.delete()
        messages.success(request, f'Removed student account for {name}.')
        return redirect('accounts:student_list')
    return render(request, 'partials/confirm_delete.html', {'object': student, 'cancel_url': 'accounts:student_list'})


@admin_required
def reset_password(request, pk, role):
    user_obj = get_object_or_404(User, pk=pk, role=role)
    list_url = 'accounts:teacher_list' if role == User.Role.TEACHER else 'accounts:student_list'
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user_obj.set_password(form.cleaned_data['new_password'])
            user_obj.save()
            messages.success(request, f"Password reset for {user_obj.get_full_name() or user_obj.username}.")
            return redirect(list_url)
    else:
        form = ResetPasswordForm()
    return render(request, 'accounts/reset_password.html', {'form': form, 'target_user': user_obj, 'list_url': list_url})


# --- Shared profile views (any role) ----------------------------------------

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed.')
            return redirect('accounts:profile')
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
