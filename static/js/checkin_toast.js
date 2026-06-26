/**
 * 체크인 토스트 — 닫기(X) 버튼을 누르면 토스트를 숨긴다.
 * 토스트 본문(링크) 클릭은 그대로 daily_care로 이동하도록 막지 않는다.
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
