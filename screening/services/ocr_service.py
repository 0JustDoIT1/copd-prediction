"""
Google Vision OCR 처리
"""

import re
from google.cloud import vision


def extract_number(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None

    return None


def parse_health_data(full_text):
    """
    OCR 전체 텍스트에서 건강검진 수치를 추출합니다.
    1차: 항목명 바로 뒤 숫자 추출
    2차: 검진결과지 표 형태 보완 추출
    """

    data = {
        "height": extract_number(full_text, [
            r"키\s*[:：]?\s*(\d+\.?\d*)",
            r"신장\s*[:：]?\s*(\d+\.?\d*)",
            r"Height\s*[:：]?\s*(\d+\.?\d*)",
        ]),
        "weight": extract_number(full_text, [
            r"몸무게\s*[:：]?\s*(\d+\.?\d*)",
            r"체중\s*[:：]?\s*(\d+\.?\d*)",
            r"Weight\s*[:：]?\s*(\d+\.?\d*)",
        ]),
        "sbp": extract_number(full_text, [
            r"수축기\s*혈압\s*[:：]?\s*(\d+\.?\d*)",
            r"SBP\s*[:：]?\s*(\d+\.?\d*)",
        ]),
        "dbp": extract_number(full_text, [
            r"이완기\s*혈압\s*[:：]?\s*(\d+\.?\d*)",
            r"DBP\s*[:：]?\s*(\d+\.?\d*)",
        ]),
        "glucose": extract_number(full_text, [
            r"공복혈당\s*[:：]?\s*(\d+\.?\d*)",
            r"혈당\s*[:：]?\s*(\d+\.?\d*)",
            r"Glucose\s*[:：]?\s*(\d+\.?\d*)",
        ]),
        "hba1c": extract_number(full_text, [
            r"HbA1c\s*[:：]?\s*(\d+\.?\d*)",
            r"당화혈색소\s*[:：]?\s*(\d+\.?\d*)",
        ]),
        "cholesterol": extract_number(full_text, [
            r"총\s*콜레스테롤\s*[:：]?\s*(\d+\.?\d*)",
            r"총콜레스테롤\s*[:：]?\s*(\d+\.?\d*)",
            r"Total\s*Cholesterol\s*[:：]?\s*(\d+\.?\d*)",
        ]),
        "hdl": extract_number(full_text, [
            r"HDL\s*콜레스테롤\s*[:：]?\s*(\d+\.?\d*)",
            r"HDL\s*[:：]?\s*(\d+\.?\d*)",
        ]),
        "triglyceride": extract_number(full_text, [
            r"중성지방\s*[:：]?\s*(\d+\.?\d*)",
            r"Triglyceride\s*[:：]?\s*(\d+\.?\d*)",
            r"TG\s*[:：]?\s*(\d+\.?\d*)",
        ]),
        "ast": extract_number(full_text, [
            r"AST\s*[:：]?\s*(\d+\.?\d*)",
        ]),
        "alt": extract_number(full_text, [
            r"ALT\s*[:：]?\s*(\d+\.?\d*)",
        ]),
        "hemoglobin": extract_number(full_text, [
            r"혈색소\s*[:：]?\s*(\d+\.?\d*)",
            r"헤모글로빈\s*[:：]?\s*(\d+\.?\d*)",
            r"Hemoglobin\s*[:：]?\s*(\d+\.?\d*)",
        ]),
        "wbc": extract_number(full_text, [
            r"WBC\s*[:：]?\s*(\d+\.?\d*)",
            r"백혈구\s*[:：]?\s*(\d+\.?\d*)",
        ]),
        "rbc": extract_number(full_text, [
            r"RBC\s*[:：]?\s*(\d+\.?\d*)",
            r"적혈구\s*[:：]?\s*(\d+\.?\d*)",
        ]),
        "hscrp": extract_number(full_text, [
            r"hsCRP\s*[:：]?\s*(\d+\.?\d*)",
            r"고감도\s*C-?반응단백\s*[:：]?\s*(\d+\.?\d*)",
        ]),
    }

    # 표 형태 보완: 175.0 cm / 72.0 kg / 23.5
    match = re.search(
        r"(\d+\.?\d*)\s*cm\s*/\s*(\d+\.?\d*)\s*kg\s*/\s*(\d+\.?\d*)",
        full_text,
        re.IGNORECASE
    )
    if match:
        data["height"] = float(match.group(1))
        data["weight"] = float(match.group(2))

    # 표 형태 보완: 120 / 80 mmHg
    match = re.search(
        r"(\d{2,3})\s*/\s*(\d{2,3})\s*mmHg",
        full_text,
        re.IGNORECASE
    )
    if match:
        data["sbp"] = float(match.group(1))
        data["dbp"] = float(match.group(2))

    # 표 형태 보완: 총콜레스테롤 186 mg/dL
    match = re.search(
        r"(?:총\s*콜레스테롤|총콜레스테롤)[\s\S]{0,80}?(\d+\.?\d*)\s*mg/dL",
        full_text,
        re.IGNORECASE
    )
    if match:
        data["cholesterol"] = float(match.group(1))

    # 표 형태 보완: 공복혈당 98 mg/dL
    match = re.search(
        r"(?:공복혈당|혈당)[\s\S]{0,80}?(\d+\.?\d*)\s*mg/dL",
        full_text,
        re.IGNORECASE
    )
    if match:
        data["glucose"] = float(match.group(1))

    # 표 형태 보완: AST / ALT 23 / 21 U/L
    match = re.search(
        r"(?:AST\s*/\s*ALT|AST\s*ALT|간기능)[\s\S]{0,80}?(\d+\.?\d*)\s*/\s*(\d+\.?\d*)\s*U/L",
        full_text,
        re.IGNORECASE
    )
    if match:
        data["ast"] = float(match.group(1))
        data["alt"] = float(match.group(2))

    return {
        key: value
        for key, value in data.items()
        if value is not None
    }

def extract_health_data(image_file):
    client = vision.ImageAnnotatorClient()

    content = image_file.read()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        return {
            "raw_text": "",
            "extracted": {},
        }

    full_text = texts[0].description
    extracted = parse_health_data(full_text)

    return {
        "raw_text": full_text,
        "extracted": extracted,
    }