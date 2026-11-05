"""Download the ClawHub skill catalog, select UI candidates by keyword, and fetch their SKILL.md.

Usage: python3 scripts/download_clawhub.py [--skip-catalog]
Outputs (under data/raw/clawhub/):
  catalog.jsonl     every public skill's metadata (one row per skill)
  candidates.jsonl  catalog rows whose name/summary/tags match a UI term (+ matched terms)
  skills/<owner>__<slug>/SKILL.md
"""
import json
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from common import DATA, http_get, log, read_jsonl, ui_terms_in, write_jsonl

BASE = "https://clawhub.ai/api/v1"
OUT = DATA / "raw" / "clawhub"


def fetch_catalog():
    cursor, n = None, 0
    while True:
        q = {"limit": 200, "sort": "name"} | ({"cursor": cursor} if cursor else {})
        page = json.loads(http_get(f"{BASE}/skills?{urllib.parse.urlencode(q)}"))
        for item in page["items"]:
            n += 1
            yield item
        cursor = page.get("nextCursor")
        print(f"\rcatalog: {n}", end="", flush=True)
        if not cursor:
            print()
            return
        time.sleep(0.1)


def fetch_skill_md(row):
    dest = OUT / "skills" / f"{row['ownerHandle']}__{row['slug']}" / "SKILL.md"
    if dest.exists():
        return "cached"
    q = urllib.parse.urlencode({"path": "SKILL.md", "version": row["latestVersion"]["version"]})
    try:
        body = http_get(f"{BASE}/skills/{urllib.parse.quote(row['slug'])}/file?{q}")
    except Exception as e:  # noqa: BLE001 - record and continue
        return f"error: {e}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)
    return "ok"


def main():
    catalog = OUT / "catalog.jsonl"
    if "--skip-catalog" not in sys.argv or not catalog.exists():
        n = write_jsonl(catalog, fetch_catalog())
        log("clawhub", "catalog (all public skills, metadata only)", n, catalog, f"{BASE}/skills sort=name")

    rows = read_jsonl(catalog)
    cands = []
    for r in rows:
        tags = " ".join(k for k in (r.get("tags") or {}) if k != "latest")
        terms = ui_terms_in(" ".join(filter(None, [r["slug"], r.get("displayName"), r.get("summary"), tags])))
        if terms and r.get("latestVersion"):
            cands.append(r | {"ui_terms": terms})
    cpath = OUT / "candidates.jsonl"
    write_jsonl(cpath, cands)
    log("clawhub", "UI keyword candidates (slug/name/summary/tags)", len(cands), cpath, "terms=scripts/common.py UI_TERMS")

    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(fetch_skill_md, cands))
    ok = sum(r in ("ok", "cached") for r in results)
    errors = [(c["slug"], r) for c, r in zip(cands, results) if r.startswith("error")]
    write_jsonl(OUT / "download_errors.jsonl", ({"slug": s, "error": e} for s, e in errors))
    log("clawhub", "SKILL.md downloaded for candidates", ok, OUT / "skills", f"errors={len(errors)} (download_errors.jsonl)")
    print(f"candidates={len(cands)} downloaded={ok} errors={len(errors)}")


if __name__ == "__main__":
    main()
