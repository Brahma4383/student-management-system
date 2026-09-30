from django import forms

from academics.models import TeacherSubjectAssignment
from assignments.models import Assignment, AssignmentSubmission

INPUT = {'class': 'input'}


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'subject', 'section', 'due_date', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs=INPUT),
            'description': forms.Textarea(attrs={'class': 'input', 'rows': 4}),
            'subject': forms.Select(attrs=INPUT),
            'section': forms.Select(attrs=INPUT),
            'due_date': forms.DateTimeInput(attrs={'class': 'input', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        self.teacher = teacher
        super().__init__(*args, **kwargs)
        if teacher is not None:
            assigned = TeacherSubjectAssignment.objects.filter(teacher=teacher).select_related('subject', 'section')
            subject_ids = assigned.values_list('subject_id', flat=True)
            section_ids = assigned.values_list('section_id', flat=True)
            self.fields['subject'].queryset = self.fields['subject'].queryset.filter(id__in=subject_ids)
            self.fields['section'].queryset = self.fields['section'].queryset.filter(id__in=section_ids)

    def clean(self):
        cleaned = super().clean()
        subject, section = cleaned.get('subject'), cleaned.get('section')
        if self.teacher is not None and subject and section:
            if not TeacherSubjectAssignment.teaches(self.teacher, subject, section):
                raise forms.ValidationError("You aren't assigned to teach this subject for this section.")
        return cleaned


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submission_text', 'submitted_file']
        widgets = {
            'submission_text': forms.Textarea(attrs={'class': 'input', 'rows': 4,
                                                       'placeholder': 'Optional notes about your submission'}),
        }


class GradeForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['grade', 'feedback']
        widgets = {
            'grade': forms.TextInput(attrs={'class': 'input', 'placeholder': 'e.g. A / 18 out of 20'}),
            'feedback': forms.Textarea(attrs={'class': 'input', 'rows': 3}),
        }

    def save(self, commit=True):
        submission = super().save(commit=False)
        submission.is_graded = True
        if commit:
            submission.save()
        return submission
