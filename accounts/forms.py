import re
from datetime import date

from django import forms
from django.contrib.auth import get_user_model

from common.validators.regex_patterns import DOCTOR_LICENSE_NO_REGEX, EMAIL_REGEX, PASSWORD_REGEX
from .models import DoctorProfile, PatientProfile

User = get_user_model()


class LoginForm(forms.Form):
    """
    로그인 폼. 의도적으로 이메일 형식/비밀번호 패턴 검증을 하지 않는다.

    로그인은 가입과 달리 "형식이 틀렸다"를 구체적으로 알려주면 보안상 좋지 않다 —
    이미 가입된 계정은 형식 검증을 통과한 값이므로, 형식 에러를 따로 보여주면
    공격자에게 "이 이메일이 가입된 계정인지" 추측할 단서를 줄 수 있다.
    그래서 클라이언트 검증은 필수 입력 여부만 확인하고, 실제 인증 성패는
    view에서 authenticate() 결과로만 판단해 "아이디 또는 비밀번호가 일치하지
    않습니다"라는 단일 메시지로 응답한다.
    """
    username = forms.CharField(
        label='이메일',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'email',
            'autofocus': True,
            'data-parsley-required': 'true',
            'data-parsley-required-message': '이메일을 입력해주세요.',
        }),
        error_messages={
            'required': '이메일을 입력해주세요.',
        },
    )
    password = forms.CharField(
        label='비밀번호',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password',
            'data-parsley-required': 'true',
            'data-parsley-required-message': '비밀번호를 입력해주세요.',
        }),
        error_messages={
            'required': '비밀번호를 입력해주세요.',
        },
    )


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
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autocomplete': 'email',
            'data-parsley-required': 'true',
            'data-parsley-pattern': EMAIL_REGEX,
            'data-parsley-required-message': '이메일을 입력해주세요.',
            'data-parsley-pattern-message': '올바른 이메일 형식이 아닙니다.',
            'data-parsley-type-message': '올바른 이메일 형식이 아닙니다.',
        }),
        error_messages={
            'required': '이메일을 입력해주세요.',
            'max_length': '이메일은 150자를 넘을 수 없습니다.',
        },
    )
    password1 = forms.CharField(
        label='비밀번호',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
            'data-parsley-required': 'true',
            'data-parsley-pattern': PASSWORD_REGEX,
            'data-parsley-required-message': '비밀번호를 입력해주세요.',
            'data-parsley-pattern-message': '영문, 숫자, 특수문자를 포함한 8~16자로 입력해주세요.',
        }),
        error_messages={
            'required': '비밀번호를 입력해주세요.',
        },
    )
    password2 = forms.CharField(
        label='비밀번호 확인',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password',
            'data-parsley-required': 'true',
            'data-parsley-equalto': '#id_password1',
            'data-parsley-required-message': '비밀번호를 다시 입력해주세요.',
            'data-parsley-equalto-message': '비밀번호가 일치하지 않습니다.',
        }),
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
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'data-parsley-required': 'true',
            'data-parsley-required-message': '생년월일을 입력해주세요.',
            'data-parsley-type-message': '올바른 날짜 형식이 아닙니다.',
        }),
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
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'data-parsley-required': 'true',
            'data-parsley-pattern': DOCTOR_LICENSE_NO_REGEX,
            'data-parsley-required-message': '면허번호를 입력해주세요.',
            'data-parsley-pattern-message': '면허번호는 숫자 4~6자리로 입력해주세요.',
        }),
        error_messages={
            'required': '면허번호를 입력해주세요.',
        },
    )

    def clean_license_no(self):
        license_no = self.cleaned_data['license_no']

        if not re.match(DOCTOR_LICENSE_NO_REGEX, license_no):
            raise forms.ValidationError('면허번호는 숫자 4~6자리로 입력해주세요.')
        
        if DoctorProfile.objects.filter(license_no=license_no).exists():
            raise forms.ValidationError('이미 등록된 면허번호입니다.')

        return license_no


class ProfileUpdateForm(forms.ModelForm):
    """
    topbar 프로필 드롭다운 → '내 정보 수정'에서 사용.
    이메일(아이디)은 로그인 식별자로 쓰이므로 수정 불가 — 읽기 전용으로만 표시.
    실제로는 더 이상 수정 가능한 User 필드가 없어 폼 자체가 비어있지만,
    템플릿에서 user.username을 읽기 전용 표시하는 데 view 컨텍스트로 user 객체를 넘긴다.
    """
    class Meta:
        model = User
        fields = []


class PatientProfileUpdateForm(forms.ModelForm):
    """
    생년월일/성별은 ML 모델의 핵심 피처(age, sex)이자 과거 PredictionResult와의
    정합성을 위해 가입 후 수정 불가 — 읽기 전용으로만 표시.
    실제로는 더 이상 수정 가능한 PatientProfile 필드가 없어 폼 자체가 비어있다.
    """
    class Meta:
        model = PatientProfile
        fields = []


class DoctorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['license_no']
        widgets = {
            'license_no': forms.TextInput(attrs={
                'class': 'form-control',
                'data-parsley-required': 'true',
                'data-parsley-pattern': DOCTOR_LICENSE_NO_REGEX,
                'data-parsley-required-message': '면허번호를 입력해주세요.',
                'data-parsley-pattern-message': '면허번호는 숫자 4~6자리로 입력해주세요.',
            }),
        }
        error_messages = {
            'license_no': {
                'required': '면허번호를 입력해주세요.',
                'unique': '이미 등록된 면허번호입니다.',
            },
        }

    def clean_license_no(self):
        license_no = self.cleaned_data['license_no']

        if not re.match(DOCTOR_LICENSE_NO_REGEX, license_no):
            raise forms.ValidationError('면허번호는 숫자 4~6자리로 입력해주세요.')

        return license_no