"""
Google Vision OCR 처리
"""

from google.cloud import vision
import io


def extract_health_data(image_file):
    client = vision.ImageAnnotatorClient()

    content = image_file.read()

    image = vision.Image(
        content=content
    )

    response = client.text_detection(
        image=image
    )

    texts = response.text_annotations

    if not texts:
        return {}

    full_text = texts[0].description

    print(full_text)

    return {}