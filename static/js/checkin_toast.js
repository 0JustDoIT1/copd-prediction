/**
 * 체크인 토스트
 * - 세션당 1회만 노출 (sessionStorage)
 * - 닫기(X) 버튼을 누르면 토스트를 숨기고, 같은 세션 동안 다시 띄우지 않음
 * - 토스트 본문(링크) 클릭은 그대로 daily_care로 이동
 */

document.addEventListener("DOMContentLoaded", function () {
  var toast = document.getElementById("checkinToast");
  var closeBtn = document.getElementById("checkinToastClose");
  if (!toast || !closeBtn) {
    return;
  }

  var STORAGE_KEY = "checkinToastDismissed";

  // 이번 세션에 이미 닫았거나 봤다면 표시하지 않음
  if (sessionStorage.getItem(STORAGE_KEY) === "1") {
    toast.classList.add("checkin-toast-hide");
    return;
  }

  // 이번 세션에 본 것으로 기록 (닫기를 안 눌러도 다음 페이지 이동/새로고침 시 재노출 방지)
  sessionStorage.setItem(STORAGE_KEY, "1");

  closeBtn.addEventListener("click", function (event) {
    event.preventDefault();
    event.stopPropagation();
    toast.classList.add("checkin-toast-hide");
  });
});
