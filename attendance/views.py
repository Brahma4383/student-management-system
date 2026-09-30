import csv
import io

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from academics.models import Section, Subject, TeacherSubjectAssignment
from accounts.decorators import admin_required, student_required, teacher_required
from accounts.models import StudentProfile
from attendance.forms import AttendanceSessionForm, BulkAttendanceUploadForm
from attendance.models import AttendanceRecord

VALID_STATUSES = {c for c, _ in AttendanceRecord.Status.choices}


def _require_teaches(teacher, subject, section):
    """Guards against a teacher marking attendance for a subject-section pair
    they aren't assigned to, e.g. via a hand-edited URL."""
    if not TeacherSubjectAssignment.teaches(teacher, subject, section):
        raise PermissionDenied("You aren't assigned to teach this subject for this section.")


@teacher_required
def mark_attendance(request):
    subject_id = request.GET.get('subject') or request.POST.get('subject')
    section_id = request.GET.get('section') or request.POST.get('section')
    date_str = request.GET.get('date') or request.POST.get('date')

    session_form = AttendanceSessionForm(teacher=request.user, initial={
        'subject': subject_id, 'section': section_id, 'date': date_str,
    })

    subject = section = attendance_date = None
    students = []

    if subject_id and section_id and date_str:
        subject = get_object_or_404(Subject, pk=subject_id)
        section = get_object_or_404(Section, pk=section_id)
        attendance_date = parse_date(date_str)
        _require_teaches(request.user, subject, section)

        if request.method == 'POST':
            existing = {r.student_id: r for r in AttendanceRecord.objects.filter(
                subject=subject, date=attendance_date, student__student_profile__section=section)}
            saved = 0
            for profile in section.students.select_related('user'):
                key = f'status_{profile.user_id}'
                status = request.POST.get(key)
                if status not in VALID_STATUSES:
                    continue
                record = existing.get(profile.user_id)
                if record:
                    record.status = status
                    record.marked_by = request.user
                    record.save()
                else:
                    AttendanceRecord.objects.create(
                        student=profile.user, subject=subject, date=attendance_date,
                        status=status, marked_by=request.user,
                    )
                saved += 1
            messages.success(request, f'Attendance saved for {saved} student(s) on {attendance_date}.')
            return redirect(f"{request.path}?subject={subject_id}&section={section_id}&date={date_str}")

        existing_map = {r.student_id: r.status for r in AttendanceRecord.objects.filter(
            subject=subject, date=attendance_date, student__student_profile__section=section)}
        students = [
            {'profile': p, 'status': existing_map.get(p.user_id, AttendanceRecord.Status.PRESENT)}
            for p in section.students.select_related('user').order_by('user__first_name', 'user__username')
        ]

    return render(request, 'attendance/mark.html', {
        'session_form': session_form, 'subject': subject, 'section': section,
        'attendance_date': attendance_date, 'students': students, 'statuses': AttendanceRecord.Status.choices,
    })


@teacher_required
def bulk_upload_attendance(request):
    result = None
    if request.method == 'POST':
        form = BulkAttendanceUploadForm(request.POST, request.FILES, teacher=request.user)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            section = form.cleaned_data['section']
            attendance_date = form.cleaned_data['date']
            csv_file = form.cleaned_data['csv_file']
            _require_teaches(request.user, subject, section)

            decoded = io.TextIOWrapper(csv_file.file, encoding='utf-8-sig')
            reader = csv.DictReader(decoded)
            fieldnames = [f.strip().lower() for f in (reader.fieldnames or [])]

            created, updated, errors = 0, 0, []
            if 'admission_number' not in fieldnames or 'status' not in fieldnames:
                errors.append('CSV must have "admission_number" and "status" columns.')
            else:
                section_admissions = {
                    p.admission_number: p for p in StudentProfile.objects.filter(section=section)
                }
                for row_num, row in enumerate(reader, start=2):
                    row = {k.strip().lower(): (v or '').strip() for k, v in row.items()}
                    adm = row.get('admission_number', '')
                    status = row.get('status', '').upper()
                    if not adm:
                        continue
                    profile = section_admissions.get(adm)
                    if not profile:
                        errors.append(f'Row {row_num}: no student with admission number "{adm}" in this section.')
                        continue
                    if status not in VALID_STATUSES:
                        errors.append(f'Row {row_num}: invalid status "{status}" for {adm}.')
                        continue
                    _, was_created = AttendanceRecord.objects.update_or_create(
                        student=profile.user, subject=subject, date=attendance_date,
                        defaults={'status': status, 'marked_by': request.user},
                    )
                    created += 1 if was_created else 0
                    updated += 0 if was_created else 1

            result = {'created': created, 'updated': updated, 'errors': errors}
            if created or updated:
                messages.success(request, f'Bulk upload done: {created} created, {updated} updated.')
    else:
        form = BulkAttendanceUploadForm(teacher=request.user)

    return render(request, 'attendance/bulk_upload.html', {'form': form, 'result': result})


@teacher_required
def attendance_csv_template(request):
    section_id = request.GET.get('section')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_template.csv"'
    writer = csv.writer(response)
    writer.writerow(['admission_number', 'student_name', 'status'])
    if section_id:
        section = get_object_or_404(Section, pk=section_id)
        for profile in section.students.select_related('user').order_by('user__first_name'):
            writer.writerow([profile.admission_number, profile.user.get_full_name() or profile.user.username, 'PRESENT'])
    return response


@student_required
def student_attendance(request):
    profile = request.user.student_profile
    records = AttendanceRecord.objects.filter(student=request.user).select_related('subject').order_by('-date')

    by_subject = {}
    for record in records:
        stats = by_subject.setdefault(record.subject, {'total': 0, 'present': 0})
        stats['total'] += 1
        if record.status in (AttendanceRecord.Status.PRESENT, AttendanceRecord.Status.LATE):
            stats['present'] += 1
    for stats in by_subject.values():
        stats['percentage'] = round(100 * stats['present'] / stats['total'], 1) if stats['total'] else 0

    return render(request, 'attendance/student_view.html', {
        'records': records[:100], 'by_subject': by_subject, 'profile': profile,
    })


@admin_required
def admin_attendance_overview(request):
    section_id = request.GET.get('section', '').strip()
    date_str = request.GET.get('date', '').strip()

    records = AttendanceRecord.objects.select_related('student', 'subject', 'student__student_profile__section')
    if section_id:
        records = records.filter(student__student_profile__section_id=section_id)
    if date_str:
        records = records.filter(date=parse_date(date_str))

    return render(request, 'attendance/admin_overview.html', {
        'records': records[:300], 'sections': Section.objects.select_related('school_class').all(),
        'selected_section': section_id, 'selected_date': date_str,
    })
