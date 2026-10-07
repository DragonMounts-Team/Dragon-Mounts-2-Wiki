/* DragonMounts 2 Wiki: shared behaviour. Plain JavaScript, no dependencies. */
(function () {
  "use strict";
  var root = document.documentElement;
  var CFG = window.DM_CONFIG || {};
  function $(s, c) { return (c || document).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (m) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[m]; }); }
  function setWikiSettings() {
    var theme = CFG.theme || {};
    var colors = {
      "--wiki-accent-light": theme.accentLight,
      "--wiki-accent-dark": theme.accentDark,
      "--wiki-hero-light": theme.heroLight,
      "--wiki-hero-dark": theme.heroDark
    };
    Object.keys(colors).forEach(function (name) {
      if (/^#[0-9a-f]{6}$/i.test(colors[name] || "")) {
        root.style.setProperty(name, colors[name]);
      }
    });
  }
  function renderNavigation() {
    if (!Array.isArray(CFG.navigation)) return;
    var currentPath = window.location.pathname;
    $$(".nav-drawer nav, .guide-sidebar nav").forEach(function (nav) {
      var fragment = document.createDocumentFragment();
      CFG.navigation.forEach(function (group) {
        if (!group || typeof group.title !== "string" || !Array.isArray(group.links)) return;
        var section = document.createElement("section");
        section.className = "guide-group";
        var heading = document.createElement("h2");
        heading.textContent = group.title;
        section.appendChild(heading);
        var list = document.createElement("ul");
        group.links.forEach(function (page) {
          if (!page || typeof page.label !== "string" || typeof page.href !== "string") return;
          var item = document.createElement("li");
          var link = document.createElement("a");
          link.textContent = page.label;
          link.href = page.href;
          if (new URL(page.href, window.location.href).pathname === currentPath) {
            link.setAttribute("aria-current", "page");
          }
          item.appendChild(link);
          list.appendChild(item);
        });
        section.appendChild(list);
        fragment.appendChild(section);
      });
      nav.replaceChildren(fragment);
    });
  }
  setWikiSettings();
  renderNavigation();

  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  /* ---------- config-driven links ---------- */
  $$("[data-link]").forEach(function (el) {
    var url = CFG[el.getAttribute("data-link")];
    var a = el.tagName === "A" ? el : $("a", el);
    if (url && a) { a.href = url; el.hidden = false; } else { el.hidden = true; }
  });
  /* hide a footer column when none of its links are set */
  $$(".footgrid > div").forEach(function (col) {
    var ls = $$("[data-link]", col);
    if (ls.length && ls.every(function (l) { return l.hidden; })) col.hidden = true;
  });

  /* ---------- theme ---------- */
  var tbtn = $("#theme");
  var themeTransitionTimer;
  function syncThemeControl() {
    if (!tbtn) return;
    var dark = root.getAttribute("data-theme") === "dark" ||
      (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme:dark)").matches);
    tbtn.setAttribute("aria-pressed", dark ? "true" : "false");
    tbtn.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
    tbtn.title = dark ? "Switch to light mode" : "Switch to dark mode";
  }
  if (tbtn) {
    syncThemeControl();
    tbtn.addEventListener("click", function () {
      var cur = root.getAttribute("data-theme");
      if (!cur) cur = matchMedia("(prefers-color-scheme:dark)").matches ? "dark" : "light";
      var next = cur === "dark" ? "light" : "dark";
      function applyTheme() {
        var reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
        if (!reduceMotion) {
          root.classList.add("theme-transitioning");
          clearTimeout(themeTransitionTimer);
          themeTransitionTimer = setTimeout(function () { root.classList.remove("theme-transitioning"); }, 380);
        }
        root.setAttribute("data-theme", next);
        store.set("dm2-theme", next);
        syncThemeControl();
      }
      applyTheme();
    });
  }

  var navToggle = $("#nav-toggle"), navDrawer = $("#nav-drawer"), navClose = $("#nav-close");
  if (navToggle && navDrawer) {
    navToggle.addEventListener("click", function () { navDrawer.showModal(); navToggle.setAttribute("aria-expanded", "true"); });
    if (navClose) navClose.addEventListener("click", function () { navDrawer.close(); });
    navDrawer.addEventListener("click", function (event) { if (event.target === navDrawer) navDrawer.close(); });
    navDrawer.addEventListener("close", function () { navToggle.setAttribute("aria-expanded", "false"); navToggle.focus(); });
    $$(".nav-drawer a").forEach(function (a) { a.addEventListener("click", function () { navDrawer.close(); }); });
  }

  /* ---------- items filter ---------- */
  var il = $("#itemlist");
  if (il) {
    var grp = "all", iq = $("#iq");
    var cards = $$(".item", il);
    var drawItems = function () {
      var q = iq.value.trim().toLowerCase(), n = 0;
      cards.forEach(function (c) {
        var ok = (grp === "all" || c.getAttribute("data-group") === grp) &&
          (!q || c.textContent.toLowerCase().indexOf(q) > -1);
        c.hidden = !ok; if (ok) n++;
      });
      $("#icount").textContent = n + (n === 1 ? " item" : " items");
      $("#iempty").hidden = n > 0;
    };
    $$("#igroups button").forEach(function (b) {
      b.addEventListener("click", function () {
        grp = b.getAttribute("data-group");
        $$("#igroups button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        drawItems();
      });
    });
    iq.addEventListener("input", drawItems);
    drawItems();
  }

  /* ---------- install checklist ---------- */
  var chk = $$(".steps input");
  if (chk.length) {
    var SK = "dm2-install";
    try { var sv = JSON.parse(store.get(SK) || "[]"); chk.forEach(function (c, i) { c.checked = !!sv[i]; }); } catch (e) {}
    var prog = function () {
      var n = chk.filter(function (c) { return c.checked; }).length;
      $("#pbar").style.width = (n / chk.length * 100) + "%";
      $("#ptxt").textContent = n === chk.length ? "All done. Load your world and take off." : n + " of " + chk.length + " steps done";
      store.set(SK, JSON.stringify(chk.map(function (c) { return c.checked; })));
    };
    chk.forEach(function (c) { c.addEventListener("change", prog); });
    var rs = $("#preset");
    if (rs) rs.addEventListener("click", function () { chk.forEach(function (c) { c.checked = false; }); prog(); });
    prog();
  }

  $$("[data-toggle-all]").forEach(function (b) {
    b.addEventListener("click", function () {
      var open = b.getAttribute("data-toggle-all") === "open";
      $$(b.getAttribute("data-scope") + " details").forEach(function (d) { if (!d.hidden) d.open = open; });
    });
  });

  /* ---------- FAQ filter ---------- */
  var fq = $("#fq");
  if (fq) {
    var qs = $$("#faqlist details.q"), fg = $$("#faqlist .fgroup");
    fq.addEventListener("input", function () {
      var q = fq.value.trim().toLowerCase(), n = 0;
      qs.forEach(function (d) {
        var ok = !q || d.textContent.toLowerCase().indexOf(q) > -1;
        d.hidden = !ok; if (ok) { n++; if (q) d.open = true; }
      });
      fg.forEach(function (g) { g.hidden = !$$("details.q", g).some(function (d) { return !d.hidden; }); });
      $("#fcount").textContent = q ? n + (n === 1 ? " answer" : " answers") : "";
      $("#fempty").hidden = n > 0;
    });
  }

  /* ---------- dragon appearance explorer ---------- */
  var appearanceExplorer = $("#appearance-explorer");
  if (appearanceExplorer) {
    var appearanceTypes = JSON.parse(appearanceExplorer.getAttribute("data-appearances") || "[]");
    appearanceTypes.forEach(function (group) {
      var key = group.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
      var card = $('[data-appearance="' + key + '"]', appearanceExplorer);
      if (!card) return;
      var image = $("[data-appearance-image]", card);
      var variantLabel = $("[data-appearance-variant]", card);
      var select = $("[data-appearance-select]", card);
      if (!image || !variantLabel || !select) return;

      select.addEventListener("change", function () {
        var variant = group.variants[Number(select.value)];
        if (!variant) return;
        image.src = variant.src;
        image.alt = group.name + " Dragon, " + variant.name + " appearance";
        variantLabel.textContent = variant.name;
      });
    });
  }

  /* ---------- open a section when linked to it ---------- */
  function openHash() {
    var id = decodeURIComponent((location.hash || "").slice(1)); if (!id) return;
    var t = document.getElementById(id); if (!t) return;
    var p = t;
    while (p) { if (p.tagName === "DETAILS") p.open = true; p = p.parentElement; }
    setTimeout(function () { t.scrollIntoView(); }, 30);
  }
  addEventListener("hashchange", openHash); openHash();

  /* ---------- table of contents scroll-spy ---------- */
  var tl = $$(".toc a");
  if (tl.length && "IntersectionObserver" in window) {
    var map = {};
    tl.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting && map[e.target.id]) {
          tl.forEach(function (a) { a.removeAttribute("aria-current"); });
          map[e.target.id].setAttribute("aria-current", "true");
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    Object.keys(map).forEach(function (id) { var h = document.getElementById(id); if (h) io.observe(h); });
  }

  /* ---------- site search ---------- */
  var sx = $("#sx"), sq = $("#sq"), sr = $("#sres"), lastFocus = null;
  var IDX = window.DM_INDEX || [];
  if (Array.isArray(CFG.navigation)) {
    CFG.navigation.forEach(function (group) {
      (group && Array.isArray(group.links) ? group.links : []).forEach(function (page) {
        if (!page || typeof page.label !== "string" || typeof page.href !== "string") return;
        if (!IDX.some(function (entry) { return entry.p === page.href && entry.k === "Page"; })) {
          IDX.push({ t: page.label, p: page.href, a: "", k: "Page", x: "Wiki guide" });
        }
      });
    });
  }
  function rank(e, terms) {
    var t = e.t.toLowerCase(), x = (e.x || "").toLowerCase(), s = 0;
    for (var i = 0; i < terms.length; i++) {
      var w = terms[i], v = 0;
      if (t === w) v = 100; else if (t.indexOf(w) === 0) v = 60; else if (t.indexOf(" " + w) > -1) v = 40;
      else if (t.indexOf(w) > -1) v = 25; else if (x.indexOf(w) > -1) v = 10; else return 0;
      s += v;
    }
    return s;
  }
  function drawSearch() {
    var q = sq.value.trim().toLowerCase();
    if (!q) { sr.innerHTML = "<p>Search dragons, eggs, taming, riding, and equipment.</p>"; return; }
    var terms = q.split(/\s+/), out = [];
    IDX.forEach(function (e) { var s = rank(e, terms); if (s) out.push([s, e]); });
    out.sort(function (a, b) { return b[0] - a[0]; });
    out = out.slice(0, 10);
    sr.innerHTML = out.length ? out.map(function (r) {
      var e = r[1];
      return '<a href="' + esc(e.p + (e.a ? "#" + e.a : "")) + '">' + esc(e.t) + "<small>" + esc(e.k) + "</small></a>";
    }).join("") : '<p>No results for "' + esc(sq.value.trim()) + '". Try a shorter word.</p>';
  }
  function openSearch() {
    if (!sx) return;
    lastFocus = document.activeElement; sx.hidden = false; sq.value = ""; drawSearch(); sq.focus();
  }
  function closeSearch() { if (!sx || sx.hidden) return; sx.hidden = true; if (lastFocus && lastFocus.focus) lastFocus.focus(); }
  var sb = $("#sbtn"); if (sb) sb.addEventListener("click", openSearch);
  if (sq) {
    sq.addEventListener("input", drawSearch);
    sx.addEventListener("click", function (e) { if (e.target === sx) closeSearch(); });
    sx.addEventListener("keydown", function (e) {
      var links = $$("a", sr), i = links.indexOf(document.activeElement);
      if (e.key === "ArrowDown") { e.preventDefault(); (links[i + 1] || links[0] || sq).focus(); }
      else if (e.key === "ArrowUp") { e.preventDefault(); if (i <= 0) sq.focus(); else links[i - 1].focus(); }
      else if (e.key === "Enter" && document.activeElement === sq && links[0]) { location.href = links[0].href; }
      else if (e.key === "Tab") {
        var f = [sq].concat(links), j = f.indexOf(document.activeElement);
        e.preventDefault(); f[(j + (e.shiftKey ? -1 : 1) + f.length) % f.length].focus();
      }
    });
  }
  addEventListener("keydown", function (e) {
    var tag = document.activeElement && document.activeElement.tagName;
    var typing = tag === "TEXTAREA" || (tag === "INPUT" && document.activeElement.type !== "checkbox");
    if (e.key === "Escape") closeSearch();
    else if ((e.key === "/" && !typing) || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k")) { e.preventDefault(); openSearch(); }
  });

})();
