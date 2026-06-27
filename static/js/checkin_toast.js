/**
 * 체크인 토스트
 * - 노출 여부 자체는 백엔드(Django session)가 결정 — 서버가 show_checkin_toast가
 *   True일 때만 토스트 HTML을 렌더링하므로, 이 스크립트는 닫기(X) 버튼 처리만 담당한다.
 * - 토스트 본문(링크) 클릭은 그대로 daily_care로 이동
 */

document.addEventListener("DOMContentLoaded", function () {
  var toast = document.getElementById("checkinToast");
  var closeBtn = document.getElementById("checkinToastClose");
  if (!toast || !closeBtn) {
    return;
  }

  closeBtn.addEventListener("click", function (event) {
    event.preventDefault();
    event.stopPropagation();
    toast.classList.add("checkin-toast-hide");
  });
});
