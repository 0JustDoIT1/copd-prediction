from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from daily_care.utils import has_checked_in_today

from .forms import (
    DoctorProfileUpdateForm,
    DoctorSignupForm,
    LoginForm,
    PatientProfileUpdateForm,
    PatientSignupForm,
    ProfileUpdateForm,
)
from .models import DoctorProfile, PatientProfile

User = get_user_model()


def _redirect_to_dashboard(request):
    """
    로그인 상태에 따른 분기 리다이렉트. role별 대시보드로 보낸다.

    미들웨어(common.middleware.LoginRequiredMiddleware)가 일반적인 접근 제어를
    전담하지만, 이 함수는 "막 로그인에 성공한 바로 그 순간"처럼 미들웨어가
    개입하기 전에 이번 요청 안에서 바로 분기해야 하는 경우에 쓰인다.
    root_view도 동일한 이유로 이 함수를 그대로 사용한다.
    """
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if request.user.role == 'doctor':
        return redirect('accounts:doctor_dashboard')
    return redirect('accounts:patient_dashboard')


def root_view(request):
    """
    '/' 경로 — 화면을 직접 그리지 않고 redirect만 담당.
    비로그인: 로그인 페이지로. 로그인: role별 대시보드로.
    """
    return _redirect_to_dashboard(request)


def login_view(request):
    """
    공통 로그인 페이지. 역할 구분 없이 하나의 폼으로 처리하고, 로그인 후 role에 따라 분기.

    로그인한 사용자가 이 페이지에 접근하는 경우는 미들웨어가 이미 대시보드로
    돌려보내므로, 이 함수 내부에서는 별도로 체크하지 않는다.
    """
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return _redirect_to_dashboard(request)

            # 보안상 아이디/비밀번호 중 어느 쪽이 틀렸는지 구분하지 않는다.
            error = '아이디 또는 비밀번호가 일치하지 않습니다.'
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'error': error,
    })


def signup_role_select_view(request):
    """회원가입 1단계: 환자/의사 역할 선택 페이지."""
    return render(request, 'accounts/signup_role_select.html')


def signup_patient_view(request):
    """환자 전용 가입 폼."""
    if request.method == 'POST':
        form = PatientSignupForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    name=form.cleaned_data['name'],
                    role='patient',
                )
                PatientProfile.objects.create(
                    user=user,
                    birth_date=form.cleaned_data['birth_date'],
                    sex=form.cleaned_data['sex'],
                )
            messages.success(request, '회원가입이 완료되었습니다. 로그인해주세요.')
            return redirect('accounts:login')
    else:
        form = PatientSignupForm()

    return render(request, 'accounts/signup_patient.html', {'form': form})


def signup_doctor_view(request):
    """의사 전용 가입 폼."""
    if request.method == 'POST':
        form = DoctorSignupForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    name=form.cleaned_data['name'],
                    role='doctor',
                )
                DoctorProfile.objects.create(
                    user=user,
                    license_no=form.cleaned_data.get('license_no', ''),
                )
            messages.success(request, '회원가입이 완료되었습니다. 로그인해주세요.')
            return redirect('accounts:login')
    else:
        form = DoctorSignupForm()

    return render(request, 'accounts/signup_doctor.html', {'form': form})


@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def patient_dashboard_view(request):
    """
    환자 홈 대시보드.

    구성: 히어로 섹션 / 카드 4개(검진입력·예약·COPD상식·호흡운동) /
    What-if 시뮬레이션(메인 콘텐츠) / FAQ 아코디언

    카드 4개는 모두 고정 안내 문구이며, COPD 상식·호흡 운동 가이드의 실제
    콘텐츠는 각 카드를 클릭해 들어가는 content 앱의 목록 페이지에서 확인한다.
    FAQ만 content.models.FAQ에서 상위 4개를 가져와 미리보기로 보여준다.

    체크인 토스트는 daily_care.utils.has_checked_in_today()로 노출 여부를
    결정한다 — 오늘 daily_log를 실제로 기록했는지 여부로 판단하므로, 세션이나
    로그인 여부와 무관하게 정확하게 동작한다.

    What-if 시뮬레이션은 환자의 가장 최근 PredictionResult(검사 기록)를 기준으로
    현재 흡연 상태/흡연량을 가져와 슬라이더 초기값으로 채운다. 검사 기록이 한
    건도 없으면 시뮬레이션 자체를 빈 상태(has_health_record=False)로 보여준다.

    whatif_compute_url: screening 팀이 /predict/what-if/ 를 만들면 그 경로로 교체.
    입력: {smoking_status, smoking_amount, weight_delta}, 출력: {risk_probability}
    (아직 미구현이라 이 부분은 TODO로 남겨둠)
    """
    from content.models import FAQ
    from screening.models import PredictionResult

    faqs = FAQ.objects.all()[:4]

    patient = request.user.patientprofile

    latest_result = (
        PredictionResult.objects
        .filter(questionnaire__patient=patient)
        .select_related('questionnaire', 'health_record')
        .order_by('-created_at')
        .first()
    )

    has_health_record = latest_result is not None

    # 검사 기록이 있으면 가장 최근 값으로 슬라이더 초기값을 채우고,
    # 없으면 화면 자체가 empty-state로 빠지므로 기본값(0, 0)을 넣어도 사용되지 않는다.
    if has_health_record:
        whatif_current_smoking = latest_result.questionnaire.smoking_status
        whatif_current_amount = latest_result.questionnaire.smoking_amount
    else:
        whatif_current_smoking = 0
        whatif_current_amount = 0

    show_checkin_toast = not has_checked_in_today(request.user)

    context = {
        'active_menu': 'home',

        'faqs': faqs,

        'has_health_record': has_health_record,
        'whatif_current_smoking': whatif_current_smoking,
        'whatif_current_amount': whatif_current_amount,

        'show_checkin_toast': show_checkin_toast,
    }
    return render(request, 'accounts/patient_dashboard.html', context)


def doctor_dashboard_view(request):
    return redirect('screening:doctor_dashboard')


def profile_view(request):
    user = request.user

    if user.role == 'patient':
        profile = user.patientprofile

        from screening.models import PredictionResult

        patient_predictions = PredictionResult.objects.filter(
            questionnaire__patient=profile
        )
        prediction_count = patient_predictions.count()
        latest_result = patient_predictions.order_by('-created_at').first()
        latest_result_date = latest_result.created_at if latest_result else None

        context = {
            'user_obj': user,
            'profile': profile,
            'prediction_count': prediction_count,
            'latest_result_date': latest_result_date,
        }
    else:
        profile_form = DoctorProfileUpdateForm(
            request.POST or None, instance=user.doctorprofile
        )
        if request.method == 'POST' and profile_form.is_valid():
            profile_form.save()
            messages.success(request, '면허번호가 변경되었습니다.')
            return redirect('accounts:profile')

        context = {
            'user_obj': user,
            'profile_form': profile_form,
        }

    return render(request, 'accounts/profile.html', context)