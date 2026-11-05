"""Shared paths, UI keyword filter, HTTP helper and data-log writer for corpus scripts."""
import datetime as dt
import http.client
import json
import random
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LOG = DATA / "DATA_LOG.txt"

# Broad UI/frontend terms used to pick candidate skills. Precision is fixed later by the LLM filter.
UI_TERMS = [
    "ui", "ux", "frontend", "front-end", "front end", "web design", "web app", "website", "landing page",
    "css", "html", "tailwind", "react", "vue", "svelte", "angular", "next.js", "nextjs", "shadcn",
    "component", "design system", "figma", "responsive", "layout", "dashboard", "user interface",
    "accessibility", "a11y", "wcag", "aria",
]
_UI_RE = re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(t) for t in UI_TERMS) + r")(?![a-z0-9])", re.I)


def ui_terms_in(text: str) -> list[str]:
    return sorted({m.group(1).lower() for m in _UI_RE.finditer(text or "")})


def log(source: str, action: str, count: int | str, path: Path | str, notes: str = "") -> None:
    """Append one line per dataset event to data/DATA_LOG.txt."""
    DATA.mkdir(parents=True, exist_ok=True)
    rel = Path(path).relative_to(ROOT) if Path(path).is_absolute() else path
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with LOG.open("a") as f:
        f.write(f"{ts} | {source} | {action} | n={count} | {rel} | {notes}\n")


def http_get(url: str, headers: dict | None = None, retries: int = 6) -> bytes:
    """GET with Retry-After / jittered backoff on 429, 403 rate limits and 5xx."""
    h = {"User-Agent": "skills-a11y-research-corpus/0.1"} | (headers or {})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            retryable = e.code in (429, 500, 502, 503, 504) or (
                e.code == 403 and "rate limit" in e.read().decode(errors="ignore").lower())
            if not retryable or attempt == retries - 1:
                raise
            wait = float(e.headers.get("Retry-After") or e.headers.get("RateLimit-Reset") or 2 ** attempt * 5)
            time.sleep(wait + random.uniform(0, 2))
        except (urllib.error.URLError, TimeoutError, http.client.IncompleteRead, ConnectionError):
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt + random.uniform(0, 1))
    raise RuntimeError("unreachable")


def write_jsonl(path: Path, rows) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
    return n


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
