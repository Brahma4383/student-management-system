from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from academics.models import Section, Subject, TeacherSubjectAssignment
from accounts.decorators import admin_required, student_required, teacher_required
from results.forms import ExamForm, ResultEntrySessionForm
from results.models import Exam, Result


# --- Admin: exam management -------------------------------------------------

@admin_required
def exam_list(request):
    exams = Exam.objects.select_related('school_class').all()
    return render(request, 'results/exam_list.html', {'exams': exams})


@admin_required
def exam_create(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam created.')
            return redirect('results:exam_list')
    else:
        form = ExamForm()
    return render(request, 'results/exam_form.html', {'form': form, 'mode': 'create'})


@admin_required
def exam_edit(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam updated.')
            return redirect('results:exam_list')
    else:
        form = ExamForm(instance=exam)
    return render(request, 'results/exam_form.html', {'form': form, 'mode': 'edit'})


@admin_required
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        exam.delete()
        messages.success(request, 'Exam deleted.')
        return redirect('results:exam_list')
    return render(request, 'partials/confirm_delete.html', {'object': exam, 'cancel_url': 'results:exam_list'})


@admin_required
def admin_results_overview(request):
    section_id = request.GET.get('section', '').strip()
    exam_id = request.GET.get('exam', '').strip()

    results = Result.objects.select_related('student', 'subject', 'exam', 'student__student_profile__section')
    if section_id:
        results = results.filter(student__student_profile__section_id=section_id)
    if exam_id:
        results = results.filter(exam_id=exam_id)

    return render(request, 'results/admin_overview.html', {
        'results': results[:300], 'sections': Section.objects.select_related('school_class').all(),
        'exams': Exam.objects.all(), 'selected_section': section_id, 'selected_exam': exam_id,
    })


# --- Teacher: marks entry ---------------------------------------------------

@teacher_required
def enter_results(request):
    exam_id = request.GET.get('exam') or request.POST.get('exam')
    subject_id = request.GET.get('subject') or request.POST.get('subject')
    section_id = request.GET.get('section') or request.POST.get('section')

    session_form = ResultEntrySessionForm(teacher=request.user, initial={
        'exam': exam_id, 'subject': subject_id, 'section': section_id,
    })

    exam = subject = section = None
    rows = []

    if exam_id and subject_id and section_id:
        exam = get_object_or_404(Exam, pk=exam_id)
        subject = get_object_or_404(Subject, pk=subject_id)
        section = get_object_or_404(Section, pk=section_id)
        if not TeacherSubjectAssignment.teaches(request.user, subject, section):
            raise PermissionDenied("You aren't assigned to teach this subject for this section.")

        if request.method == 'POST':
            existing = {r.student_id: r for r in Result.objects.filter(
                exam=exam, subject=subject, student__student_profile__section=section)}
            max_marks_raw = (request.POST.get('max_marks') or '100').strip() or '100'
            try:
                max_marks = Decimal(max_marks_raw)
            except InvalidOperation:
                max_marks = Decimal('100')

            saved = 0
            for profile in section.students.select_related('user'):
                raw = (request.POST.get(f'marks_{profile.user_id}') or '').strip()
                if raw == '':
                    continue
                try:
                    marks = Decimal(raw)
                except InvalidOperation:
                    continue
                record = existing.get(profile.user_id)
                if record:
                    record.marks_obtained = marks
                    record.max_marks = max_marks
                    record.graded_by = request.user
                    record.save()
                else:
                    Result.objects.create(
                        exam=exam, subject=subject, student=profile.user,
                        marks_obtained=marks, max_marks=max_marks, graded_by=request.user,
                    )
                saved += 1
            messages.success(request, f'Results saved for {saved} student(s).')
            return redirect(f"{request.path}?exam={exam_id}&subject={subject_id}&section={section_id}")

        existing_map = {r.student_id: r for r in Result.objects.filter(
            exam=exam, subject=subject, student__student_profile__section=section)}
        rows = [
            {'profile': p, 'result': existing_map.get(p.user_id)}
            for p in section.students.select_related('user').order_by('user__first_name', 'user__username')
        ]

    return render(request, 'results/entry.html', {
        'session_form': session_form, 'exam': exam, 'subject': subject, 'section': section, 'rows': rows,
    })


# --- Student: results + improvement ----------------------------------------

@student_required
def student_results(request):
    results = Result.objects.filter(student=request.user).select_related('exam', 'subject').order_by('exam__date')

    by_exam = {}
    for r in results:
        by_exam.setdefault(r.exam, []).append(r)

    trend = []
    for exam in sorted(by_exam.keys(), key=lambda e: e.date):
        rows = by_exam[exam]
        total_obtained = sum(float(r.marks_obtained) for r in rows)
        total_max = sum(float(r.max_marks) for r in rows)
        percentage = round(total_obtained / total_max * 100, 1) if total_max else 0
        trend.append({'exam': exam, 'percentage': percentage, 'rows': rows})

    improvement = None
    if len(trend) >= 2:
        improvement = round(trend[-1]['percentage'] - trend[-2]['percentage'], 1)

    chart_labels = [t['exam'].name for t in trend]
    chart_data = [t['percentage'] for t in trend]

    return render(request, 'results/student_results.html', {
        'trend': list(reversed(trend)), 'improvement': improvement,
        'chart_labels': chart_labels, 'chart_data': chart_data,
    })
