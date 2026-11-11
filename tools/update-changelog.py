#!/usr/bin/env python3
"""
Refreshes the changelog from GitHub Releases. Runs daily in CI (.github/workflows/changelog.yml)
and from the local editor's "Update changelog" button. Safe to run by hand:

    python3 tools/update-changelog.py            # fetch + rewrite
    python3 tools/update-changelog.py --dry-run  # show what would change
    python3 tools/update-changelog.py --from-file releases-api.json   # offline test

Hand-edit an entry in assets/releases.json and add  "curated": true  to stop it being overwritten.
Only changelog.html (release lists) and the Release-note rows of assets/data.js are touched.
"""
import argparse, json, os, re, sys, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
import releases as R

ap = argparse.ArgumentParser()
ap.add_argument("--dry-run", action="store_true")
ap.add_argument("--from-file")
args = ap.parse_args()

def fetch():
    out, page = [], 1
    while True:
        req = urllib.request.Request(f"https://api.github.com/repos/{R.REPO}/releases?per_page=100&page={page}",
                                     headers={"Accept": "application/vnd.github+json", "User-Agent": "dm2-wiki-changelog"})
        tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if tok: req.add_header("Authorization", "Bearer " + tok)
        with urllib.request.urlopen(req, timeout=30) as resp: batch = json.load(resp)
        out += batch
        if len(batch) < 100: return out
        page += 1

try:
    raw = json.load(open(args.from_file, encoding="utf8")) if args.from_file else fetch()
except Exception as ex:
    print(f"Could not reach GitHub ({ex}); changelog left unchanged."); sys.exit(0)

fresh = [R.parse_release(r) for r in raw if not r.get("draft")]
entries = R.merge(R.load(), fresh)
stable, pre, search = R.render(entries)

def patch(text, name, inner):
    pat = re.compile(rf"<!--{name}:start-->.*?<!--{name}:end-->", re.S)
    if not pat.search(text): raise SystemExit(f"Marker {name} missing from changelog.html; run tools/build.py once.")
    return pat.sub(lambda m: R.wrap(name, inner), text)

changed = []
path = os.path.join(R.ROOT, "changelog.html")
page = open(path, encoding="utf8", newline="").read()
nl = "\r\n" if "\r\n" in page else "\n"
new = patch(patch(page, "releases", f'<div class="release-list">{stable}</div>'), "prereleases", f'<div class="release-list">{pre}</div>')
if new != page: changed.append("changelog.html")

dpath = os.path.join(R.ROOT, "assets", "data.js")
data = open(dpath, encoding="utf8", newline="").read()
m = re.match(r"window\.DM_INDEX=(.*?);\s*$", data, re.S)
idx = [e for e in json.loads(m.group(1)) if e.get("k") != "Release note"] + search
newdata = "window.DM_INDEX=" + json.dumps(idx, ensure_ascii=False) + ";" + nl
if newdata != data: changed.append("assets/data.js")

before = R.load()
if before != entries: changed.append("assets/releases.json")
print(f"{len(entries)} releases ({len(fresh)} fetched). Changed: {', '.join(changed) or 'nothing'}")
if args.dry_run or not changed: sys.exit(0)
R.save(entries)
open(path, "w", encoding="utf8", newline="").write(new)
open(dpath, "w", encoding="utf8", newline="").write(newdata)
