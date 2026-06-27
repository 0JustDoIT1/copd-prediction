document.addEventListener("DOMContentLoaded", function () {
  var tabs = document.querySelectorAll(".content-tab");

  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      var targetId = tab.getAttribute("data-target");

      tabs.forEach(function (t) {
        t.classList.remove("active");
      });
      tab.classList.add("active");

      document.querySelectorAll(".content-list").forEach(function (panel) {
        panel.classList.add("d-none");
      });
      document.getElementById(targetId).classList.remove("d-none");
    });
  });
});
