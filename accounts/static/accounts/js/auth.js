document.addEventListener('DOMContentLoaded', function () {
  var errorBoxes = document.querySelectorAll('.js-server-error');

  errorBoxes.forEach(function (box) {
    var watchIds = (box.getAttribute('data-watch') || '')
      .split(',')
      .map(function (id) { return id.trim(); })
      .filter(Boolean);

    watchIds.forEach(function (id) {
      var input = document.getElementById(id);
      if (!input) return;

      input.addEventListener('input', function () {
        box.style.display = 'none';
      });
    });
  });
});