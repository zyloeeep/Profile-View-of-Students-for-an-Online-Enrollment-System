(function () {
  var btn = document.getElementById("sidebar-toggle");
  var menu = document.getElementById("sidebar-menu");
  if (!btn || !menu) return;

  function closeMenu() {
    menu.classList.add("hidden");
    menu.classList.remove("flex");
    btn.setAttribute("aria-expanded", "false");
  }

  btn.addEventListener("click", function () {
    var isHidden = menu.classList.toggle("hidden");
    menu.classList.toggle("flex", !isHidden);
    btn.setAttribute("aria-expanded", String(!isHidden));
  });

  document.addEventListener("click", function (e) {
    if (menu.classList.contains("hidden")) return;
    if (menu.contains(e.target) || btn.contains(e.target)) return;
    closeMenu();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeMenu();
  });
})();