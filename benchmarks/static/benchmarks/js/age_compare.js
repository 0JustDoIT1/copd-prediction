document.addEventListener("DOMContentLoaded", function () {
  const mainColor =
    getComputedStyle(document.documentElement)
      .getPropertyValue("--color-main")
      .trim() || "#4a7c72";
  const accentColor =
    getComputedStyle(document.documentElement)
      .getPropertyValue("--color-accent")
      .trim() || "#a8cdc3";

  // 권고 점수 비교 차트 (가로 막대)
  if (window.SCORE_COMPARISON) {
    const scoreCtx = document.getElementById("scoreChart");
    if (scoreCtx) {
      new Chart(scoreCtx, {
        type: "bar",
        data: {
          labels: ["나", "동연령대 평균"],
          datasets: [
            {
              data: [
                window.SCORE_COMPARISON.my_score,
                window.SCORE_COMPARISON.benchmark_score,
              ],
              backgroundColor: [mainColor, accentColor],
              borderRadius: 8,
              maxBarThickness: 64,
            },
          ],
        },
        options: {
          indexAxis: "y",
          maintainAspectRatio: false,
          devicePixelRatio: Math.max(window.devicePixelRatio || 1, 2), // PDF 캡처 시 흐려지지 않도록 캔버스 자체 해상도를 높임
          plugins: { legend: { display: false } },
          scales: {
            x: {
              beginAtZero: true,
              ticks: { callback: (v) => v + "%" },
            },
          },
        },
      });
    }
  }

  // 막대 위에 값을 직접 표시하는 경량 커스텀 플러그인 (별도 라이브러리 불필요)
  const valueLabelPlugin = {
    id: "valueLabel",
    afterDatasetsDraw(chart) {
      const { ctx } = chart;
      const meta = chart.getDatasetMeta(0);
      const data = chart.data.datasets[0].data;
      const unit = chart.config._unit || "";

      ctx.save();
      ctx.font = "600 13px Pretendard, sans-serif";
      ctx.fillStyle = "#444";
      ctx.textAlign = "center";

      meta.data.forEach(function (bar, index) {
        const value = data[index];
        ctx.fillText(`${value}${unit}`, bar.x, bar.y - 8);
      });
      ctx.restore();
    },
  };

  // 건강 지표별 비교 차트 — 탭으로 선택된 패널의 차트만 그린다
  const chartInstances = {}; // variable_name -> Chart 인스턴스 (중복 생성 방지)

  function renderVariableChart(canvas) {
    if (!canvas || chartInstances[canvas.id]) return; // 이미 그려진 차트는 다시 그리지 않음

    const myValue = parseFloat(canvas.dataset.myValue);
    const benchmarkValue = parseFloat(canvas.dataset.benchmarkValue);
    const unit = canvas.dataset.unit;
    // 두 값 중 큰 쪽보다 여유 있게 Y축 최대값을 잡아 막대+라벨이 잘리지 않게 함
    const suggestedMax = Math.max(myValue, benchmarkValue) * 1.25;

    const chart = new Chart(canvas, {
      type: "bar",
      data: {
        labels: ["나", "평균"],
        datasets: [
          {
            data: [myValue, benchmarkValue],
            backgroundColor: [mainColor, accentColor],
            borderRadius: 6,
            maxBarThickness: 64,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        devicePixelRatio: Math.max(window.devicePixelRatio || 1, 2), // PDF 캡처 시 흐려지지 않도록 캔버스 자체 해상도를 높임
        layout: { padding: { top: 24 } },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ctx.parsed.y + unit,
            },
          },
        },
        scales: {
          y: { beginAtZero: true, suggestedMax: suggestedMax },
        },
      },
      plugins: [valueLabelPlugin],
    });
    chart.config._unit = unit;
    chart.update();
    chartInstances[canvas.id] = chart;
  }

  function activateVariableTab(targetName) {
    document.querySelectorAll(".variable-tab").forEach(function (tab) {
      tab.classList.toggle("active", tab.dataset.target === targetName);
    });
    document.querySelectorAll(".variable-panel").forEach(function (panel) {
      const isActive = panel.dataset.panel === targetName;
      panel.classList.toggle("active", isActive);
      if (isActive) {
        renderVariableChart(panel.querySelector(".variable-chart"));
      }
    });
  }

  document.querySelectorAll(".variable-tab").forEach(function (tab) {
    tab.addEventListener("click", function () {
      activateVariableTab(tab.dataset.target);
    });
  });

  // 최초 진입 시 활성화된(첫 번째) 탭의 차트만 그림
  const initialTab = document.querySelector(".variable-tab.active");
  if (initialTab) {
    activateVariableTab(initialTab.dataset.target);
  }
});
