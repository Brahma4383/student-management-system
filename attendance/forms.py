from django import forms

from academics.models import Section, Subject

INPUT = {'class': 'input'}


class AttendanceSessionForm(forms.Form):
    """Picks which subject/section/date to mark or bulk-upload attendance for."""
    subject = forms.ModelChoiceField(queryset=Subject.objects.none(), widget=forms.Select(attrs=INPUT))
    section = forms.ModelChoiceField(queryset=Section.objects.none(), widget=forms.Select(attrs=INPUT))
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'input', 'type': 'date'}))

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher is not None:
            from academics.models import TeacherSubjectAssignment
            assigned = TeacherSubjectAssignment.objects.filter(teacher=teacher)
            self.fields['subject'].queryset = Subject.objects.filter(
                id__in=assigned.values_list('subject_id', flat=True))
            self.fields['section'].queryset = Section.objects.filter(
                id__in=assigned.values_list('section_id', flat=True))


class BulkAttendanceUploadForm(forms.Form):
    subject = forms.ModelChoiceField(queryset=Subject.objects.none(), widget=forms.Select(attrs=INPUT))
    section = forms.ModelChoiceField(queryset=Section.objects.none(), widget=forms.Select(attrs=INPUT))
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'input', 'type': 'date'}))
    csv_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'input', 'accept': '.csv'}),
        help_text='CSV with columns: admission_number,status (PRESENT/ABSENT/LATE/EXCUSED)',
    )

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher is not None:
            from academics.models import TeacherSubjectAssignment
            assigned = TeacherSubjectAssignment.objects.filter(teacher=teacher)
            self.fields['subject'].queryset = Subject.objects.filter(
                id__in=assigned.values_list('subject_id', flat=True))
            self.fields['section'].queryset = Section.objects.filter(
                id__in=assigned.values_list('section_id', flat=True))

    def clean_csv_file(self):
        f = self.cleaned_data['csv_file']
        if not f.name.lower().endswith('.csv'):
            raise forms.ValidationError('Please upload a .csv file.')
        return f
