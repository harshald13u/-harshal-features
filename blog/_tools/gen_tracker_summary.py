#!/usr/bin/env python3
"""Generate /tracker-summary.json from the tracker's EMBEDDED_SNAPSHOT_ROWS so the
homepage can fetch a tiny file instead of the full ~600KB dashboard HTML, AND keep the
hardcoded count fallback in index.html + hi/index.html in sync with the live data.

Replicates the homepage's syncTracker() logic exactly (unique-link count, e-paper count,
latest 3). The homepage also self-heals at runtime by fetching the (cache-busted) dashboard,
so the displayed number is always correct even if this script is not re-run; running this
just keeps the instant-paint summary and the no-JS fallback current.

Run this whenever the tracker data changes:  python3 blog/_tools/gen_tracker_summary.py
"""
import os, re, json, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC  = os.path.join(ROOT, "Harshal_Dasani_Dashboard.html")
OUT  = os.path.join(ROOT, "tracker-summary.json")
FALLBACK_FILES = [os.path.join(ROOT, "index.html"), os.path.join(ROOT, "hi", "index.html")]

def canon(u):
    u = (u or "").strip().lower()
    u = re.sub(r'^https?://', '', u)
    u = re.sub(r'^(www\.|m\.|amp\.)', '', u)
    u = re.sub(r'/+$', '', u)
    u = re.sub(r'\.+$', '', u)
    return u.split('#')[0]

EP = re.compile(r'news\s?paper|\bepaper\b|e[\s-]?paper|magazine|\bedition\b|\.pdf$|'
                r'true point news|outlook business december|outlook business november|'
                r'wall street cn|stcn article|bhopal english edition|cn article|detailnews|\.shtml', re.I)

def parse_date(v):
    s = (v or "").strip()
    for fmt in ("%Y-%m-%d","%Y-%m-%dT%H:%M:%S","%d %b %Y","%d %B %Y","%b %d, %Y",
                "%B %d, %Y","%d-%m-%Y","%m/%d/%Y","%d/%m/%Y","%Y/%m/%d"):
        try: return datetime.datetime.strptime(s, fmt)
        except Exception: pass
    return datetime.datetime.min

# Defensive: only rewrite the trackerCount fallback when EXACTLY one match is found.
FALLBACK_RE = re.compile(
    r'(id="trackerCount"\s+data-target=")\d+("\s+aria-label=")[\d,]+( unique feature links")')

def sync_fallback(path, n):
    if not os.path.exists(path):
        print(f"  fallback skip (missing): {path}"); return
    html = open(path, encoding="utf-8").read()
    matches = FALLBACK_RE.findall(html)
    if len(matches) != 1:
        print(f"  fallback skip ({len(matches)} matches, expected 1): {path}"); return
    new = FALLBACK_RE.sub(lambda m: f"{m.group(1)}{n}{m.group(2)}{n:,}{m.group(3)}", html)
    if new != html:
        open(path, "w", encoding="utf-8").write(new)
        print(f"  fallback synced -> {n:,}: {os.path.relpath(path, ROOT)}")
    else:
        print(f"  fallback already current ({n:,}): {os.path.relpath(path, ROOT)}")

def main():
    html = open(SRC, encoding="utf-8").read()
    m = re.search(r'EMBEDDED_SNAPSHOT_ROWS\s*=\s*(\[[\s\S]*?\])\s*;', html)
    if not m:
        raise SystemExit("EMBEDDED_SNAPSHOT_ROWS not found in dashboard")
    rows = json.loads(m.group(1))
    seen, n = set(), 0
    for r in rows:
        c = canon(r.get("Link"))
        if c and c not in seen:
            seen.add(c); n += 1
    ep = sum(1 for r in rows if EP.search(str(r.get("Heading") or "")))
    cand = [r for r in rows if r.get("Heading") and r.get("Link")]
    cand.sort(key=lambda r: parse_date(r.get("Date")), reverse=True)
    latest = [{k: r.get(k) for k in ("Heading","Link","Topic","Publication","Date")}
              for r in cand[:3]]
    out = {"count": n, "epaper": ep, "latest": latest,
           "generated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {OUT}: count={n} epaper={ep} latest={len(latest)} bytes={os.path.getsize(OUT)}")
    for fp in FALLBACK_FILES:
        sync_fallback(fp, n)

if __name__ == "__main__":
    main()
