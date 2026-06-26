/**
 * 환자 대시보드 히어로 섹션 — 슬로건 순환 효과.
 *
 * 1) 제목+부제 페이드인 (제목은 타이핑으로 채워지는 동안 페이드인)
 * -> 2) 완성 상태로 일정 시간 유지
 * -> 3) 제목+부제 동시 페이드아웃
 * -> 4) 다음 슬로건으로 교체 후 1)부터 반복.
 */

document.addEventListener("DOMContentLoaded", function () {
  var titleEl = document.getElementById("heroTitle");
  var subtitleEl = document.getElementById("heroSubtitle");
  if (!titleEl || !subtitleEl) {
    return;
  }

  var slogans = [
    {
      line1: "검진 데이터로 폐 건강을 먼저 살피고",
      line2: "당신의 호흡을 끝까지 함께 책임집니다",
      subtitle:
        "이 점수는 진단이 아닌 권고이며, 최종 검토는 의사가 직접 진행합니다.",
    },
    {
      line1: "오늘의 작은 기록이",
      line2: "내일의 건강한 호흡이 됩니다",
      subtitle: "꾸준한 기록은 변화를 가장 먼저 알아채는 방법입니다.",
    },
  ];

  var TYPE_SPEED = 38; // 한 글자 타이핑 간격(ms)
  var FADE_DURATION = 500; // 제목/부제 페이드 인/아웃 시간(ms)
  var HOLD_DURATION = 3800; // 완성 상태로 유지하는 시간(ms)
  var GAP_DURATION = 300; // 페이드아웃 후 다음 슬로건 시작 전 공백(ms)

  var current = 0;

  var span1 = document.createElement("span");
  var br = document.createElement("br");
  var span2 = document.createElement("span");
  titleEl.appendChild(span1);
  titleEl.appendChild(br);
  titleEl.appendChild(span2);

  titleEl.style.transition = "opacity " + FADE_DURATION + "ms ease";
  subtitleEl.style.transition = "opacity " + FADE_DURATION + "ms ease";
  titleEl.style.opacity = "0";
  subtitleEl.style.opacity = "0";

  function typeText(span, text, onDone) {
    var i = 0;
    function step() {
      if (i <= text.length) {
        span.textContent = text.slice(0, i);
        i++;
        setTimeout(step, TYPE_SPEED);
      } else if (onDone) {
        onDone();
      }
    }
    step();
  }

  function runCycle() {
    var slogan = slogans[current];

    span1.textContent = "";
    span2.textContent = "";
    subtitleEl.textContent = slogan.subtitle;

    // 제목을 페이드인시키면서, 그 안의 글자는 타이핑으로 채운다.
    titleEl.style.opacity = "1";
    typeText(span1, slogan.line1, function () {
      typeText(span2, slogan.line2, function () {
        subtitleEl.style.opacity = "1";

        setTimeout(function () {
          // 제목과 부제를 동시에 페이드아웃.
          titleEl.style.opacity = "0";
          subtitleEl.style.opacity = "0";

          setTimeout(function () {
            current = (current + 1) % slogans.length;
            setTimeout(runCycle, GAP_DURATION);
          }, FADE_DURATION);
        }, HOLD_DURATION);
      });
    });
  }

  setTimeout(runCycle, 100);
});
