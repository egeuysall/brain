#!/usr/bin/env python3
"""Fetch X post candidates via DuckDuckGo through r.jina.ai, then hydrate posts via r.jina.ai/x.com."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_QUERIES = [
    "site:x.com standup waste engineering team status",
    "site:x.com engineering manager slack chaos status",
    "site:x.com PR confusion review context status",
    "site:x.com who owns this bug status",
    "site:x.com had to jump on a call to figure this out status",
    "site:x.com context is scattered in slack status",
    "site:x.com jira is useless engineering status",
    "site:x.com things falling through cracks engineering status",
    "site:x.com standup status theater engineering manager",
    "site:x.com decisions buried in slack engineering team",
]

STATUS_RE = re.compile(r"https://x\.com/([A-Za-z0-9_]+)/status/(\d+)")
DATE_RE = re.compile(r"\[\d{1,2}:\d{2}\s[AP]M · ([A-Za-z]{3} \d{1,2}, \d{4})\]\(")
TITLE_QUOTE_RE = re.compile(r'^# .* on X: "(.*)" / X$', re.MULTILINE)


@dataclass
class Post:
    query: str
    url: str
    author: str
    status_id: str
    timestamp_label: str | None
    date_iso: str | None
    text: str
    source: str


def fetch_text(url: str, timeout: int = 30, retries: int = 5) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        },
    )
    delay = 1.0
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(delay)
                delay *= 2
                continue
            raise
        except urllib.error.URLError:
            last_err = None
            if attempt < retries:
                time.sleep(delay)
                delay *= 2
                continue
            break

    # Curl fallback is often more resilient with DDG + r.jina.ai.
    proc = subprocess.run(
        [
            "curl",
            "-L",
            "--max-time",
            str(timeout),
            "-A",
            (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            url,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout

    if last_err:
        raise last_err
    raise RuntimeError(f"Failed to fetch URL after retries: {url}")


def ddg_search_links(query: str) -> list[str]:
    url = "https://r.jina.ai/http://duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    try:
        text = fetch_text(url)
    except Exception:
        return []
    urls: set[str] = set()
    for match in STATUS_RE.findall(text):
        urls.add(f"https://x.com/{match[0]}/status/{match[1]}")

    # Also parse encoded uddg links if present.
    for encoded in re.findall(r"uddg=([^&\s)]+)", text):
        decoded = urllib.parse.unquote(encoded)
        m = STATUS_RE.search(decoded)
        if m:
            urls.add(f"https://x.com/{m.group(1)}/status/{m.group(2)}")
    return sorted(urls)


def parse_date(markdown: str) -> tuple[str | None, str | None]:
    m = DATE_RE.search(markdown)
    if not m:
        return None, None
    label = m.group(1)
    try:
        parsed = dt.datetime.strptime(label, "%b %d, %Y").date().isoformat()
    except ValueError:
        return label, None
    return label, parsed


def parse_text(markdown: str) -> str:
    title_match = TITLE_QUOTE_RE.search(markdown)
    if title_match:
        return re.sub(r"\s+", " ", title_match.group(1)).strip()

    # Fallback: capture paragraph right after handle line
    lines = [line.strip() for line in markdown.splitlines()]
    for idx, line in enumerate(lines):
        if line.startswith("@") and idx + 1 < len(lines):
            candidate = lines[idx + 1].strip()
            if candidate and not candidate.startswith("[") and len(candidate) > 20:
                return re.sub(r"\s+", " ", candidate).strip()
    return ""


def hydrate_post(query: str, url: str) -> Post | None:
    m = STATUS_RE.search(url)
    if not m:
        return None
    author, status_id = m.group(1), m.group(2)
    wrapped = "https://r.jina.ai/http://x.com/" + f"{author}/status/{status_id}"
    try:
        markdown = fetch_text(wrapped)
    except Exception:
        return None

    if "Log in to X / X" in markdown:
        return None

    timestamp_label, date_iso = parse_date(markdown)
    text = parse_text(markdown)
    return Post(
        query=query,
        url=f"https://x.com/{author}/status/{status_id}",
        author=author,
        status_id=status_id,
        timestamp_label=timestamp_label,
        date_iso=date_iso,
        text=text,
        source=wrapped,
    )


def load_queries(arg: str | None) -> list[str]:
    if not arg:
        return DEFAULT_QUERIES
    return [q.strip() for q in arg.split(",") if q.strip()]


def within_window(date_iso: str | None, start_date: dt.date, end_date: dt.date) -> bool:
    if not date_iso:
        return False
    try:
        d = dt.date.fromisoformat(date_iso)
    except ValueError:
        return False
    return start_date <= d <= end_date


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--queries")
    parser.add_argument("--max-links-per-query", type=int, default=20)
    parser.add_argument("--max-hydrated", type=int, default=200)
    parser.add_argument("--sleep-ms", type=int, default=250)
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()

    queries = load_queries(args.queries)
    today = dt.date.today()
    start_date = today - dt.timedelta(days=max(args.days, 1))

    per_query_links: dict[str, list[str]] = {}
    all_links: list[tuple[str, str]] = []
    for query in queries:
        links = ddg_search_links(query)[: args.max_links_per_query]
        per_query_links[query] = links
        all_links.extend((query, link) for link in links)
        time.sleep(args.sleep_ms / 1000)

    seen: set[str] = set()
    hydrated: list[Post] = []
    for query, link in all_links:
        if link in seen:
            continue
        seen.add(link)
        post = hydrate_post(query, link)
        if post:
            hydrated.append(post)
        if len(hydrated) >= args.max_hydrated:
            break
        time.sleep(args.sleep_ms / 1000)

    in_window = [
        p for p in hydrated if within_window(p.date_iso, start_date=start_date, end_date=today)
    ]

    payload = {
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": "ddg_via_r_jina_ai + x_page_via_r_jina_ai",
        "daysWindow": args.days,
        "queries": queries,
        "perQueryLinks": per_query_links,
        "counts": {
            "queries": len(queries),
            "rawLinks": len(all_links),
            "uniqueLinks": len(seen),
            "hydrated": len(hydrated),
            "inWindow": len(in_window),
        },
        "posts": [asdict(p) for p in hydrated],
        "postsInWindow": [asdict(p) for p in in_window],
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out_path), "counts": payload["counts"]}, indent=2))


if __name__ == "__main__":
    main()
