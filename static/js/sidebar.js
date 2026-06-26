/**
 * base.html(사이드바 레이아웃) 전용 스크립트.
 * - 사이드바 그룹(검진/검사, 비교 리포트 등) 드롭다운 펼침/접힘
 * - 모바일 화면에서 사이드바 열기/닫기 + 배경 오버레이 클릭 시 닫기
 */

document.addEventListener('DOMContentLoaded', function () {
  // 사이드바 그룹(드롭다운) 토글
  document.querySelectorAll('.nav-group-toggle').forEach(function (toggle) {
    toggle.addEventListener('click', function () {
      var targetId = toggle.getAttribute('data-target');
      var submenu = document.getElementById(targetId);
      var isOpen = !submenu.classList.contains('d-none');
      submenu.classList.toggle('d-none', isOpen);
      toggle.setAttribute('aria-expanded', String(!isOpen));
      toggle.classList.toggle('group-open', !isOpen);
    });
  });

  // 모바일 사이드바 열기/닫기
  var sidebar = document.getElementById('sidebar');
  var sidebarToggle = document.getElementById('sidebarToggle');
  var sidebarOverlay = document.getElementById('sidebarOverlay');

  function openSidebar() {
    sidebar.classList.add('open');
    sidebarOverlay.classList.add('show');
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    sidebarOverlay.classList.remove('show');
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function () {
      if (sidebar.classList.contains('open')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', closeSidebar);
  }
});