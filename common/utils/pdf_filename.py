from datetime import date


def build_pdf_filename(title, patient_name):
    """
    PDF 다운로드 파일명을 '날짜_이름_제목.pdf' 형식으로 만든다.
    예: '260628_홍길동_동연령대비교리포트.pdf'

    날짜는 YYMMDD 형식(오늘 날짜, 생성 시점 기준)을 사용한다.

    Args:
        title: 제목 부분 (공백 없이, 예: '동연령대비교리포트')
        patient_name: 환자 이름 (accounts.models.User.name)

    Returns:
        str: 완성된 파일명 (확장자 .pdf 포함)
    """
    date_str = date.today().strftime('%y%m%d')
    safe_name = patient_name.strip() if patient_name else '환자'
    safe_title = title.strip()
    return f"{date_str}_{safe_name}_{safe_title}.pdf"