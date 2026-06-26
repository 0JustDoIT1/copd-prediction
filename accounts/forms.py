import re
from datetime import date

from django import forms
from django.contrib.auth import get_user_model

from common.validators.regex_patterns import DOCTOR_LICENSE_NO_REGEX, EMAIL_REGEX, PASSWORD_REGEX
from .models import DoctorProfile, PatientProfile

User = get_user_model()


class BaseSignupForm(forms.Form):
    """
    환자/의사 가입 폼이 공통으로 갖는 필드(이메일, 비밀번호).
    역할별 폼(PatientSignupForm/DoctorSignupForm)이 이를 상속해서 추가 필드를 덧붙인다.

    아이디는 이메일 형식을 그대로 사용한다 (User.username 필드에 이메일 문자열을 저장).
    """
    email = forms.CharField(
        label='이메일',
        max_length=150,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}),
        error_messages={
            'required': '이메일을 입력해주세요.',
            'max_length': '이메일은 150자를 넘을 수 없습니다.',
        },
    )
    password1 = forms.CharField(
        label='비밀번호',
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        error_messages={
            'required': '비밀번호를 입력해주세요.',
        },
    )
    password2 = forms.CharField(
        label='비밀번호 확인',
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        error_messages={
            'required': '비밀번호를 다시 입력해주세요.',
        },
    )

    def clean_email(self):
        email = self.cleaned_data['email']

        if not re.match(EMAIL_REGEX, email):
            raise forms.ValidationError('올바른 이메일 형식이 아닙니다.')

        if User.objects.filter(username=email).exists():
            raise forms.ValidationError('이미 가입된 이메일입니다.')

        return email

    def clean_password1(self):
        password1 = self.cleaned_data['password1']

        if not re.match(PASSWORD_REGEX, password1):
            raise forms.ValidationError(
                '비밀번호는 영문, 숫자, 특수문자를 포함한 8~16자로 입력해주세요.'
            )

        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', '비밀번호가 일치하지 않습니다.')

        return cleaned_data


class PatientSignupForm(BaseSignupForm):
    """환자 전용 가입 폼: 공통 필드 + 생년월일/성별."""
    birth_date = forms.DateField(
        label='생년월일',
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        error_messages={
            'required': '생년월일을 입력해주세요.',
            'invalid': '올바른 날짜 형식이 아닙니다.',
        },
    )
    sex = forms.ChoiceField(
        label='성별',
        required=True,
        choices=PatientProfile._meta.get_field('sex').choices,
        widget=forms.RadioSelect,
        error_messages={
            'required': '성별을 선택해주세요.',
        },
    )

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        if birth_date > date.today():
            raise forms.ValidationError('생년월일은 미래 날짜일 수 없습니다.')
        return birth_date


class DoctorSignupForm(BaseSignupForm):
    """의사 전용 가입 폼: 공통 필드 + 면허번호(필수)."""
    license_no = forms.CharField(
        label='면허번호',
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            'required': '면허번호를 입력해주세요.',
        },
    )

    def clean_license_no(self):
        license_no = self.cleaned_data['license_no']

        if not re.match(DOCTOR_LICENSE_NO_REGEX, license_no):
            raise forms.ValidationError('면허번호는 숫자 4~6자리로 입력해주세요.')

        return license_no


class ProfileUpdateForm(forms.ModelForm):
    """topbar 프로필 드롭다운 → '내 정보 수정'에서 사용. User 모델의 기본 정보만 다룬다."""

    class Meta:
        model = User
        fields = ['username']
        labels = {
            'username': '이메일',
        }
        widgets = {
            'username': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'username': {
                'required': '이메일을 입력해주세요.',
            },
        }

    def clean_username(self):
        email = self.cleaned_data['username']

        if not re.match(EMAIL_REGEX, email):
            raise forms.ValidationError('올바른 이메일 형식이 아닙니다.')

        qs = User.objects.filter(username=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('이미 가입된 이메일입니다.')

        return email


class PatientProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['birth_date', 'sex']
        widgets = {
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sex': forms.RadioSelect,
        }
        error_messages = {
            'birth_date': {'required': '생년월일을 입력해주세요.'},
            'sex': {'required': '성별을 선택해주세요.'},
        }

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        if birth_date > date.today():
            raise forms.ValidationError('생년월일은 미래 날짜일 수 없습니다.')
        return birth_date


class DoctorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['license_no']
        widgets = {
            'license_no': forms.TextInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'license_no': {
                'required': '면허번호를 입력해주세요.',
            },
        }

    def clean_license_no(self):
        license_no = self.cleaned_data['license_no']

        if not re.match(DOCTOR_LICENSE_NO_REGEX, license_no):
            raise forms.ValidationError('면허번호는 숫자 4~6자리로 입력해주세요.')

        return license_no