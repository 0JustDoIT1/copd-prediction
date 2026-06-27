document.addEventListener("DOMContentLoaded", function () {
  var input = document.getElementById("faqSearchInput");
  var items = document.querySelectorAll(".faq-item");
  var noResult = document.querySelector(".faq-no-result");

  if (!input) {
    return;
  }

  input.addEventListener("input", function () {
    var query = input.value.trim().toLowerCase();
    var visibleCount = 0;

    items.forEach(function (item) {
      var question = (
        item.getAttribute("data-faq-question") || ""
      ).toLowerCase();
      var matches = question.indexOf(query) !== -1;
      item.classList.toggle("d-none", !matches);
      if (matches) {
        visibleCount += 1;
      }
    });

    if (noResult) {
      noResult.classList.toggle("d-none", visibleCount !== 0);
    }
  });
});
