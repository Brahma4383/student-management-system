from django import forms

from academics.models import SchoolClass, Section, Subject, TeacherSubjectAssignment
from accounts.models import User

INPUT = {'class': 'input'}


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs=INPUT)}


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['school_class', 'name', 'class_teacher']
        widgets = {
            'school_class': forms.Select(attrs=INPUT),
            'name': forms.TextInput(attrs=INPUT),
            'class_teacher': forms.Select(attrs=INPUT),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['class_teacher'].queryset = User.objects.filter(role=User.Role.TEACHER)
        self.fields['class_teacher'].required = False


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'school_class']
        widgets = {
            'name': forms.TextInput(attrs=INPUT),
            'code': forms.TextInput(attrs=INPUT),
            'school_class': forms.Select(attrs=INPUT),
        }


class TeacherSubjectAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherSubjectAssignment
        fields = ['teacher', 'subject', 'section']
        widgets = {
            'teacher': forms.Select(attrs=INPUT),
            'subject': forms.Select(attrs=INPUT),
            'section': forms.Select(attrs=INPUT),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(role=User.Role.TEACHER)
