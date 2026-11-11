"""Shared release helpers: parse GitHub releases, merge into assets/releases.json, render changelog HTML."""
import html, json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JSON_PATH = os.path.join(ROOT, "assets", "releases.json")
REPO = "DragonMounts-Team/DragonMounts2-Bedrock"
RELEASE_URL = f"https://github.com/{REPO}/releases/tag/"

def esc(s): return html.escape(str(s), quote=True)

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def clean_md(t):
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"[*_`~]+", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"\s+", " ", t).strip(" -:\t")

def parse_release(r):
    """Turn one GitHub API release object into our entry format."""
    tag = r["tag_name"]
    name = (r.get("name") or tag).strip() or tag
    low = (name + " " + tag).lower()
    stage = "Pre-release" if r.get("prerelease") else "Hotfix" if "hotfix" in low else "Release"
    bullets, paras = [], []
    for line in (r.get("body") or "").replace("\r", "").split("\n"):
        s = line.strip()
        if not s or s.startswith("#") or set(s) <= set("-=_* "): continue
        m = re.match(r"^(?:[-*+]|\d+[.)])\s+(.*)", s)
        txt = clean_md(m.group(1) if m else s)
        if len(txt) < 3 or re.match(r"(?i)^(full changelog|what'?s changed|new contributors)", txt): continue
        (bullets if m else paras).append(txt if txt[-1] in ".!?" else txt + ".")
    changes = (bullets or paras)[:12] or ["No written notes were published for this release."]
    lead = paras[0] if bullets and paras else " ".join(changes[:2])
    summary = lead if len(lead) <= 190 else lead[:187].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return {"version": name, "date": (r.get("published_at") or r.get("created_at") or "")[:10],
            "stage": stage, "tag": tag, "summary": summary, "changes": changes}

def load():
    try:
        with open(JSON_PATH, encoding="utf8") as f: return json.load(f)
    except (OSError, ValueError): return []

def save(entries):
    with open(JSON_PATH, "w", encoding="utf8", newline="\n") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False); f.write("\n")

def merge(existing, fresh):
    """Entries marked curated=true are hand-written and never overwritten."""
    by_tag = {e["tag"]: e for e in existing}
    for e in fresh:
        old = by_tag.get(e["tag"])
        if old and old.get("curated"): continue
        by_tag[e["tag"]] = e
    return sorted(by_tag.values(), key=lambda e: (e["date"], e["tag"]), reverse=True)

def render(entries):
    """Returns (stable_html, prerelease_html, search_entries)."""
    stable, pre, search = [], [], []
    for r in entries:
        anchor = slug("release-" + r["tag"])
        changes = "".join(f"<li>{esc(c)}</li>" for c in r["changes"])
        item = (f'<details class="release-entry" id="{esc(anchor)}" data-stage="{esc(r["stage"])}">'
                f'<summary><span><b>{esc(r["version"])}</b><small>{esc(r["date"])} · {esc(r["stage"])}</small></span>'
                f'<span class="release-summary">{esc(r["summary"])}</span></summary><ul>{changes}</ul>'
                f'<p class="release-source"><a href="{RELEASE_URL}{esc(r["tag"])}">Official release notes</a></p></details>')
        (pre if r["stage"] == "Pre-release" else stable).append(item)
        search.append({"t": r["version"], "p": "changelog.html", "a": anchor, "k": "Release note", "x": r["summary"]})
    return "".join(stable), "".join(pre), search

def wrap(name, inner): return f"<!--{name}:start-->{inner}<!--{name}:end-->"
