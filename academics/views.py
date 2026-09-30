from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from academics.forms import SchoolClassForm, SectionForm, SubjectForm, TeacherSubjectAssignmentForm
from academics.models import SchoolClass, Section, Subject, TeacherSubjectAssignment
from accounts.decorators import admin_required


@admin_required
def class_list(request):
    classes = SchoolClass.objects.prefetch_related('sections', 'subjects').all()
    return render(request, 'academics/class_list.html', {'classes': classes})


@admin_required
def class_create(request):
    if request.method == 'POST':
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class created.')
            return redirect('academics:class_list')
    else:
        form = SchoolClassForm()
    return render(request, 'academics/class_form.html', {'form': form, 'mode': 'create'})


@admin_required
def class_edit(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    if request.method == 'POST':
        form = SchoolClassForm(request.POST, instance=school_class)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated.')
            return redirect('academics:class_list')
    else:
        form = SchoolClassForm(instance=school_class)
    return render(request, 'academics/class_form.html', {'form': form, 'mode': 'edit'})


@admin_required
def class_delete(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    if request.method == 'POST':
        school_class.delete()
        messages.success(request, 'Class deleted.')
        return redirect('academics:class_list')
    return render(request, 'partials/confirm_delete.html', {'object': school_class, 'cancel_url': 'academics:class_list'})


@admin_required
def section_create(request):
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section created.')
            return redirect('academics:class_list')
    else:
        form = SectionForm(initial={'school_class': request.GET.get('school_class')})
    return render(request, 'academics/section_form.html', {'form': form, 'mode': 'create'})


@admin_required
def section_edit(request, pk):
    section = get_object_or_404(Section, pk=pk)
    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section updated.')
            return redirect('academics:class_list')
    else:
        form = SectionForm(instance=section)
    return render(request, 'academics/section_form.html', {'form': form, 'mode': 'edit'})


@admin_required
def section_delete(request, pk):
    section = get_object_or_404(Section, pk=pk)
    if request.method == 'POST':
        section.delete()
        messages.success(request, 'Section deleted.')
        return redirect('academics:class_list')
    return render(request, 'partials/confirm_delete.html', {'object': section, 'cancel_url': 'academics:class_list'})


@admin_required
def subject_list(request):
    subjects = Subject.objects.select_related('school_class').all()
    return render(request, 'academics/subject_list.html', {'subjects': subjects})


@admin_required
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject created.')
            return redirect('academics:subject_list')
    else:
        form = SubjectForm()
    return render(request, 'academics/subject_form.html', {'form': form, 'mode': 'create'})


@admin_required
def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated.')
            return redirect('academics:subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'academics/subject_form.html', {'form': form, 'mode': 'edit'})


@admin_required
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted.')
        return redirect('academics:subject_list')
    return render(request, 'partials/confirm_delete.html', {'object': subject, 'cancel_url': 'academics:subject_list'})


@admin_required
def teaching_assignment_list(request):
    assignments = TeacherSubjectAssignment.objects.select_related('teacher', 'subject', 'section', 'section__school_class')
    return render(request, 'academics/teaching_assignment_list.html', {'assignments': assignments})


@admin_required
def teaching_assignment_create(request):
    if request.method == 'POST':
        form = TeacherSubjectAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teaching assignment created.')
            return redirect('academics:teaching_assignment_list')
    else:
        form = TeacherSubjectAssignmentForm()
    return render(request, 'academics/teaching_assignment_form.html', {'form': form})


@admin_required
def teaching_assignment_delete(request, pk):
    assignment = get_object_or_404(TeacherSubjectAssignment, pk=pk)
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Teaching assignment removed.')
        return redirect('academics:teaching_assignment_list')
    return render(request, 'partials/confirm_delete.html', {'object': assignment, 'cancel_url': 'academics:teaching_assignment_list'})
