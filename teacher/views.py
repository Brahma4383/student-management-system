from django.utils import timezone

from academics.models import TeacherSubjectAssignment
from accounts.decorators import teacher_required
from assignments.models import Assignment, AssignmentSubmission
from django.shortcuts import render


@teacher_required
def dashboard(request):
    assignments_qs = TeacherSubjectAssignment.objects.filter(teacher=request.user).select_related(
        'subject', 'section', 'section__school_class')

    my_assignments = Assignment.objects.filter(created_by=request.user).select_related('subject', 'section')
    pending_grading = AssignmentSubmission.objects.filter(
        assignment__created_by=request.user, is_graded=False).select_related('assignment', 'student')

    context = {
        'teaching_assignments': assignments_qs,
        'section_count': assignments_qs.values('section').distinct().count(),
        'subject_count': assignments_qs.values('subject').distinct().count(),
        'recent_assignments': my_assignments[:5],
        'assignment_count': my_assignments.count(),
        'pending_grading': pending_grading[:8],
        'pending_grading_count': pending_grading.count(),
        'today': timezone.localdate(),
    }
    return render(request, 'teacher/dashboard.html', context)
