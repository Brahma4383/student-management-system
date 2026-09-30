# Student Management System

Django-based school/college management system with role-based access for
Admin, Teacher and Student.

## ⚠️ Security note

**Passwords in this project are stored in plain text, not hashed**, per project
requirements. This is implemented in exactly one place:
[accounts/models.py](accounts/models.py) (`User.set_password` / `User.check_password`).
Everywhere else, Django's normal auth flow (login, sessions, admin) is untouched.

Do not reuse this pattern for a system that will hold real people's data. If you
change your mind later, deleting that override (so it falls back to
`AbstractUser`'s default hashing) is the one-line fix — you'll need to reset
existing users' passwords afterwards since old plain-text values won't match a
hash.

## Features

- **Admin** — manage teacher/student accounts (create, edit, deactivate, reset
  password), classes/sections/subjects, teacher-subject-section assignments,
  and view all attendance/results across the school. Django admin (`/admin/`)
  is also available for power-user/debug access.
- **Teacher** — post assignments to a section, grade submissions, mark
  attendance (manually or via bulk CSV upload, with a downloadable
  pre-filled roster template), and enter exam results.
- **Student** — view/submit assignments, view attendance percentage per
  subject, view results with an exam-over-exam improvement chart, and chat
  with friends (search students, send/accept friend requests, message with
  lightweight auto-refresh).

## Project layout

```
accounts/       custom User model (role: ADMIN/TEACHER/STUDENT), profiles, auth, admin-side user management
academics/      SchoolClass, Section, Subject, TeacherSubjectAssignment (admin-managed)
assignments/    Assignment + AssignmentSubmission, teacher & student views
attendance/     AttendanceRecord, marking grid + bulk CSV upload
results/        Exam + Result, marks entry, student improvement view
chat/           Friendship + Message, student-to-student chat
teacher/        teacher dashboard (aggregates the apps above)
student/        student dashboard (aggregates the apps above)
templates/      shared base.html, partials, error pages
static/         shared CSS/JS
library/        pre-existing empty app scaffold, not wired up (out of scope)
```

## Setup

A virtual environment already exists at `myvenv/`. From `student_management/`:

```
myvenv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data   # optional: creates sample classes/users/data
python manage.py runserver
```

Then open http://127.0.0.1:8000/.

## Demo accounts

Created by `seed_demo_data` (safe to re-run):

| Role    | Username   | Password  |
|---------|------------|-----------|
| Admin   | `admin`    | admin123  |
| Teacher | `t.sharma` | teach123  |
| Teacher | `t.verma`  | teach123  |
| Teacher | `t.gupta`  | teach123  |
| Student | `s.aarav`  | pass123   |
| Student | `s.diya`   | pass123   |
| Student | `s.ishaan` | pass123   |
| Student | `s.kavya`  | pass123   |
| Student | `s.vihaan` | pass123   |
| Student | `s.myra`   | pass123   |

`s.aarav` and `s.diya` are already friends with a couple of chat messages, so
you can see the chat feature immediately.

To create your own admin instead: `python manage.py createsuperuser`.
