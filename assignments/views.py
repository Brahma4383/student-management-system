from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from academics.models import TeacherSubjectAssignment
from accounts.decorators import student_required, teacher_required
from assignments.forms import AssignmentForm, GradeForm, SubmissionForm
from assignments.models import Assignment, AssignmentSubmission


# --- Teacher side -------------------------------------------------------

@teacher_required
def teacher_assignment_list(request):
    assignments = Assignment.objects.filter(created_by=request.user).select_related('subject', 'section')
    return render(request, 'assignments/teacher_list.html', {'assignments': assignments})


@teacher_required
def assignment_create(request):
    if not TeacherSubjectAssignment.objects.filter(teacher=request.user).exists():
        messages.error(request, "You aren't assigned to teach any subject/section yet. Ask an admin to set that up.")
        return redirect('assignments:teacher_list')

    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, teacher=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, 'Assignment posted.')
            return redirect('assignments:teacher_list')
    else:
        form = AssignmentForm(teacher=request.user)
    return render(request, 'assignments/assignment_form.html', {'form': form, 'mode': 'create'})


@teacher_required
def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment, teacher=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated.')
            return redirect('assignments:teacher_list')
    else:
        form = AssignmentForm(instance=assignment, teacher=request.user)
    return render(request, 'assignments/assignment_form.html', {'form': form, 'mode': 'edit'})


@teacher_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted.')
        return redirect('assignments:teacher_list')
    return render(request, 'partials/confirm_delete.html', {'object': assignment, 'cancel_url': 'assignments:teacher_list'})


@teacher_required
def assignment_submissions(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    submissions = assignment.submissions.select_related('student', 'student__student_profile')
    submitted_ids = set(submissions.values_list('student_id', flat=True))
    pending_students = assignment.section.students.select_related('user').exclude(user_id__in=submitted_ids)
    return render(request, 'assignments/submissions.html', {
        'assignment': assignment, 'submissions': submissions, 'pending_students': pending_students,
    })


@teacher_required
def grade_submission(request, pk):
    submission = get_object_or_404(AssignmentSubmission, pk=pk, assignment__created_by=request.user)
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade saved.')
            return redirect('assignments:submissions', pk=submission.assignment_id)
    else:
        form = GradeForm(instance=submission)
    return render(request, 'assignments/grade_form.html', {'form': form, 'submission': submission})


# --- Student side ---------------------------------------------------------

@student_required
def student_assignment_list(request):
    profile = request.user.student_profile
    assignments = Assignment.objects.none()
    if profile.section_id:
        assignments = Assignment.objects.filter(section=profile.section).select_related('subject')
    my_submissions = {s.assignment_id: s for s in AssignmentSubmission.objects.filter(student=request.user)}
    now = timezone.now()
    return render(request, 'assignments/student_list.html', {
        'assignments': assignments, 'my_submissions': my_submissions, 'now': now,
    })


@student_required
def assignment_submit(request, pk):
    profile = request.user.student_profile
    assignment = get_object_or_404(Assignment, pk=pk, section=profile.section)
    submission = assignment.submissions.filter(student=request.user).first()

    if submission and submission.is_graded:
        messages.info(request, 'This submission has already been graded and can no longer be edited.')
        return redirect('assignments:student_list')

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            new_submission = form.save(commit=False)
            new_submission.assignment = assignment
            new_submission.student = request.user
            new_submission.save()
            messages.success(request, 'Submission saved.')
            return redirect('assignments:student_list')
    else:
        form = SubmissionForm(instance=submission)
    return render(request, 'assignments/submit_form.html', {'form': form, 'assignment': assignment, 'submission': submission})
