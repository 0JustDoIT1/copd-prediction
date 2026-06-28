document.addEventListener("DOMContentLoaded", function () {
  const mainColor =
    getComputedStyle(document.documentElement)
      .getPropertyValue("--color-main")
      .trim() || "#4a7c72";
  const accentColor =
    getComputedStyle(document.documentElement)
      .getPropertyValue("--color-accent")
      .trim() || "#a8cdc3";

  const chartInstances = {}; // canvas.id -> Chart 인스턴스 (탭 전환 시 중복 생성 방지)

  function renderLineChart(canvas) {
    if (!canvas || chartInstances[canvas.id]) return;

    let series = [];
    try {
      series = JSON.parse(canvas.dataset.series || "[]");
    } catch (e) {
      series = [];
    }
    const unit = canvas.dataset.unit || "";

    // 데이터가 1건뿐이면 선이 아니라 점 하나만 찍히는 게 정상 동작
    chartInstances[canvas.id] = new Chart(canvas, {
      type: "line",
      data: {
        labels: series.map((p) => p.date),
        datasets: [
          {
            data: series.map((p) => p.value),
            borderColor: mainColor,
            backgroundColor: mainColor,
            pointBackgroundColor: mainColor,
            pointRadius: 5,
            pointHoverRadius: 7,
            borderWidth: 2,
            tension: 0.25,
            fill: false,
          },
        ],
      },
      options: {
        maintainAspectRatio: false,
        devicePixelRatio: Math.max(window.devicePixelRatio || 1, 2), // PDF 캡처 시 흐려지지 않도록 캔버스 자체 해상도를 높임
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ctx.parsed.y + unit,
            },
          },
        },
        scales: {
          y: { beginAtZero: false },
          x: {
            ticks: { autoSkip: true, maxRotation: 0 },
          },
        },
      },
    });
  }

  function activateTimelineTab(targetName) {
    document.querySelectorAll(".timeline-tab").forEach(function (tab) {
      tab.classList.toggle("active", tab.dataset.target === targetName);
    });
    document.querySelectorAll(".timeline-panel").forEach(function (panel) {
      const isActive = panel.dataset.panel === targetName;
      panel.classList.toggle("active", isActive);
      if (isActive) {
        const canvas = panel.querySelector("canvas");
        renderLineChart(canvas);
      }
    });
  }

  document.querySelectorAll(".timeline-tab").forEach(function (tab) {
    tab.addEventListener("click", function () {
      activateTimelineTab(tab.dataset.target);
    });
  });

  // 최초 진입 시 활성화된(권고 점수) 탭의 차트만 그림
  const initialTab = document.querySelector(".timeline-tab.active");
  if (initialTab) {
    activateTimelineTab(initialTab.dataset.target);
  }
});
