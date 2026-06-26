from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve


def _resolve_url_name(path):
    """경로를 'namespace:name' 형태의 URL 이름으로 변환. 실패하면 None."""
    try:
        match = resolve(path)
    except Exception:
        return None
    return f'{match.namespace}:{match.url_name}' if match.namespace else match.url_name


class LoginRequiredMiddleware:
    """
    프로젝트 전역 접근 제어 미들웨어. 두 방향을 모두 처리한다.

    1) 미로그인 사용자가 보호된 페이지(기본값: 전부)에 접근 → 로그인 페이지로 보냄.
       settings.LOGIN_EXEMPT_URL_NAMES 목록에 있는 URL 이름만 예외로 통과시킨다.

    2) 로그인한 사용자가 로그인/가입 같은 "비로그인 전용" 페이지에 접근
       → 각자의 대시보드로 돌려보낸다.
       settings.GUEST_ONLY_URL_NAMES 목록(로그인/가입 화면들)을 검사 대상으로 삼는다.

    각 뷰마다 @login_required나 "if request.user.is_authenticated: redirect(...)"를
    일일이 작성하는 방식은 팀원이 새 뷰를 만들 때 빠뜨리기 쉽다. 이 미들웨어가
    기본 동작을 한 곳에서 관리하고, 개별 뷰의 동일한 체크는 이중 방어선으로 남겨도 무방하다.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # 정적 파일, Django admin은 자체 체계를 쓰므로 항상 예외.
        if path.startswith(settings.STATIC_URL) or path.startswith('/admin/'):
            return self.get_response(request)

        url_name = _resolve_url_name(path)

        if request.user.is_authenticated:
            # 방향 2: 로그인한 사용자가 로그인/가입 페이지에 접근하면 대시보드로.
            guest_only_names = getattr(settings, 'GUEST_ONLY_URL_NAMES', [])
            if url_name in guest_only_names:
                if request.user.role == 'doctor':
                    return redirect('accounts:doctor_dashboard')
                return redirect('accounts:patient_dashboard')
            return self.get_response(request)

        # 방향 1: 미로그인 사용자가 보호된 페이지에 접근하면 로그인 페이지로.
        exempt_names = getattr(settings, 'LOGIN_EXEMPT_URL_NAMES', [])
        if url_name in exempt_names:
            return self.get_response(request)

        login_url = getattr(settings, 'LOGIN_URL', 'accounts:login')
        return redirect(login_url)