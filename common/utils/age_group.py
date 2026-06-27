from datetime import date


def calculate_age(birth_date):
    """생년월일로부터 만 나이를 계산한다."""
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def calculate_age_group(birth_date):
    """
    만 나이를 fixture 기준 10세 단위 연령대 문자열로 변환한다.
    예: 65세 -> '60s', 23세 -> '20s'
    Benchmark.age_group 필드와 동일한 포맷을 반환한다.
    """
    age = calculate_age(birth_date)
    decade = (age // 10) * 10
    decade = max(20, min(decade, 80))  # fixture 범위: 20s~80s
    return f"{decade}s"