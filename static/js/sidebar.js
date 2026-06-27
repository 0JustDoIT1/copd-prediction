/**
 * base.html(사이드바 레이아웃) 전용 스크립트.
 * - 사이드바 그룹(검진/검사, 비교 리포트 등) Bootstrap Collapse 연동 + caret 회전
 * - 모바일 화면에서 사이드바 열기/닫기 + 배경 오버레이 클릭 시 닫기
 */

document.addEventListener("DOMContentLoaded", function () {
  // 사이드바 그룹(드롭다운) — Bootstrap Collapse 이벤트에 맞춰 caret 회전만 처리
  document
    .querySelectorAll(".nav-submenu.collapse")
    .forEach(function (submenu) {
      var toggle = document.querySelector(
        '[data-bs-target="#' + submenu.id + '"]',
      );
      if (!toggle) {
        return;
      }

      // 초기 상태 동기화 (서버에서 active_group으로 이미 show된 경우 caret도 펼쳐진 모양으로)
      if (submenu.classList.contains("show")) {
        toggle.classList.add("group-open");
      }

      submenu.addEventListener("shown.bs.collapse", function () {
        toggle.classList.add("group-open");
        toggle.setAttribute("aria-expanded", "true");
      });

      submenu.addEventListener("hidden.bs.collapse", function () {
        toggle.classList.remove("group-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });

  // 모바일 사이드바 열기/닫기
  var sidebar = document.getElementById("sidebar");
  var sidebarToggle = document.getElementById("sidebarToggle");
  var sidebarOverlay = document.getElementById("sidebarOverlay");

  function openSidebar() {
    sidebar.classList.add("open");
    sidebarOverlay.classList.add("show");
  }

  function closeSidebar() {
    sidebar.classList.remove("open");
    sidebarOverlay.classList.remove("show");
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", function () {
      if (sidebar.classList.contains("open")) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener("click", closeSidebar);
  }
});
