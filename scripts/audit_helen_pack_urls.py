"""Audit URLs in the Helen pack — checks HTTP status of every external URL
cited in the HTML docs and the skill markdown files.

Outputs a report grouped by status:
  - 200 OK (good)
  - 3xx redirects (target URL shown)
  - 404 not found (broken)
  - other errors (timeout, SSL, DNS, etc.)

Usage:
    python3 scripts/audit_helen_pack_urls.py

Requires: requests (pip install requests)
"""

from __future__ import annotations

import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("ERROR: this script requires 'requests'. Install with:")
    print("  python3 -m pip install --user requests")
    sys.exit(1)


REPO = Path(__file__).resolve().parents[1]

FILES = [
    REPO / "helen-pack" / "00-indice.html",
    REPO / "helen-pack" / "01-deck-difusion.html",
    REPO / "helen-pack" / "02-casos-estudio.html",
    REPO / "helen-pack" / "03-independencia.html",
    REPO / "helen-pack" / "04-directoras.html",
    REPO / ".claude" / "skills" / "creative-direction" / "SKILL.md",
    REPO / ".claude" / "skills" / "creative-direction" / "SOURCES.md",
]

# Regex to capture http/https URLs from HTML href + markdown links + bare URLs
URL_RE = re.compile(
    r'https?://[^\s<>"\')]+',
    re.IGNORECASE,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es,en;q=0.9",
}

TIMEOUT = 15
DELAY = 0.3   # polite delay between requests


def collect_urls() -> dict[str, list[Path]]:
    """Return {url: [files where it appears]}."""
    seen: dict[str, list[Path]] = defaultdict(list)
    for f in FILES:
        if not f.exists():
            print(f"  WARN: missing file {f}", file=sys.stderr)
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        urls = URL_RE.findall(text)
        for raw in urls:
            # Strip trailing punctuation, but keep balanced parens in URL
            # (e.g. Wikipedia disambiguators like "Lemonade_(album)").
            url = raw.rstrip('.,;:!?"\'')
            # Only strip a trailing ")" if there's no matching "(" inside the URL.
            while url.endswith(')') and url.count('(') < url.count(')'):
                url = url[:-1]
            seen[url].append(f.relative_to(REPO))
    return seen


def check(url: str) -> tuple[int | str, str | None]:
    """Return (status_or_error_str, final_url_if_redirected)."""
    try:
        # Try HEAD first (lighter); fall back to GET if server doesn't allow.
        r = requests.head(
            url, headers=HEADERS, timeout=TIMEOUT,
            allow_redirects=True,
        )
        if r.status_code in (405, 403, 400):
            r = requests.get(
                url, headers=HEADERS, timeout=TIMEOUT,
                allow_redirects=True, stream=True,
            )
            r.close()
        final = r.url if r.url != url else None
        return r.status_code, final
    except requests.exceptions.SSLError as e:
        return f"SSL_ERROR ({type(e).__name__})", None
    except requests.exceptions.ConnectionError:
        return "CONNECTION_ERROR", None
    except requests.exceptions.Timeout:
        return "TIMEOUT", None
    except requests.exceptions.TooManyRedirects:
        return "TOO_MANY_REDIRECTS", None
    except Exception as e:
        return f"ERROR ({type(e).__name__})", None


def main() -> int:
    print("=" * 70)
    print("Helen-pack URL audit")
    print("=" * 70)

    urls = collect_urls()
    total = len(urls)
    print(f"\nFound {total} unique URLs across {len(FILES)} files.\n")

    results: dict[str, list[tuple[str, str | None, list[Path]]]] = defaultdict(list)

    for i, (url, files) in enumerate(sorted(urls.items()), 1):
        domain = urlparse(url).netloc
        status, final = check(url)
        bucket = classify(status)
        results[bucket].append((url, final, files))
        marker = mark(bucket)
        print(f"  [{i:3d}/{total}] {marker} {status:<25} {domain}")
        time.sleep(DELAY)

    print("\n" + "=" * 70)
    print("REPORT")
    print("=" * 70)

    for bucket in ("OK", "REDIRECT", "404", "OTHER_ERROR"):
        items = results.get(bucket, [])
        if not items:
            continue
        print(f"\n## {bucket} — {len(items)} URLs")
        print("-" * 70)
        for url, final, files in items:
            file_list = ", ".join(str(f) for f in files)
            line = f"  {url}"
            if final and final != url:
                line += f"\n    → redirects to: {final}"
            line += f"\n    in: {file_list}"
            print(line)

    print("\n" + "=" * 70)
    summary = {k: len(v) for k, v in results.items()}
    print(f"SUMMARY: {summary}")
    print("=" * 70)

    return 0 if not (results.get("404") or results.get("OTHER_ERROR")) else 1


def classify(status) -> str:
    if isinstance(status, int):
        if 200 <= status < 300:
            return "OK"
        if 300 <= status < 400:
            return "REDIRECT"
        if status == 404:
            return "404"
        return "OTHER_ERROR"
    return "OTHER_ERROR"


def mark(bucket: str) -> str:
    return {
        "OK": "✓",
        "REDIRECT": "→",
        "404": "✗",
        "OTHER_ERROR": "!",
    }.get(bucket, "?")


if __name__ == "__main__":
    sys.exit(main())
