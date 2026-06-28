/**
 * 공용 PDF 내보내기 함수 (가장 단순한 형태).
 *
 * html2canvas로 "지금 화면에 보이는 모습 그대로"를 캡처하고, jsPDF로
 * 그 이미지를 PDF 한 장에 담아 다운로드한다. PDF 저장 버튼 자체도 화면에
 * 그대로 둔 채 캡처한다 (버튼이 PDF에 함께 찍히는 것은 의도된 동작).
 *
 * 의도적인 단순화:
 *   탭 구조 화면(동연령대 비교, 추적기록 타임라인)에서 6개 탭을 전부 한
 *   PDF에 모으려는 시도는 화면 깜빡임, 차트 잘림, 검은 배경 등 다양한
 *   문제를 반복적으로 일으켰다. 이 함수는 그런 시도를 모두 포기하고,
 *   "지금 선택된 탭 1개"만 PDF로 저장하는 가장 단순하고 예측 가능한
 *   동작만 한다. 여러 탭을 저장하려면 탭을 바꿔가며 버튼을 여러 번 눌러
 *   탭별로 별도 PDF를 받으면 된다.
 *
 * 사용법:
 *   document.getElementById('pdfExportBtn').addEventListener('click', function () {
 *     exportVisibleAreaToPdf('pdfExportTarget', 'filename.pdf');
 *   });
 *
 * @param {string} elementId  캡처할 대상 요소의 id (페이지 전체를 감싸는 div)
 * @param {string} filename   다운로드될 PDF 파일명
 */
function exportVisibleAreaToPdf(elementId, filename) {
  var target = document.getElementById(elementId);
  if (!target) {
    console.error(
      "exportVisibleAreaToPdf: 대상 요소를 찾을 수 없습니다 (id=" +
        elementId +
        ")",
    );
    return;
  }
  if (typeof html2canvas === "undefined") {
    console.error(
      "exportVisibleAreaToPdf: html2canvas 라이브러리가 로드되지 않았습니다.",
    );
    return;
  }
  var JsPdfCtor =
    window.jspdf && window.jspdf.jsPDF ? window.jspdf.jsPDF : window.jsPDF;
  if (!JsPdfCtor) {
    console.error(
      "exportVisibleAreaToPdf: jsPDF 라이브러리가 로드되지 않았습니다.",
    );
    return;
  }

  // Bootstrap Icons 같은 아이콘 폰트는 @font-face로 비동기 로드되는데,
  // 캡처 시점에 아직 로드가 끝나지 않으면 그 아이콘 부분이 빈 칸으로
  // 캡처되는 문제가 있다. document.fonts.ready로 모든 웹폰트(아이콘
  // 폰트 포함) 로딩이 끝날 때까지 기다린 뒤에 캡처를 시작한다.
  var fontsReady =
    document.fonts && document.fonts.ready
      ? document.fonts.ready
      : Promise.resolve();

  // fonts.ready 이후에도 실제 화면 리페인트가 한 프레임 정도 더 필요할 수 있어
  // 짧게 한 번 더 대기한다 (아이콘 폰트가 적용된 모습이 화면에 그려질 시간 확보).
  fontsReady
    .then(function () {
      return new Promise(function (resolve) {
        requestAnimationFrame(function () {
          requestAnimationFrame(resolve);
        });
      });
    })
    .then(function () {
      return html2canvas(target, {
        scale: 3, // 해상도를 높여 텍스트/차트가 흐릿하게 나오지 않도록 함
        useCORS: true,
        backgroundColor: "#ffffff",
        imageTimeout: 0,
        logging: false,
      });
    })
    .then(function (canvas) {
      // PNG는 무손실 포맷이라 텍스트나 차트의 선명한 경계가 JPEG처럼
      // 뭉개지지 않는다. 사진이 아닌 화면 캡처(텍스트+도형)에는 PNG가 더 적합하다.
      var imgData = canvas.toDataURL("image/png");

      var PAGE_WIDTH_MM = 210; // A4
      var PAGE_HEIGHT_MM = 297;
      var MARGIN_MM = 10;
      var contentWidthMm = PAGE_WIDTH_MM - MARGIN_MM * 2;
      var imgHeightMm = (canvas.height / canvas.width) * contentWidthMm;

      var doc = new JsPdfCtor({
        unit: "mm",
        format: "a4",
        orientation: "portrait",
        compress: false,
      });

      // 이미지가 한 페이지보다 길면 여러 페이지로 나눠서 이어 붙인다.
      var pageContentHeightMm = PAGE_HEIGHT_MM - MARGIN_MM * 2;
      var remainingHeightMm = imgHeightMm;
      var positionMm = 0;
      var isFirstPage = true;

      while (remainingHeightMm > 0) {
        if (!isFirstPage) {
          doc.addPage();
        }
        // addImage에 음수 y를 줘서 다음 페이지에서는 이미지의 이어지는 부분이
        // 보이도록 한다 (이미지 전체를 매번 같은 크기로 그리되 위치만 위로 올림).
        // NONE 압축을 명시해 jsPDF가 이미지를 추가로 손실 압축하지 않도록 한다.
        doc.addImage(
          imgData,
          "PNG",
          MARGIN_MM,
          MARGIN_MM - positionMm,
          contentWidthMm,
          imgHeightMm,
          undefined,
          "NONE",
        );
        remainingHeightMm -= pageContentHeightMm;
        positionMm += pageContentHeightMm;
        isFirstPage = false;
      }

      doc.save(filename);
    })
    .catch(function (error) {
      console.error("PDF 생성 중 오류가 발생했습니다:", error);
    });
}
