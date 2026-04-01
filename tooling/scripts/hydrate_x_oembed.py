#!/usr/bin/env python3
"""Hydrate X post URLs via publish.twitter.com oEmbed endpoint."""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import html
import json
import re
import subprocess
import urllib.parse
from pathlib import Path

STATUS_RE = re.compile(r"https://x\.com/([A-Za-z0-9_]+)/status/(\d+)")
P_RE = re.compile(r"<p[^>]*>(.*?)</p>", re.DOTALL | re.IGNORECASE)
A_DATE_RE = re.compile(r">([A-Za-z]+\s+\d{1,2},\s+\d{4})</a>", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")


def curl_json(url: str, timeout: int = 20) -> dict | None:
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
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def extract_text_from_html(embed_html: str) -> str:
    m = P_RE.search(embed_html)
    if not m:
        return ""
    raw = m.group(1).replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
    stripped = TAG_RE.sub("", raw)
    return re.sub(r"\s+", " ", html.unescape(stripped)).strip()


def hydrate_one(link: str) -> dict | None:
    m = STATUS_RE.search(link)
    if not m:
        return None
    author = m.group(1)
    status_id = m.group(2)
    oembed_url = (
        "https://publish.twitter.com/oembed?omit_script=true&url="
        + urllib.parse.quote(link, safe="")
    )
    payload = curl_json(oembed_url, timeout=25)
    if not payload:
        return None
    embed_html = payload.get("html", "") or ""
    if not embed_html:
        return None

    text = extract_text_from_html(embed_html)
    date_label = None
    date_iso = None
    dm = A_DATE_RE.search(embed_html)
    if dm:
        date_label = dm.group(1)
        try:
            date_iso = dt.datetime.strptime(date_label, "%B %d, %Y").date().isoformat()
        except ValueError:
            date_iso = None

    return {
        "url": f"https://x.com/{author}/status/{status_id}",
        "author": author,
        "statusId": status_id,
        "authorName": payload.get("author_name", ""),
        "authorUrl": payload.get("author_url", ""),
        "text": text,
        "dateLabel": date_label,
        "dateIso": date_iso,
        "providerName": payload.get("provider_name", ""),
    }


def load_links_from_input(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    links: list[str] = []
    if isinstance(data, dict):
        discovered = data.get("discovered")
        if isinstance(discovered, dict):
            for arr in discovered.values():
                if isinstance(arr, list):
                    links.extend(str(x) for x in arr)
        posts = data.get("posts")
        if isinstance(posts, list):
            for item in posts:
                if isinstance(item, dict) and item.get("url"):
                    links.append(str(item["url"]))
    elif isinstance(data, list):
        links.extend(str(x) for x in data)
    out = []
    seen = set()
    for link in links:
        m = STATUS_RE.search(link)
        if not m:
            continue
        canonical = f"https://x.com/{m.group(1)}/status/{m.group(2)}"
        if canonical in seen:
            continue
        seen.add(canonical)
        out.append(canonical)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="JSON file with links/discovered map")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--max-links", type=int, default=160)
    args = ap.parse_args()

    links = load_links_from_input(Path(args.input))[: args.max_links]
    hydrated: list[dict] = []
    with cf.ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futures = {ex.submit(hydrate_one, link): link for link in links}
        for fut in cf.as_completed(futures):
            row = fut.result()
            if row:
                hydrated.append(row)

    payload = {
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": "publish.twitter.com/oembed",
        "counts": {"inputLinks": len(links), "hydrated": len(hydrated)},
        "posts": sorted(hydrated, key=lambda p: (p.get("dateIso") or "", p["url"]), reverse=True),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(out), "counts": payload["counts"]}, indent=2))


if __name__ == "__main__":
    main()
