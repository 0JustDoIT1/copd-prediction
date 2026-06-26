/**
 * 헤더 우측에 오늘 날짜를 한국어 형식으로 표시.
 */

document.addEventListener("DOMContentLoaded", function () {
  var dateEl = document.getElementById("topbarDate");
  if (!dateEl) {
    return;
  }

  var days = ["일", "월", "화", "수", "목", "금", "토"];
  var now = new Date();
  var text =
    now.getFullYear() +
    "년 " +
    (now.getMonth() + 1) +
    "월 " +
    now.getDate() +
    "일 " +
    days[now.getDay()] +
    "요일";

  dateEl.innerHTML = '<i class="bi bi-calendar3"></i> ' + text;
});
