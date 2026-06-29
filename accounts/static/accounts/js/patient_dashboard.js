/**
 * 환자 대시보드 — What-if 시뮬레이션.
 *
 * computeScore()는 더미 계산식이다. screening 팀이 /predict/what-if/ 를
 * 만들면 이 함수 내부만 fetch 호출로 교체하면 된다.
 * 입력: {smoking_status, smoking_amount}
 * 출력: {risk_probability}
 *
 * 주의: 체중(BMI) 슬라이더는 의도적으로 제거됨. 실제 모델에서 HE_BMI 계수가
 * 단순 선형(체중상승 -> 권고점수 단순하락)으로 학습되어 있어, 저체중·고체중을
 * 모두 위험으로 보는 일반적인 체중-COPD 관계와 어긋나 보이는 문제가 있었고,
 * 환자가 슬라이더로 "바꿀 수 있는" 변수 중에서도 의학적으로 설명하기 까다로운
 * 항목이라 What-if 시뮬레이션 대상에서 제외하기로 함.
 *
 * 사용하는 전역 값 두 개는 patient_dashboard.html에서 Django 템플릿 변수로
 * window에 미리 세팅해둔다: window.WHATIF_CURRENT_SMOKING, window.WHATIF_CURRENT_AMOUNT
 */

document.addEventListener("DOMContentLoaded", function () {
  var whatifPanel = document.getElementById("whatifPanel");
  if (!whatifPanel || whatifPanel.dataset.hasRecord !== "true") {
    return;
  }

  var CURRENT_SMOKING = window.WHATIF_CURRENT_SMOKING;
  var CURRENT_AMOUNT = window.WHATIF_CURRENT_AMOUNT;

  var smokingVal = CURRENT_SMOKING;
  var amountVal = CURRENT_AMOUNT;

  var smokingButtons = document.querySelectorAll("#smokingToggle button");
  var amountSlider = document.getElementById("amountSlider");
  var amountOut = document.getElementById("amountOut");
  var amountRow = document.getElementById("amountRow");
  var currentScoreEl = document.getElementById("currentScore");
  var currentText = document.getElementById("currentText");
  var resultScoreEl = document.getElementById("resultScore");
  var resultText = document.getElementById("resultText");
  var resultBadge = document.getElementById("resultBadge");

  function syncSlidersToCurrentValues() {
    amountSlider.value = amountVal;
    amountOut.textContent = amountVal + "개비";
  }

  function updateButtons() {
    smokingButtons.forEach(function (btn) {
      var active = parseInt(btn.dataset.val, 10) === smokingVal;
      btn.classList.toggle("active", active);
    });
    var isNonSmoker = smokingVal === 0;
    amountRow.style.opacity = isNonSmoker ? "0.35" : "1";
    amountSlider.disabled = isNonSmoker;
  }

  function computeScore(smoking, amount) {
    var base = 0.5;
    base += smoking * 0.08;
    base += (smoking === 0 ? 0 : amount) * 0.003;
    return Math.max(0.05, Math.min(0.95, base));
  }

  function labelFor(score) {
    return score >= 0.4
      ? "검사를 받아보시는 게 좋습니다"
      : "현재로선 특별한 권고 사항이 없습니다";
  }

  function render() {
    var currentScore = computeScore(CURRENT_SMOKING, CURRENT_AMOUNT);
    var simScore = computeScore(smokingVal, amountVal);
    var diff = simScore - currentScore;

    currentScoreEl.textContent = (currentScore * 100).toFixed(1);
    currentText.textContent = labelFor(currentScore);

    resultScoreEl.textContent = (simScore * 100).toFixed(1);
    resultText.textContent = labelFor(simScore);

    var diffPct = Math.abs(diff * 100).toFixed(1);

    resultBadge.classList.remove("whatif-badge-down", "whatif-badge-up");
    if (Math.abs(diff) < 0.005) {
      resultBadge.textContent = "변화 없음";
    } else if (diff < 0) {
      resultBadge.textContent = diffPct + "%p 낮아짐";
      resultBadge.classList.add("whatif-badge-down");
    } else {
      resultBadge.textContent = diffPct + "%p 높아짐";
      resultBadge.classList.add("whatif-badge-up");
    }
  }

  smokingButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      smokingVal = parseInt(btn.dataset.val, 10);
      updateButtons();
      render();
    });
  });

  amountSlider.addEventListener("input", function () {
    amountVal = parseInt(amountSlider.value, 10);
    amountOut.textContent = amountVal + "개비";
    render();
  });

  syncSlidersToCurrentValues();
  updateButtons();
  render();
});