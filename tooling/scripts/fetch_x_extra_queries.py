#!/usr/bin/env python3
from __future__ import annotations

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
    "site:x.com engineering manager standup status",
    "site:x.com standup waste engineering",
    "site:x.com status theater engineering team",
    "site:x.com jira slack github standup",
    "site:x.com async standup github slack",
    "site:x.com who owns this bug engineering",
    "site:x.com bug ownership engineering team",
    "site:x.com ownership unclear bug fix",
    "site:x.com context scattered slack engineering",
    "site:x.com context switch slack coding",
    "site:x.com context buried in slack thread engineering",
    "site:x.com decisions buried in slack engineering",
    "site:x.com decisions not written engineering team",
    "site:x.com had to jump on a call engineering",
    "site:x.com jump on a call to figure this out bug",
    "site:x.com project state unknown engineering manager",
    "site:x.com we dont know whats going on engineering team",
    "site:x.com things falling through cracks engineering",
    "site:x.com falling through cracks dev team",
    "site:x.com ticket stale engineering slack",
    "site:x.com jira stale tickets engineering",
    "site:x.com jira is useless engineering manager",
    "site:x.com waiting for review pr queue",
    "site:x.com pr confusion engineering team",
    "site:x.com review queue latency engineering",
    "site:x.com support incident context scattered",
    "site:x.com incident timeline slack thread engineering",
    "site:x.com handoff slack pr ticket engineering",
    "site:x.com no clear owner bug engineering",
    "site:x.com who owns fix engineering manager",
    "site:x.com founder cto slack jira github team",
    "site:x.com small dev team slack github context",
    "site:x.com engineering manager slack chaos",
    "site:x.com status meetings useless engineering",
    "site:x.com daily update repeat standup",
    "site:x.com same standup updates every day",
    "site:x.com blocked dependency standup",
    "site:x.com deployment blocked waiting review",
    "site:x.com too many tools slack jira notion github",
    "site:x.com where is context pr review",
]

STATUS_RE = re.compile(r"https://x\.com/([A-Za-z0-9_]+)/status/(\d+)")
DATE_RE = re.compile(r"\[\d{1,2}:\d{2}\s[AP]M · ([A-Za-z]{3} \d{1,2}, \d{4})\]\(")
TITLE_RE = re.compile(r'^# .* on X: "(.*)" / X$', re.MULTILINE)


def curl_text(url: str, timeout: int = 25) -> str:
    proc = subprocess.run(
        ["curl", "-L", "--max-time", str(timeout), "-A", "Mozilla/5.0", url],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout


def discover_links(query: str) -> list[str]:
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
    return sorted(links)


def hydrate(link: str) -> dict | None:
    m = STATUS_RE.search(link)
    if not m:
        return None
    author, sid = m.group(1), m.group(2)
    wrapped = f"https://r.jina.ai/http://x.com/{author}/status/{sid}"
    text = curl_text(wrapped, timeout=25)
    if not text or "Log in to X / X" in text:
        return None

    title = ""
    tm = TITLE_RE.search(text)
    if tm:
        title = re.sub(r"\s+", " ", tm.group(1)).strip()

    date_iso = None
    dm = DATE_RE.search(text)
    if dm:
        try:
            date_iso = dt.datetime.strptime(dm.group(1), "%b %d, %Y").date().isoformat()
        except ValueError:
            date_iso = None

    return {
        "url": f"https://x.com/{author}/status/{sid}",
        "author": author,
        "statusId": sid,
        "text": title,
        "dateIso": date_iso,
        "source": wrapped,
    }


def main() -> None:
    by_query: dict[str, list[str]] = {}
    all_links: list[str] = []

    for q in QUERIES:
        links = discover_links(q)
        by_query[q] = links
        all_links.extend(links[:12])
        time.sleep(0.35)

    unique_links = list(dict.fromkeys(all_links))

    posts: list[dict] = []
    with cf.ThreadPoolExecutor(max_workers=18) as ex:
        futures = [ex.submit(hydrate, link) for link in unique_links]
        for fut in cf.as_completed(futures):
            row = fut.result()
            if row:
                posts.append(row)

    payload = {
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "queries": QUERIES,
        "discovered": by_query,
        "counts": {
            "queries": len(QUERIES),
            "links": len(all_links),
            "unique": len(unique_links),
            "hydrated": len(posts),
        },
        "posts": posts,
    }

    out = Path("resources/threads/2026-04-03/x-links-extra-queries.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out), "counts": payload["counts"]}, indent=2))


if __name__ == "__main__":
    main()
