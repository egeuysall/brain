#!/usr/bin/env python3
"""Quickly discover and hydrate X posts via r.jina.ai using bounded concurrency."""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import re
import subprocess
import time
import urllib.parse
from pathlib import Path


QUERIES = [
    "site:x.com standup slack status",
    "site:x.com engineering standup status",
    "site:x.com jira slack github standup",
    "site:x.com who owns this bug engineering",
    "site:x.com bug ownership engineering team",
    "site:x.com context scattered slack engineering",
    "site:x.com had to jump on a call engineering",
    "site:x.com pull request review context switch",
    "site:x.com incident timeline slack thread",
    "site:x.com startup engineering standup jira",
    "site:x.com dev team standup daily update",
    "site:x.com engineering manager status update",
    "site:x.com async standup github slack jira",
    "site:x.com ticket stale slack thread",
    "site:x.com ownership unclear bug fix",
    "site:x.com review blocked waiting pr",
    "site:x.com decisions buried in slack engineering",
    "site:x.com status theater engineering",
    "site:x.com project state unknown engineering manager",
]

STATUS_RE = re.compile(r"https://x\.com/([A-Za-z0-9_]+)/status/(\d+)")
DATE_RE = re.compile(r"\[\d{1,2}:\d{2}\s[AP]M · ([A-Za-z]{3} \d{1,2}, \d{4})\]\(")
TITLE_RE = re.compile(r'^# .* on X: "(.*)" / X$', re.MULTILINE)


def curl_text(url: str, timeout: int = 20) -> str:
    cmd = [
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
    ]
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        return ""
    return proc.stdout


def discover_links(query: str, max_links: int) -> list[str]:
    url = "https://r.jina.ai/http://duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    text = curl_text(url, timeout=25)
    if not text:
        return []

    links: set[str] = set(re.findall(r"https://x\.com/[A-Za-z0-9_]+/status/\d+", text))
    for enc in re.findall(r"uddg=([^&\s)]+)", text):
        dec = urllib.parse.unquote(enc)
        m = re.search(r"https://x\.com/[A-Za-z0-9_]+/status/\d+", dec)
        if m:
            links.add(m.group(0))
    return list(sorted(links))[:max_links]


def parse_post(link: str) -> dict | None:
    wrapped = "https://r.jina.ai/http://" + link.replace("https://", "")
    text = curl_text(wrapped, timeout=25)
    if not text or "Log in to X / X" in text:
        return None
    m = STATUS_RE.search(link)
    if not m:
        return None
    author, status_id = m.group(1), m.group(2)

    title = ""
    tm = TITLE_RE.search(text)
    if tm:
        title = re.sub(r"\s+", " ", tm.group(1)).strip()

    date_label = None
    date_iso = None
    dm = DATE_RE.search(text)
    if dm:
        date_label = dm.group(1)
        try:
            date_iso = dt.datetime.strptime(date_label, "%b %d, %Y").date().isoformat()
        except ValueError:
            date_iso = None

    return {
        "url": f"https://x.com/{author}/status/{status_id}",
        "author": author,
        "statusId": status_id,
        "text": title,
        "dateLabel": date_label,
        "dateIso": date_iso,
        "source": wrapped,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-links-per-query", type=int, default=8)
    ap.add_argument("--max-hydrate", type=int, default=120)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    discovered: dict[str, list[str]] = {}
    all_links: list[str] = []
    for q in QUERIES:
        links = discover_links(q, args.max_links_per_query)
        discovered[q] = links
        all_links.extend(links)
        time.sleep(0.6)

    unique_links = list(dict.fromkeys(all_links))[: args.max_hydrate]
    hydrated: list[dict] = []
    with cf.ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futures = {ex.submit(parse_post, link): link for link in unique_links}
        for fut in cf.as_completed(futures):
            post = fut.result()
            if post:
                hydrated.append(post)

    payload = {
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": "duckduckgo_via_r_jina + x_status_via_r_jina",
        "queries": QUERIES,
        "counts": {
            "queryCount": len(QUERIES),
            "discoveredLinks": len(all_links),
            "uniqueLinks": len(unique_links),
            "hydratedPosts": len(hydrated),
        },
        "discovered": discovered,
        "posts": hydrated,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out), "counts": payload["counts"]}, indent=2))


if __name__ == "__main__":
    main()
