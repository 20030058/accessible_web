"""Find SKILL.md files on GitHub via code search (one query per UI term) and download them.

GitHub code search returns at most 1000 results per query and allows ~10 requests/min,
so a full run takes roughly 20-40 minutes. Re-running skips queries already saved.

Usage: python3 scripts/download_github.py
Outputs (under data/raw/github/):
  hits/<term>.jsonl   raw search hits per query term
  index.jsonl         unique files (dedup by blob sha) with the terms that found them
  skills/<owner>__<repo>__<sha12>/SKILL.md
"""
import json
import re
import subprocess
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from common import DATA, UI_TERMS, http_get, log, read_jsonl, write_jsonl

OUT = DATA / "raw" / "github"
TOKEN = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
HDR = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}


def search(term):
    dest = OUT / "hits" / f"{re.sub(r'[^a-z0-9]+', '_', term.lower())}.jsonl"
    if dest.exists():
        return read_jsonl(dest)
    q = f'filename:SKILL.md "{term}"' if " " in term or "-" in term or "." in term else f"filename:SKILL.md {term}"
    hits, total = [], None
    for page in range(1, 11):
        url = "https://api.github.com/search/code?" + urllib.parse.urlencode({"q": q, "per_page": 100, "page": page})
        data = json.loads(http_get(url, HDR))
        total = data.get("total_count")
        for it in data["items"]:
            hits.append({"term": term, "repo": it["repository"]["full_name"], "path": it["path"],
                         "sha": it["sha"], "html_url": it["html_url"]})
        time.sleep(6.5)  # stay under 10 code-search requests/min
        if len(data["items"]) < 100:
            break
    write_jsonl(dest, hits)
    log("github", f'code search q={q}', len(hits), dest, f"total_count={total} (API caps at 1000)")
    print(f"{term!r}: {len(hits)} hits (total {total})", flush=True)
    return hits


def download(row):
    owner, repo = row["repo"].split("/", 1)
    dest = OUT / "skills" / f"{owner}__{repo}__{row['sha'][:12]}" / "SKILL.md"
    if dest.exists():
        return "cached"
    raw = row["html_url"].replace("https://github.com/", "https://raw.githubusercontent.com/", 1).replace("/blob/", "/", 1)
    try:
        body = http_get(raw)
    except Exception as e:  # noqa: BLE001
        return f"error: {e}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)
    return "ok"


def main():
    index = {}
    for term in UI_TERMS:
        for h in search(term):
            if h["path"].rsplit("/", 1)[-1] != "SKILL.md":
                continue
            row = index.setdefault(h["sha"], {k: h[k] for k in ("repo", "path", "sha", "html_url")} | {"terms": []})
            row["terms"].append(term)
    rows = list(index.values())
    write_jsonl(OUT / "index.jsonl", rows)
    log("github", "unique SKILL.md files across all UI queries (dedup by blob sha)", len(rows), OUT / "index.jsonl")

    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(download, rows))
    ok = sum(r in ("ok", "cached") for r in results)
    errors = [{"repo": r["repo"], "path": r["path"], "error": s} for r, s in zip(rows, results) if s.startswith("error")]
    write_jsonl(OUT / "download_errors.jsonl", errors)
    log("github", "SKILL.md downloaded", ok, OUT / "skills", f"errors={len(errors)} (download_errors.jsonl)")
    print(f"unique={len(rows)} downloaded={ok} errors={len(errors)}")


if __name__ == "__main__":
    main()
