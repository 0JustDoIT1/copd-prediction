/**
 * 환자 대시보드 — What-if 시뮬레이션.
 *
 * screening 앱의 실제 추론 엔드포인트(/predict/what-if/, screening.views.predict_whatif)에
 * fetch로 요청을 보내, 실제 LR 모델(.pkl) 기반 권고 점수를 받아온다.
 * 요청: {smoking_status, smoking_amount}
 * 응답: {risk_probability}
 *
 * 동작 방식:
 *   - 슬라이더/토글 조작은 화면 텍스트(라벨)만 즉시 갱신하고, 서버 요청은 보내지
 *     않는다. 매 조작마다 서버에 요청을 보내면 부담이 크고 응답 지연으로 UX가
 *     끊기므로, 실제 재계산은 "변화 계산하기" 버튼을 눌렀을 때 한 번만 실행한다.
 *   - 페이지 진입 시 최초 1회는 자동으로 계산을 실행한다. 이 최초 계산이 끝나기
 *     전까지 점수/문구 자리에는 샤이머(shimmer) 스켈레톤을 보여줘 빈 "0%"가
 *     순간적으로 노출되는 것을 막는다.
 *   - 값이 바뀌었는데 아직 재계산하지 않은 상태는 버튼에 절제된 섀도 링 +
 *     약한 흔들림 + 짧은 문구 변경으로 알려준다.
 *
 * 사용하는 전역 값은 patient_dashboard.html에서 Django 템플릿 변수로
 * window에 미리 세팅해둔다:
 *   window.WHATIF_CURRENT_SMOKING, window.WHATIF_CURRENT_AMOUNT, window.WHATIF_COMPUTE_URL
 *
 * 주의: 체중(BMI) 슬라이더는 제거된 상태. 실제 모델에서 HE_BMI 계수가 단순
 * 선형(체중상승 -> 권고점수 단순하락)으로 학습되어 있어, 저체중·고체중을
 * 모두 위험으로 보는 일반적인 체중-COPD 관계와 어긋나 보이는 문제가 있었고,
 * 환자가 슬라이더로 "바꿀 수 있는" 변수 중에서도 의학적으로 설명하기 까다로운
 * 항목이라 What-if 시뮬레이션 대상에서 제외함. 이 파일에는 weight 관련
 * 코드가 전혀 없어야 한다 - HTML에도 weightSlider/weightOut 요소가 없으므로,
 * 혹시 이 파일에 weight 관련 코드가 남아있으면 null 참조 에러가 난다.
 */

document.addEventListener("DOMContentLoaded", function () {
  var whatifPanel = document.getElementById("whatifPanel");
  if (!whatifPanel || whatifPanel.dataset.hasRecord !== "true") {
    return;
  }

  var COMPUTE_URL = window.WHATIF_COMPUTE_URL;
  var CURRENT_SMOKING = window.WHATIF_CURRENT_SMOKING;
  var CURRENT_AMOUNT = window.WHATIF_CURRENT_AMOUNT;

  var smokingVal = CURRENT_SMOKING;
  var amountVal = CURRENT_AMOUNT;
  var hasLoadedOnce = false;

  var smokingButtons = document.querySelectorAll("#smokingToggle button");
  var amountSlider = document.getElementById("amountSlider");
  var amountOut = document.getElementById("amountOut");
  var amountRow = document.getElementById("amountRow");
  var calcBtn = document.getElementById("whatifCalcBtn");
  var resultGrid = document.getElementById("whatifResultGrid");
  var currentScoreEl = document.getElementById("currentScore");
  var currentText = document.getElementById("currentText");
  var resultScoreEl = document.getElementById("resultScore");
  var resultText = document.getElementById("resultText");
  var resultBadge = document.getElementById("resultBadge");

  // 필수 요소 중 하나라도 없으면(HTML 구조가 어긋났으면) 조용히 종료.
  // null.addEventListener 같은 에러로 스크립트 전체가 죽는 것을 방지한다.
  var requiredElements = [
    smokingButtons.length > 0 ? true : null,
    amountSlider, amountOut, amountRow, calcBtn, resultGrid,
    currentScoreEl, currentText, resultScoreEl, resultText, resultBadge,
  ];
  if (requiredElements.indexOf(null) !== -1) {
    console.error("What-if 시뮬레이션: 필요한 화면 요소를 찾지 못해 초기화를 중단합니다.");
    return;
  }

  var calcBtnDefaultHtml = calcBtn.innerHTML;
  var currentCard = resultGrid.querySelector(".whatif-result-current");
  var simCard = resultGrid.querySelector(".whatif-result-sim");

  function getCsrfToken() {
    var input = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : "";
  }

  function syncSlidersToCurrentValues() {
    amountSlider.value = amountVal;
    amountOut.textContent = amountVal + "개비";
  }

  function markStale() {
    if (!hasLoadedOnce) {
      return;
    }
    calcBtn.classList.add("whatif-calc-btn-pulse");
    calcBtn.innerHTML = '<i class="bi bi-arrow-repeat"></i> 다시 계산하기';
  }

  function clearStale() {
    calcBtn.classList.remove("whatif-calc-btn-pulse");
    calcBtn.innerHTML = calcBtnDefaultHtml;
  }

  function updateButtons() {
    smokingButtons.forEach(function (btn) {
      var active = parseInt(btn.dataset.val, 10) === smokingVal;
      btn.classList.toggle("active", active);
    });

    // 현재흡연(2)만 흡연량 조절 가능
    var canChangeAmount = smokingVal === 2;

    amountRow.style.opacity = canChangeAmount ? "1" : "0.35";
    amountSlider.disabled = !canChangeAmount;

    if (!canChangeAmount) {
      amountSlider.value = 0;
      amountOut.textContent = "0개비";
    } else {
      amountSlider.value = amountVal;
      amountOut.textContent = amountVal + "개비";
    }
  }

  function labelFor(score) {
    return score >= 0.4
      ? "검사를 받아보시는 게 좋습니다"
      : "현재로선 특별한 권고 사항이 없습니다";
  }

  function fetchScore(smoking, amount) {
    return fetch(COMPUTE_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({
        smoking_status: smoking,
        smoking_amount: amount,
      }),
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("요청이 실패했습니다 (" + response.status + ")");
        }
        return response.json();
      })
      .then(function (data) {
        return data.risk_probability;
      });
  }

  function setLoadingState(isLoading) {
    calcBtn.disabled = isLoading;
    calcBtn.classList.toggle("is-loading", isLoading);

    if (isLoading) {
      clearStale();
    }

    if (!hasLoadedOnce) {
      return;
    }
    resultGrid.classList.toggle("is-recalculating", isLoading);
  }

  function render() {
    setLoadingState(true);

    Promise.all([
      fetchScore(CURRENT_SMOKING, CURRENT_AMOUNT),
      fetchScore(
        smokingVal,
        smokingVal === 2 ? amountVal : 0
      ),
    ])
      .then(function (scores) {
        var currentScore = scores[0];
        var simScore = scores[1];
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

        if (!hasLoadedOnce) {
          hasLoadedOnce = true;
          currentCard.classList.add("is-loaded");
          simCard.classList.add("is-loaded");
          resultBadge.classList.add("is-loaded");
        }
      })
      .catch(function (error) {
        console.error("What-if 시뮬레이션 계산 중 오류가 발생했습니다:", error);
        if (hasLoadedOnce) {
          resultBadge.textContent = "계산 실패";
        } else {
          // 최초 계산이 아예 실패한 경우, 무한 스켈레톤으로 방치되지 않도록
          // 명시적으로 실패 문구를 보여준다.
          currentText.textContent = "계산에 실패했습니다";
          resultText.textContent = "버튼을 다시 눌러주세요";
          resultBadge.textContent = "계산 실패";
          hasLoadedOnce = true;
          currentCard.classList.add("is-loaded");
          simCard.classList.add("is-loaded");
          resultBadge.classList.add("is-loaded");
        }
      })
      .finally(function () {
        setLoadingState(false);
      });
  }

  smokingButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      smokingVal = parseInt(btn.dataset.val, 10);
      updateButtons();
      markStale();
    });
  });

  amountSlider.addEventListener("input", function () {
    amountVal = parseInt(amountSlider.value, 10);
    amountOut.textContent = amountVal + "개비";
    markStale();
  });

  calcBtn.addEventListener("click", function () {
    render();
  });

  syncSlidersToCurrentValues();
  updateButtons();
  render(); // 최초 1회는 자동 계산
});