/* Wiki chrome: breadcrumbs, right-hand table of contents with scroll-spy, previous/next, edit links. */
(function () {
  var cfg = window.DM_CONFIG || {}, nav = cfg.navigation || [];
  var file = (location.pathname.split("/").pop() || "index.html");
  var flat = [];
  nav.forEach(function (g) { g.links.forEach(function (l) { flat.push({ g: g.title, label: l.label, href: l.href }); }); });
  var i = flat.findIndex(function (l) { return l.href.split("#")[0] === file; });
  var layout = document.querySelector(".layout.has-sidebar"), art = layout && layout.querySelector("article");
  if (!layout || !art || i < 0) return;
  var cur = flat[i];
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  // Breadcrumbs
  var head = document.querySelector(".phead .wrap");
  if (head) head.insertAdjacentHTML("afterbegin", '<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Dragon Mounts 2 Wiki</a><span>' + esc(cur.g) + '</span><b aria-current="page">' + esc(cur.label) + "</b></nav>");

  // Right-hand table of contents (moved out of the left sidebar)
  var side = layout.querySelector(".guide-sidebar"), toc = null;
  if (side) Array.prototype.forEach.call(side.querySelectorAll(".guide-group"), function (g) {
    var h = g.querySelector("h2"); if (h && /on this page/i.test(h.textContent)) toc = g;
  });
  if (toc) {
    var aside = document.createElement("aside"); aside.className = "toc"; aside.setAttribute("aria-label", "On this page");
    aside.appendChild(toc); layout.appendChild(aside); layout.classList.add("has-toc");
    var links = Array.prototype.slice.call(aside.querySelectorAll("a[href^='#']"));
    var map = {}; links.forEach(function (a) { var t = document.getElementById(a.getAttribute("href").slice(1)); if (t) map[t.id] = a; });
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { links.forEach(function (a) { a.removeAttribute("aria-current"); }); map[e.target.id].setAttribute("aria-current", "true"); } });
      }, { rootMargin: "-90px 0px -70% 0px" });
      Object.keys(map).forEach(function (id) { io.observe(document.getElementById(id)); });
    }
  }

  // Previous / next page
  var p = flat[i - 1], n = flat[i + 1];
  var pager = '<nav class="pager" aria-label="Previous and next page">' +
    (p ? '<a class="prev" href="' + esc(p.href) + '"><small>Previous</small><b>' + esc(p.label) + "</b></a>" : "<span></span>") +
    (n ? '<a class="next" href="' + esc(n.href) + '"><small>Next</small><b>' + esc(n.label) + "</b></a>" : "<span></span>") + "</nav>";
  // Page meta: edit + report links
  var meta = '<p class="page-meta">' + (cfg.repo ? '<a href="' + esc(cfg.repo) + "/edit/main/" + esc(file) + '">Edit this page on GitHub</a>' : "") +
    (cfg.issues ? '<a href="' + esc(cfg.issues) + '">Report a mistake</a>' : "") + '<span id="lastmod"></span></p>';
  art.insertAdjacentHTML("beforeend", meta + pager);
  var lm = new Date(document.lastModified); if (!isNaN(lm) && lm.getFullYear() > 2020) document.getElementById("lastmod").textContent = "Last updated " + lm.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
})();
