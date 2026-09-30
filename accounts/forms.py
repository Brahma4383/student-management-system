from django import forms
from django.contrib.auth.forms import AuthenticationForm

from accounts.models import StudentProfile, TeacherProfile, User
from academics.models import Section


TEXT_WIDGET = forms.TextInput(attrs={'class': 'input'})


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input'}))


class TeacherCreateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input'}),
        help_text='Stored as plain text - visible to admins as-is.',
    )
    employee_id = forms.CharField(widget=TEXT_WIDGET)
    department = forms.CharField(required=False, widget=TEXT_WIDGET)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'password']
        widgets = {
            'username': TEXT_WIDGET,
            'first_name': TEXT_WIDGET,
            'last_name': TEXT_WIDGET,
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'phone_number': TEXT_WIDGET,
        }

    def clean_employee_id(self):
        emp_id = self.cleaned_data['employee_id']
        if TeacherProfile.objects.filter(employee_id=emp_id).exists():
            raise forms.ValidationError('A teacher with this employee ID already exists.')
        return emp_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.TEACHER
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            TeacherProfile.objects.create(
                user=user,
                employee_id=self.cleaned_data['employee_id'],
                department=self.cleaned_data['department'],
            )
        return user


class TeacherEditForm(forms.ModelForm):
    department = forms.CharField(required=False, widget=TEXT_WIDGET)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'is_active']
        widgets = {
            'first_name': TEXT_WIDGET,
            'last_name': TEXT_WIDGET,
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'phone_number': TEXT_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'teacher_profile'):
            self.fields['department'].initial = self.instance.teacher_profile.department

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.teacher_profile
            profile.department = self.cleaned_data['department']
            profile.save()
        return user


class StudentCreateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input'}),
        help_text='Stored as plain text - visible to admins as-is.',
    )
    admission_number = forms.CharField(widget=TEXT_WIDGET)
    section = forms.ModelChoiceField(queryset=Section.objects.select_related('school_class').all(),
                                      required=False, widget=forms.Select(attrs={'class': 'input'}))
    date_of_birth = forms.DateField(required=False,
                                     widget=forms.DateInput(attrs={'class': 'input', 'type': 'date'}))
    guardian_name = forms.CharField(required=False, widget=TEXT_WIDGET)
    guardian_phone = forms.CharField(required=False, widget=TEXT_WIDGET)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'password']
        widgets = {
            'username': TEXT_WIDGET,
            'first_name': TEXT_WIDGET,
            'last_name': TEXT_WIDGET,
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'phone_number': TEXT_WIDGET,
        }

    def clean_admission_number(self):
        adm = self.cleaned_data['admission_number']
        if StudentProfile.objects.filter(admission_number=adm).exists():
            raise forms.ValidationError('A student with this admission number already exists.')
        return adm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                admission_number=self.cleaned_data['admission_number'],
                section=self.cleaned_data['section'],
                date_of_birth=self.cleaned_data['date_of_birth'],
                guardian_name=self.cleaned_data['guardian_name'],
                guardian_phone=self.cleaned_data['guardian_phone'],
            )
        return user


class StudentEditForm(forms.ModelForm):
    section = forms.ModelChoiceField(queryset=Section.objects.select_related('school_class').all(),
                                      required=False, widget=forms.Select(attrs={'class': 'input'}))
    date_of_birth = forms.DateField(required=False,
                                     widget=forms.DateInput(attrs={'class': 'input', 'type': 'date'}))
    guardian_name = forms.CharField(required=False, widget=TEXT_WIDGET)
    guardian_phone = forms.CharField(required=False, widget=TEXT_WIDGET)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'is_active']
        widgets = {
            'first_name': TEXT_WIDGET,
            'last_name': TEXT_WIDGET,
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'phone_number': TEXT_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'student_profile'):
            profile = self.instance.student_profile
            self.fields['section'].initial = profile.section
            self.fields['date_of_birth'].initial = profile.date_of_birth
            self.fields['guardian_name'].initial = profile.guardian_name
            self.fields['guardian_phone'].initial = profile.guardian_phone

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.student_profile
            profile.section = self.cleaned_data['section']
            profile.date_of_birth = self.cleaned_data['date_of_birth']
            profile.guardian_name = self.cleaned_data['guardian_name']
            profile.guardian_phone = self.cleaned_data['guardian_phone']
            profile.save()
        return user


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input'}),
        help_text='Stored as plain text.',
        min_length=6,
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_photo']
        widgets = {
            'first_name': TEXT_WIDGET,
            'last_name': TEXT_WIDGET,
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'phone_number': TEXT_WIDGET,
        }


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input'}), min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input'}), min_length=6)

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        pwd = self.cleaned_data['current_password']
        if not self.user.check_password(pwd):
            raise forms.ValidationError('Current password is incorrect.')
        return pwd

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('new_password') and cleaned.get('confirm_password'):
            if cleaned['new_password'] != cleaned['confirm_password']:
                raise forms.ValidationError('New passwords do not match.')
        return cleaned
