/**
 * 체크인 토스트
 * - 기본 노출 여부는 백엔드(daily_care.has_checked_in_today)가 결정 — 서버가
 *   show_checkin_toast가 True일 때만 토스트 HTML을 렌더링한다.
 * - "오늘 하루 안 보기"는 그 위에 한 단계 더 — localStorage에 오늘 날짜를
 *   기록해두고, 같은 날짜라면 서버가 보여줘도 클라이언트에서 즉시 숨긴다.
 *   날짜가 바뀌면 자동으로 무효화되어 다시 노출된다.
 */

document.addEventListener("DOMContentLoaded", function () {
  var toast = document.getElementById("checkinToast");
  if (!toast) {
    return;
  }

  var STORAGE_KEY = "checkinToastDismissedDate";
  var todayStr = new Date().toDateString();

  if (localStorage.getItem(STORAGE_KEY) === todayStr) {
    toast.classList.add("checkin-toast-hide");
    return;
  }

  var closeBtn = document.getElementById("checkinToastClose");
  var dismissBtn = document.getElementById("checkinToastDismiss");

  if (closeBtn) {
    closeBtn.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      toast.classList.add("checkin-toast-hide");
    });
  }

  if (dismissBtn) {
    dismissBtn.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      localStorage.setItem(STORAGE_KEY, todayStr);
      toast.classList.add("checkin-toast-hide");
    });
  }
});
