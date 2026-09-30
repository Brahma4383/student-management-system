from django import forms

from academics.models import Section, Subject
from results.models import Exam

INPUT = {'class': 'input'}


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'school_class', 'date']
        widgets = {
            'name': forms.TextInput(attrs=INPUT),
            'school_class': forms.Select(attrs=INPUT),
            'date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
        }


class ResultEntrySessionForm(forms.Form):
    exam = forms.ModelChoiceField(queryset=Exam.objects.none(), widget=forms.Select(attrs=INPUT))
    subject = forms.ModelChoiceField(queryset=Subject.objects.none(), widget=forms.Select(attrs=INPUT))
    section = forms.ModelChoiceField(queryset=Section.objects.none(), widget=forms.Select(attrs=INPUT))

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher is not None:
            from academics.models import TeacherSubjectAssignment
            assigned = TeacherSubjectAssignment.objects.filter(teacher=teacher)
            subject_ids = assigned.values_list('subject_id', flat=True)
            section_ids = assigned.values_list('section_id', flat=True)
            self.fields['subject'].queryset = Subject.objects.filter(id__in=subject_ids)
            self.fields['section'].queryset = Section.objects.filter(id__in=section_ids)
            self.fields['exam'].queryset = Exam.objects.filter(
                school_class_id__in=Subject.objects.filter(id__in=subject_ids).values_list('school_class_id', flat=True))
