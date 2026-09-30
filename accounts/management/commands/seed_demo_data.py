import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from academics.models import SchoolClass, Section, Subject, TeacherSubjectAssignment
from accounts.models import StudentProfile, TeacherProfile, User
from assignments.models import Assignment, AssignmentSubmission
from attendance.models import AttendanceRecord
from chat.models import Friendship, Message
from results.models import Exam, Result


class Command(BaseCommand):
    help = 'Creates demo classes, teachers, students, and sample activity data. Safe to re-run.'

    def handle(self, *args, **options):
        today = timezone.localdate()

        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'role': User.Role.ADMIN, 'is_staff': True, 'is_superuser': True,
                      'first_name': 'System', 'last_name': 'Admin', 'email': 'admin@example.com'},
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        self.stdout.write(self.style.SUCCESS(f'Admin: admin / admin123'))

        class10, _ = SchoolClass.objects.get_or_create(name='Class 10')
        class9, _ = SchoolClass.objects.get_or_create(name='Class 9')

        section_10a, _ = Section.objects.get_or_create(school_class=class10, name='A')
        section_10b, _ = Section.objects.get_or_create(school_class=class10, name='B')
        section_9a, _ = Section.objects.get_or_create(school_class=class9, name='A')

        math10, _ = Subject.objects.get_or_create(code='MATH10', defaults={'name': 'Mathematics', 'school_class': class10})
        sci10, _ = Subject.objects.get_or_create(code='SCI10', defaults={'name': 'Science', 'school_class': class10})
        eng10, _ = Subject.objects.get_or_create(code='ENG10', defaults={'name': 'English', 'school_class': class10})
        math9, _ = Subject.objects.get_or_create(code='MATH9', defaults={'name': 'Mathematics', 'school_class': class9})
        eng9, _ = Subject.objects.get_or_create(code='ENG9', defaults={'name': 'English', 'school_class': class9})

        teachers_data = [
            ('t.sharma', 'Anita', 'Sharma', 'EMP001', 'Mathematics'),
            ('t.verma', 'Raj', 'Verma', 'EMP002', 'Science'),
            ('t.gupta', 'Priya', 'Gupta', 'EMP003', 'English'),
        ]
        teachers = {}
        for username, first, last, emp_id, dept in teachers_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'role': User.Role.TEACHER, 'first_name': first, 'last_name': last,
                          'email': f'{username}@example.com'},
            )
            if created:
                user.set_password('teach123')
                user.save()
                TeacherProfile.objects.create(user=user, employee_id=emp_id, department=dept, joined_on=today)
            teachers[username] = user
        self.stdout.write(self.style.SUCCESS('Teachers: t.sharma / t.verma / t.gupta, password teach123'))

        section_10a.class_teacher = teachers['t.sharma']
        section_10a.save()

        assignments_map = [
            (teachers['t.sharma'], math10, section_10a),
            (teachers['t.sharma'], math9, section_9a),
            (teachers['t.verma'], sci10, section_10a),
            (teachers['t.gupta'], eng10, section_10a),
            (teachers['t.gupta'], eng9, section_9a),
        ]
        for teacher, subject, section in assignments_map:
            TeacherSubjectAssignment.objects.get_or_create(teacher=teacher, subject=subject, section=section)

        students_data = [
            ('s.aarav', 'Aarav', 'Kumar', 'ADM001', section_10a),
            ('s.diya', 'Diya', 'Singh', 'ADM002', section_10a),
            ('s.ishaan', 'Ishaan', 'Patel', 'ADM003', section_10a),
            ('s.kavya', 'Kavya', 'Reddy', 'ADM004', section_10a),
            ('s.vihaan', 'Vihaan', 'Shah', 'ADM005', section_10b),
            ('s.ananya', 'Ananya', 'Nair', 'ADM006', section_10b),
            ('s.arjun', 'Arjun', 'Rao', 'ADM007', section_9a),
            ('s.myra', 'Myra', 'Iyer', 'ADM008', section_9a),
        ]
        students = {}
        for username, first, last, adm, section in students_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'role': User.Role.STUDENT, 'first_name': first, 'last_name': last,
                          'email': f'{username}@example.com'},
            )
            if created:
                user.set_password('pass123')
                user.save()
                StudentProfile.objects.create(
                    user=user, admission_number=adm, section=section,
                    date_of_birth=datetime.date(2010, 6, 15),
                    guardian_name=f'Guardian of {first}', guardian_phone='9999999999',
                )
            students[username] = user
        self.stdout.write(self.style.SUCCESS('Students: s.aarav ... s.myra, password pass123'))

        mid_term, _ = Exam.objects.get_or_create(name='Mid Term', school_class=class10,
                                                   date=today - datetime.timedelta(days=45))
        final_term, _ = Exam.objects.get_or_create(name='Final Term', school_class=class10,
                                                     date=today - datetime.timedelta(days=5))

        section_10a_students = ['s.aarav', 's.diya', 's.ishaan', 's.kavya']
        base_marks = {'s.aarav': 62, 's.diya': 78, 's.ishaan': 55, 's.kavya': 88}
        improvement = {'s.aarav': 12, 's.diya': 6, 's.ishaan': -4, 's.kavya': 5}
        for username in section_10a_students:
            student = students[username]
            for subject in (math10, sci10, eng10):
                Result.objects.get_or_create(
                    exam=mid_term, student=student, subject=subject,
                    defaults={'marks_obtained': base_marks[username], 'max_marks': 100, 'graded_by': teachers['t.sharma']},
                )
                Result.objects.get_or_create(
                    exam=final_term, student=student, subject=subject,
                    defaults={'marks_obtained': min(100, base_marks[username] + improvement[username]),
                              'max_marks': 100, 'graded_by': teachers['t.sharma']},
                )

        for day_offset in range(10, 0, -1):
            record_date = today - datetime.timedelta(days=day_offset)
            if record_date.weekday() >= 5:
                continue
            for username in section_10a_students:
                status = AttendanceRecord.Status.ABSENT if (day_offset == 7 and username == 's.ishaan') else AttendanceRecord.Status.PRESENT
                AttendanceRecord.objects.get_or_create(
                    student=students[username], subject=math10, date=record_date,
                    defaults={'status': status, 'marked_by': teachers['t.sharma']},
                )

        assignment, _ = Assignment.objects.get_or_create(
            title='Algebra worksheet 1', subject=math10, section=section_10a, created_by=teachers['t.sharma'],
            defaults={'description': 'Solve all questions in chapter 3 and show your working.',
                      'due_date': timezone.now() + datetime.timedelta(days=5)},
        )
        AssignmentSubmission.objects.get_or_create(
            assignment=assignment, student=students['s.diya'],
            defaults={'submission_text': 'Completed all 10 questions, attached below.'},
        )

        friendship, _ = Friendship.objects.get_or_create(
            from_user=students['s.aarav'], to_user=students['s.diya'],
            defaults={'status': Friendship.Status.ACCEPTED},
        )
        if friendship.status != Friendship.Status.ACCEPTED:
            friendship.status = Friendship.Status.ACCEPTED
            friendship.save()
        if not Message.objects.filter(sender=students['s.aarav'], recipient=students['s.diya']).exists():
            Message.objects.create(sender=students['s.aarav'], recipient=students['s.diya'], body='Hey, did you finish the math worksheet?')
            Message.objects.create(sender=students['s.diya'], recipient=students['s.aarav'], body='Yep, just submitted it!')

        self.stdout.write(self.style.SUCCESS('Demo data ready.'))
