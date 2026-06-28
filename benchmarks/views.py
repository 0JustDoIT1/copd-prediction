import json

from django.shortcuts import render

from .services import get_age_compare_context, get_timeline_context, get_risk_factors_context


def age_compare_view(request):
    """
    환자 본인의 최신 검사 결과를 동연령대·동성별 평균과 비교하는 화면.
    PredictionResult가 없는 환자는 empty-state를 표시한다.
    """
    patient = request.user.patientprofile

    context = get_age_compare_context(patient)

    return render(request, 'benchmarks/age_compare.html', {
        'has_data': context is not None,
        'data': context,
        'active_group': 'benchmarks',
        'active_menu': 'age_compare',
    })


def timeline_view(request):
    """
    환자 본인의 전체 검사 기록을 시간순으로 보여주는 추적기록 타임라인 화면.
    권고 점수 + 건강 지표 6개의 추이를 탭으로 전환하며 선그래프로 확인한다.
    PredictionResult가 없으면 empty-state, 1건뿐이면 "아직 비교할 이전 기록 없음" 안내.
    """
    patient = request.user.patientprofile

    context = get_timeline_context(patient)

    if context is not None:
        # 템플릿에서 안전하게 JS로 박아넣을 수 있도록 미리 JSON 문자열로 직렬화
        context['score_series_json'] = json.dumps(context['score_series'])
        for item in context['variable_timelines']:
            item['series_json'] = json.dumps(item['series'])

    return render(request, 'benchmarks/timeline.html', {
        'has_data': context is not None,
        'data': context,
        'active_group': 'benchmarks',
        'active_menu': 'tracking',
    })


def risk_factors_view(request):
    """
    환자 본인의 최근 검사에서 권고 점수에 영향을 준 주요 요인(top_factors)을
    시각화하는 화면. screening 앱이 저장한 값을 그대로 사용한다.
    PredictionResult가 없으면 empty-state를 표시한다.
    """
    patient = request.user.patientprofile

    context = get_risk_factors_context(patient)

    return render(request, 'benchmarks/risk_factors.html', {
        'has_data': context is not None,
        'data': context,
        'active_group': 'benchmarks',
        'active_menu': 'risk_factors',
    })