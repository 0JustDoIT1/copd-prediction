from common.utils.age_group import calculate_age_group
from screening.models import PredictionResult
from .models import Benchmark
from .variable_info import get_variable_explanation, get_variable_label_info, SCORE_DESCRIPTION

# 화면에 표시할 6개 벤치마크 변수와, HealthRecord/Questionnaire 필드 매핑
# label: 화면 표시명, unit: 단위 표시
VARIABLE_DISPLAY_INFO = {
    'HE_BMI': {'label': '체질량지수(BMI)', 'unit': 'kg/m²'},
    'HE_sbp': {'label': '수축기 혈압', 'unit': 'mmHg'},
    'HE_dbp': {'label': '이완기 혈압', 'unit': 'mmHg'},
    'HE_glu': {'label': '공복혈당', 'unit': 'mg/dL'},
    'HE_chol': {'label': '총콜레스테롤', 'unit': 'mg/dL'},
    'smoking_amount': {'label': '흡연량', 'unit': '개비/일'},
}


def get_age_compare_context(patient):
    """
    환자 본인의 최신 검사 결과와 동연령대·동성별 평균을 비교하는
    화면에 필요한 전체 컨텍스트를 만들어 반환한다.

    Args:
        patient: PatientProfile 인스턴스

    Returns:
        dict | None: 표시할 데이터가 없으면 None (템플릿에서 empty-state 처리)
    """
    latest_result = (
        PredictionResult.objects
        .filter(questionnaire__patient=patient)
        .select_related('questionnaire', 'health_record')
        .order_by('-created_at')
        .first()
    )

    if latest_result is None:
        return None

    age_group = calculate_age_group(patient.birth_date)
    sex = patient.sex

    benchmark_qs = Benchmark.objects.filter(age_group=age_group, sex=sex)
    benchmark_map = {b.variable_name: b.mean_value for b in benchmark_qs}

    health_record = latest_result.health_record
    questionnaire = latest_result.questionnaire

    # 변수별 내 값 추출 (HealthRecord 5개 + Questionnaire 1개)
    # key는 Benchmark.variable_name 표기(HE_BMI 등)에 맞춤
    my_values = {
        'HE_BMI': health_record.bmi,
        'HE_sbp': health_record.sbp,
        'HE_dbp': health_record.dbp,
        'HE_glu': health_record.glucose,
        'HE_chol': health_record.cholesterol,
        'smoking_amount': questionnaire.smoking_amount,
    }

    variable_comparisons = []
    for var_name, info in VARIABLE_DISPLAY_INFO.items():
        my_value = my_values.get(var_name)
        benchmark_value = benchmark_map.get(var_name)

        if my_value is None or benchmark_value is None:
            continue  # 값이 없는 변수는 비교에서 제외

        diff = my_value - benchmark_value
        is_higher = diff > 0
        explanation = get_variable_explanation(var_name)

        variable_comparisons.append({
            'variable_name': var_name,
            'label': info['label'],
            'unit': info['unit'],
            'my_value': round(my_value, 1),
            'benchmark_value': round(benchmark_value, 1),
            'diff': round(diff, 1),
            'is_higher': is_higher,
            'description': explanation['description'] if explanation else '',
            'interpretation': (
                explanation['high_interpretation'] if is_higher
                else explanation['low_interpretation']
            ) if explanation else '',
            'copd_relation': explanation['copd_relation'] if explanation else '',
        })

    # 권고 점수 비교용 벤치마크 (변수명 'risk_probability'로 같은 테이블에 저장된다고 가정)
    score_benchmark_value = benchmark_map.get('risk_probability')

    score_comparison = None
    if score_benchmark_value is not None:
        my_score = round(latest_result.risk_probability * 100, 1)
        benchmark_score = round(score_benchmark_value * 100, 1)
        score_comparison = {
            'my_score': my_score,
            'benchmark_score': benchmark_score,
            'diff': round(my_score - benchmark_score, 1),
            'is_higher': my_score > benchmark_score,
        }

    return {
        'age_group': age_group,
        'sex': sex,
        'score_comparison': score_comparison,
        'variable_comparisons': variable_comparisons,
        'result_created_at': latest_result.created_at,
    }


def get_timeline_context(patient):
    """
    환자 본인의 전체 PredictionResult를 검사일(created_at) 순으로 정렬해
    추적기록 타임라인 화면에 필요한 컨텍스트를 만들어 반환한다.

    권고 점수 + 6개 건강 지표 각각의 시간별 추이를 선그래프로 보여주기 위해
    변수별로 [{date, value}, ...] 형태의 시리즈를 구성한다.

    Args:
        patient: PatientProfile 인스턴스

    Returns:
        dict | None: 검사 기록이 1건도 없으면 None (템플릿에서 empty-state 처리)
                      1건뿐이면 has_enough_data=False로 표시 (추이 비교 불가 안내용)
    """
    results = list(
        PredictionResult.objects
        .filter(questionnaire__patient=patient)
        .select_related('questionnaire', 'health_record')
        .order_by('created_at')
    )

    if not results:
        return None

    # 권고 점수 시리즈 (모든 검사에 항상 존재)
    # 같은 날짜에 여러 건 기록될 수 있어, 날짜만으로는 X축 라벨이 겹칠 수 있음
    # → 시:분까지 포함해 각 검사를 구분되게 표시
    score_series = [
        {
            'date': r.created_at.strftime('%Y-%m-%d %H:%M'),
            'value': round(r.risk_probability * 100, 1),
        }
        for r in results
    ]

    # 변수별 시리즈 — 검사마다 HealthRecord/Questionnaire 값이 None일 수 있어 건너뜀
    variable_series_map = {var_name: [] for var_name in VARIABLE_DISPLAY_INFO}

    for r in results:
        date_str = r.created_at.strftime('%Y-%m-%d %H:%M')
        health_record = r.health_record
        questionnaire = r.questionnaire

        values_for_result = {
            'HE_BMI': health_record.bmi,
            'HE_sbp': health_record.sbp,
            'HE_dbp': health_record.dbp,
            'HE_glu': health_record.glucose,
            'HE_chol': health_record.cholesterol,
            'smoking_amount': questionnaire.smoking_amount,
        }

        for var_name in VARIABLE_DISPLAY_INFO:
            value = values_for_result.get(var_name)
            if value is not None:
                variable_series_map[var_name].append({
                    'date': date_str,
                    'value': round(value, 1),
                })

    variable_timelines = []
    for var_name, info in VARIABLE_DISPLAY_INFO.items():
        series = variable_series_map[var_name]
        if not series:
            continue  # 한 번도 기록되지 않은 변수는 탭에서 제외
        explanation = get_variable_explanation(var_name)
        variable_timelines.append({
            'variable_name': var_name,
            'label': info['label'],
            'unit': info['unit'],
            'series': series,
            'description': explanation['description'] if explanation else '',
        })

    latest_result = results[-1]
    first_result = results[0]

    return {
        'has_enough_data': len(results) >= 2,  # 1건뿐이면 추이 비교 의미 없음
        'result_count': len(results),
        'score_series': score_series,
        'score_description': SCORE_DESCRIPTION,
        'variable_timelines': variable_timelines,
        'first_date': first_result.created_at,
        'latest_date': latest_result.created_at,
    }


def get_risk_factors_context(patient):
    """
    환자 본인의 최근 검사 결과(PredictionResult.top_factors)를 기반으로
    위험요인 시각화 화면에 필요한 컨텍스트를 만들어 반환한다.

    top_factors는 screening 앱이 모델 추론 시점에 이미 계산해 저장해둔 값을
    그대로 사용한다 (별도로 계수를 다시 계산하지 않음 — 결과 페이지와 수치가
    항상 일치해야 하기 때문).

    Args:
        patient: PatientProfile 인스턴스

    Returns:
        dict | None: PredictionResult가 없으면 None (템플릿에서 empty-state 처리)
    """
    latest_result = (
        PredictionResult.objects
        .filter(questionnaire__patient=patient)
        .order_by('-created_at')
        .first()
    )

    if latest_result is None:
        return None

    factors = []
    raw_items = latest_result.top_factors or []

    # 막대 길이 계산 기준 — 절댓값이 가장 큰 contribution을 100%로 두고 나머지를 비율로 환산
    max_abs_contribution = max(
        (abs(item.get('contribution', 0)) for item in raw_items if item.get('contribution') is not None),
        default=0,
    )

    for item in raw_items:
        var_name = item.get('feature')
        contribution = item.get('contribution')

        if var_name is None or contribution is None:
            continue  # 형식이 어긋난 항목은 건너뜀 (방어적 처리)

        label_info = get_variable_label_info(var_name)
        explanation = get_variable_explanation(var_name)
        increases_risk = contribution > 0

        bar_percent = round(abs(contribution) / max_abs_contribution * 100, 1) if max_abs_contribution > 0 else 0

        factors.append({
            'variable_name': var_name,
            'label': label_info['label'],
            'contribution': round(contribution, 3),
            'bar_percent': bar_percent,
            'increases_risk': increases_risk,
            'description': explanation['description'] if explanation else '',
            'interpretation': (
                explanation.get('increases_risk') if increases_risk
                else explanation.get('decreases_risk')
            ) if explanation else '',
            'copd_relation': explanation['copd_relation'] if explanation else '',
        })

    return {
        'score': round(latest_result.risk_probability * 100, 1),
        'factors': factors,
        'result_created_at': latest_result.created_at,
    }