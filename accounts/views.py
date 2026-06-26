from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import (
    DoctorProfileUpdateForm,
    DoctorSignupForm,
    PatientProfileUpdateForm,
    PatientSignupForm,
    ProfileUpdateForm,
)
from .models import DoctorProfile, PatientProfile

User = get_user_model()


def _redirect_to_dashboard(request):
    """로그인 상태에 따른 분기 리다이렉트. role별 대시보드로 보낸다."""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if request.user.role == 'doctor':
        return redirect('screening:doctor_dashboard')
    return redirect('accounts:patient_dashboard')


def root_view(request):
    """
    '/' 경로 — 화면을 직접 그리지 않고 redirect만 담당.
    비로그인: 로그인 페이지로. 로그인: role별 대시보드로.
    """
    return _redirect_to_dashboard(request)


def login_view(request):
    """공통 로그인 페이지. 역할 구분 없이 하나의 폼으로 처리하고, 로그인 후 role에 따라 분기."""
    if request.user.is_authenticated:
        return _redirect_to_dashboard(request)

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return _redirect_to_dashboard(request)

        # 보안상 아이디/비밀번호 중 어느 쪽이 틀렸는지 구분하지 않는다.
        error = '아이디 또는 비밀번호가 일치하지 않습니다.'

    return render(request, 'accounts/login.html', {'error': error})


def signup_role_select_view(request):
    """회원가입 1단계: 환자/의사 역할 선택 페이지."""
    if request.user.is_authenticated:
        return _redirect_to_dashboard(request)
    return render(request, 'accounts/signup_role_select.html')


def signup_patient_view(request):
    """환자 전용 가입 폼."""
    if request.user.is_authenticated:
        return _redirect_to_dashboard(request)

    if request.method == 'POST':
        form = PatientSignupForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    role='patient',
                )
                PatientProfile.objects.create(
                    user=user,
                    birth_date=form.cleaned_data['birth_date'],
                    sex=form.cleaned_data['sex'],
                )
            login(request, user)
            return redirect('accounts:patient_dashboard')
    else:
        form = PatientSignupForm()

    return render(request, 'accounts/signup_patient.html', {'form': form})


def signup_doctor_view(request):
    """의사 전용 가입 폼."""
    if request.user.is_authenticated:
        return _redirect_to_dashboard(request)

    if request.method == 'POST':
        form = DoctorSignupForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    role='doctor',
                )
                DoctorProfile.objects.create(
                    user=user,
                    license_no=form.cleaned_data.get('license_no', ''),
                )
            login(request, user)
            return redirect('screening:doctor_dashboard')
    else:
        form = DoctorSignupForm()

    return render(request, 'accounts/signup_doctor.html', {'form': form})


@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def patient_dashboard_view(request):
    return render(request, 'accounts/patient_dashboard.html', {
        'active_menu': 'home',
    })


@login_required
def profile_view(request):
    """topbar 프로필 드롭다운 → 내 정보 수정. User 기본정보 + role별 프로필 정보를 같이 처리."""
    user = request.user

    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, instance=user)

        if user.role == 'patient':
            profile = user.patientprofile
            profile_form = PatientProfileUpdateForm(request.POST, instance=profile)
        else:
            profile = user.doctorprofile
            profile_form = DoctorProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            messages.success(request, '내 정보가 수정되었습니다.')
            return redirect('accounts:profile')
    else:
        user_form = ProfileUpdateForm(instance=user)
        if user.role == 'patient':
            profile_form = PatientProfileUpdateForm(instance=user.patientprofile)
        else:
            profile_form = DoctorProfileUpdateForm(instance=user.doctorprofile)

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })