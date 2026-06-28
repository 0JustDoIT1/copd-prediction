# PDF 저장 기능 사용 가이드

화면에 "PDF로 저장" 버튼을 추가하는 방법입니다.

## 동작 방식

- 지금 화면에 보이는 모습 그대로를 PDF로 저장합니다.
- 탭으로 화면이 나뉘어 있다면, 탭을 바꿔가며 버튼을 눌러 탭별로 따로 저장하면 됩니다.
- 차트가 있는 화면은 화질이 살짝 흐리게 나올 수 있습니다.

## 적용 방법

### 1. 캡처할 영역에 id 부여

```html
{% block content %}
<div class="내화면-page" id="pdfExportTarget">...</div>
{% endblock %}
```

### 2. 버튼 추가

```html
<button type="button" class="pdf-export-btn" id="pdfExportBtn">
  <i class="bi bi-file-earmark-pdf"></i> PDF로 저장
</button>
```

```css
.pdf-export-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--color-main);
  background: #fff;
  color: var(--color-main);
  font-size: 13px;
  font-weight: 600;
  padding: 9px 16px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.pdf-export-btn:hover {
  background: var(--color-main);
  color: #fff;
}
```

### 3. 라이브러리 로드 + 클릭 핸들러 연결

```html
{% block extra_js %}
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="{% static 'js/pdf_export.js' %}"></script>
<script>
  const pdfExportBtn = document.getElementById("pdfExportBtn");
  if (pdfExportBtn) {
    pdfExportBtn.addEventListener("click", function () {
      exportVisibleAreaToPdf("pdfExportTarget", "파일명.pdf");
    });
  }
</script>
{% endblock %}
```

`pdf_export.js`는 `common/static/js/pdf_export.js`에 있는 공용 파일을 그대로 가져다 쓰면 됩니다.

## 파일명을 "날짜*환자명*제목" 형식으로 만들기

```python
from common.utils.pdf_filename import build_pdf_filename

def my_view(request):
    return render(request, 'my_app/my_page.html', {
        'pdf_filename': build_pdf_filename('내화면제목', request.user.name),
    })
```

`title`은 공백 없이 한글로 (예: `'검사결과리포트'`). 결과: `260628_홍길동_검사결과리포트.pdf`

템플릿에서는:

```html
exportVisibleAreaToPdf('pdfExportTarget', '{{ pdf_filename }}');
```

## 참고 예시

`benchmarks/templates/benchmarks/age_compare.html`, `risk_factors.html`에 이미 적용되어 있으니 그대로 참고하면 됩니다.
