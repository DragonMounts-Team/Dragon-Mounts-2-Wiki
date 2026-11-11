/* Live GitHub feed: releases, pre-releases and commits for DragonMounts2-Bedrock.
   Static data (assets/releases.json, assets/commits.json) is kept fresh by CI; this script
   also asks the GitHub API in the browser (cached 10 min) so new releases show up immediately. */
(function () {
  var REPO = "DragonMounts-Team/DragonMounts2-Bedrock", API = "https://api.github.com/repos/" + REPO;
  var TAGURL = "https://github.com/" + REPO + "/releases/tag/";
  var $ = function (s) { return document.querySelector(s); };
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function slug(s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); }
  function clean(t) {
    return t.replace(/!\[[^\]]*\]\([^)]*\)/g, "").replace(/\[([^\]]+)\]\([^)]*\)/g, "$1").replace(/https?:\/\/\S+/g, "")
      .replace(/[*_`~]+/g, "").replace(/<[^>]+>/g, "").replace(/\s+/g, " ").replace(/^[\s\-:]+|[\s\-:]+$/g, "");
  }
  function parse(r) {
    var tag = r.tag_name, name = (r.name || tag).trim() || tag, low = (name + " " + tag).toLowerCase();
    var stage = r.prerelease ? "Pre-release" : low.indexOf("hotfix") > -1 ? "Hotfix" : "Release", bl = [], pa = [];
    (r.body || "").replace(/\r/g, "").split("\n").forEach(function (l) {
      var s = l.trim(); if (!s || s[0] === "#" || /^[-=_* ]+$/.test(s)) return;
      var m = s.match(/^(?:[-*+]|\d+[.)])\s+(.*)/), t = clean(m ? m[1] : s);
      if (t.length < 3 || /^(full changelog|what'?s changed|new contributors)/i.test(t)) return;
      (m ? bl : pa).push(/[.!?]$/.test(t) ? t : t + ".");
    });
    var ch = (bl.length ? bl : pa).slice(0, 12); if (!ch.length) ch = ["No written notes were published for this release."];
    var lead = bl.length && pa.length ? pa[0] : ch.slice(0, 2).join(" ");
    return { version: name, date: (r.published_at || r.created_at || "").slice(0, 10), stage: stage, tag: tag,
      summary: lead.length <= 190 ? lead : lead.slice(0, 187).replace(/\s+\S*$/, "") + "…", changes: ch };
  }
  function entryHTML(r) {
    var a = slug("release-" + r.tag);
    return '<details class="release-entry" id="' + esc(a) + '" data-stage="' + esc(r.stage) + '"><summary><span><b>' + esc(r.version) +
      '</b><small>' + esc(r.date) + ' · ' + esc(r.stage) + '</small></span><span class="release-summary">' + esc(r.summary) + '</span></summary><ul>' +
      r.changes.map(function (c) { return "<li>" + esc(c) + "</li>"; }).join("") + '</ul><p class="release-source"><a href="' + TAGURL + esc(r.tag) + '">Official release notes</a></p></details>';
  }
  function getJSON(url, key, ttl) {
    try { var c = JSON.parse(sessionStorage.getItem(key) || "null"); if (c && Date.now() - c.t < ttl) return Promise.resolve(c.d); } catch (e) {}
    return fetch(url, { headers: { Accept: "application/vnd.github+json" } }).then(function (r) { if (!r.ok) throw 0; return r.json(); })
      .then(function (d) { try { sessionStorage.setItem(key, JSON.stringify({ t: Date.now(), d: d })); } catch (e) {} return d; });
  }
  function staticJSON(p) { return fetch(p, { cache: "no-cache" }).then(function (r) { return r.ok ? r.json() : []; }).catch(function () { return []; }); }
  function releases() {
    return Promise.all([staticJSON("assets/releases.json"), getJSON(API + "/releases?per_page=30", "dm2-rel", 6e5).catch(function () { return []; })]).then(function (x) {
      var by = {}; x[0].forEach(function (e) { by[e.tag] = e; });
      x[1].filter(function (r) { return !r.draft; }).forEach(function (r) { var e = parse(r); if (!by[e.tag] || !by[e.tag].curated) by[e.tag] = e; });
      return Object.keys(by).map(function (k) { return by[k]; }).sort(function (a, b) { return a.date < b.date ? 1 : a.date > b.date ? -1 : 0; });
    });
  }
  function commits() {
    return getJSON(API + "/commits?per_page=15", "dm2-com", 6e5).then(function (d) {
      return d.map(function (c) { return { sha: c.sha.slice(0, 7), url: c.html_url, msg: c.commit.message.split("\n")[0], date: c.commit.author.date.slice(0, 10), who: (c.author && c.author.login) || c.commit.author.name }; });
    }).catch(function () { return staticJSON("assets/commits.json"); });
  }

  // Changelog page: add any releases the static HTML doesn't have yet, plus the commit feed.
  var stableBox = $("#releases ~ .release-list, [data-live=stable]"), listS = document.querySelectorAll(".release-list");
  if (document.getElementById("releases") && listS.length >= 2) {
    releases().then(function (all) {
      all.forEach(function (r) {
        if (document.getElementById(slug("release-" + r.tag))) return;
        var box = listS[r.stage === "Pre-release" ? 1 : 0]; box.insertAdjacentHTML("afterbegin", entryHTML(r));
      });
    });
    var cb = $("#commit-feed");
    if (cb) commits().then(function (c) {
      cb.innerHTML = c.length ? c.map(function (x) {
        return '<li><a href="' + esc(x.url) + '"><code>' + esc(x.sha) + '</code> ' + esc(x.msg) + '</a><small>' + esc(x.date) + ' · ' + esc(x.who) + '</small></li>';
      }).join("") : "<li>Commit history could not be loaded. See GitHub.</li>";
    });
  }

})();
