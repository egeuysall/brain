#!/usr/bin/env python3
"""Harvest Reddit posts safely for research workflows.

Design goals:
- Prefer `old.reddit.com/r/<sub>/new/` HTML listings to avoid JSON instability.
- Parse post metadata and filter by age window (default 48-72h).
- Optionally fetch OP body text for higher-signal screening.
- Fail closed on network and parse errors where appropriate.

Security defaults:
- HTTPS-only fetches.
- User-agent required.
- Max bytes guardrail.
- Throttled requests and bounded retries.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_SUBREDDITS = [
    "EngineeringManagers",
    "ExperiencedDevs",
    "ProductManagement",
    "projectmanagement",
    "devops",
    "managers",
]

FIRST_PERSON_RE = re.compile(r"\b(i|we|our|my|us)\b", re.IGNORECASE)
PAIN_RE = re.compile(
    r"\b(frustrat|stuck|confus|waste|slip|miss|chaos|hard|overwhelm|late|"
    r"not working|doesn.t work|break another|moved on|blocked|bottleneck|"
    r"pointing fingers|can.t keep up|rework)\b",
    re.IGNORECASE,
)
COORD_RE = re.compile(
    r"\b(slack|jira|standup|async|context|alignment|misalign|handoff|"
    r"coordination|communication|status|owner|follow[- ]?up|meeting)\b",
    re.IGNORECASE,
)
PROMO_RE = re.compile(r"\b(i built|would you use|first report.?s free|sign up|demo)\b", re.IGNORECASE)

TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


class HarvestError(Exception):
    """Raised when harvest should fail closed."""


@dataclass
class Candidate:
    subreddit: str
    title: str
    url: str
    created_at: str
    age_hours: float
    age_label: str
    author: str
    op_body: str
    first_person: bool
    pain_signal: bool
    coordination_signal: bool
    promotional_signal: bool
    high_signal_score: int
    high_signal: bool


def ensure_https(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise HarvestError(f"Refusing non-HTTPS URL: {url}")


def normalize_url_for_request(url: str) -> str:
    """Encode non-ASCII URL parts to keep urllib/http.client requests safe."""
    return urllib.parse.quote(url, safe=":/?&=%#")


def parse_iso8601(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value)
    except ValueError as exc:
        raise HarvestError(f"Invalid datetime: {value}") from exc
    if dt.tzinfo is None:
        raise HarvestError(f"Datetime missing timezone: {value}")
    return dt.astimezone(timezone.utc)


def strip_tags_to_text(raw_html: str) -> str:
    text = TAG_RE.sub(" ", raw_html)
    text = html.unescape(text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


def fetch_text(url: str, timeout_seconds: int, max_bytes: int, user_agent: str, retries: int = 2) -> str:
    ensure_https(url)
    request_url = normalize_url_for_request(url)
    req = urllib.request.Request(
        request_url,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        },
        method="GET",
    )

    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                status = resp.getcode()
                if status == 429:
                    retry_after = resp.headers.get("Retry-After")
                    wait_seconds = float(retry_after) if retry_after else (2.0 * (attempt + 1))
                    time.sleep(min(wait_seconds, 15.0))
                    continue
                if status != 200:
                    raise HarvestError(f"Unexpected HTTP status {status} for {url}")
                body = resp.read(max_bytes + 1)
                if len(body) > max_bytes:
                    raise HarvestError(f"Response too large for {url} (>{max_bytes} bytes)")
                return body.decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < retries:
                wait_seconds = float(exc.headers.get("Retry-After", 2 * (attempt + 1)))
                time.sleep(min(wait_seconds, 15.0))
                last_exc = exc
                continue
            last_exc = exc
        except urllib.error.URLError as exc:
            last_exc = exc
        if attempt < retries:
            time.sleep(min(2.0 * (attempt + 1), 10.0))

    raise HarvestError(f"Failed to fetch {url}: {last_exc}")


def fetch_text_with_curl(url: str, timeout_seconds: int, max_bytes: int, user_agent: str) -> str:
    """Fallback fetch path for environments where urllib gets blocked.

    Uses curl with explicit user-agent and timeout and applies the same
    size guardrail.
    """

    ensure_https(url)
    request_url = normalize_url_for_request(url)
    result = subprocess.run(
        [
            "curl",
            "-sL",
            "--max-time",
            str(timeout_seconds),
            "-A",
            user_agent,
            request_url,
        ],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        stderr_text = result.stderr.decode("utf-8", errors="replace").strip()
        raise HarvestError(f"curl fetch failed for {url}: {stderr_text or result.returncode}")
    if len(result.stdout) > max_bytes:
        raise HarvestError(f"Response too large for {url} (>{max_bytes} bytes)")
    return result.stdout.decode("utf-8", errors="replace")


def extract_posts_from_new_html(page_html: str, subreddit_hint: str) -> list[dict[str, str]]:
    parts = page_html.split('<div class=" thing id-t3_')
    if len(parts) <= 1:
        return []

    posts: list[dict[str, str]] = []
    for fragment in parts[1:]:
        chunk = '<div class=" thing id-t3_' + fragment
        permalink_m = re.search(r'data-permalink="([^"]+)"', chunk)
        title_m = re.search(r'<a class="title[^\"]*"[^>]*>(.*?)</a>', chunk, re.DOTALL)
        dt_m = re.search(r'<time[^>]*datetime="([^"]+)"[^>]*>(.*?)</time>', chunk, re.DOTALL)
        author_m = re.search(r'class="author[^\"]*"[^>]*>([^<]+)</a>', chunk)
        sub_m = re.search(r'data-subreddit="([^"]+)"', chunk)

        if not (permalink_m and title_m and dt_m):
            continue

        permalink = permalink_m.group(1)
        title = strip_tags_to_text(title_m.group(1))
        created_at = dt_m.group(1).strip()
        age_label = strip_tags_to_text(dt_m.group(2))
        author = author_m.group(1).strip() if author_m else "unknown"
        subreddit = sub_m.group(1).strip() if sub_m else subreddit_hint

        url = permalink if permalink.startswith("https://") else f"https://www.reddit.com{permalink}"
        posts.append(
            {
                "subreddit": subreddit,
                "title": title,
                "url": url,
                "created_at": created_at,
                "age_label": age_label,
                "author": author,
            }
        )
    return posts


def extract_op_body_from_post_html(post_html: str) -> str:
    split_marker = '<div class=" thing id-t3_'
    if split_marker not in post_html:
        return ""

    first_thing = split_marker + post_html.split(split_marker, 1)[1]
    if '<div class="child"' in first_thing:
        first_thing = first_thing.split('<div class="child"', 1)[0]

    body_m = re.search(
        r'<div class="usertext-body[^\"]*">\s*<div class="md">(.*?)</div>\s*</div>',
        first_thing,
        re.DOTALL,
    )
    if not body_m:
        # Fallback for pages where OP text is not rendered in legacy body blocks.
        og_desc_m = re.search(
            r'<meta[^>]+property="og:description"[^>]+content="([^"]+)"',
            post_html,
            re.IGNORECASE,
        )
        if og_desc_m:
            return strip_tags_to_text(og_desc_m.group(1))
        meta_desc_m = re.search(
            r'<meta[^>]+name="description"[^>]+content="([^"]+)"',
            post_html,
            re.IGNORECASE,
        )
        if meta_desc_m:
            return strip_tags_to_text(meta_desc_m.group(1))
        return ""

    return strip_tags_to_text(body_m.group(1))


def score_candidate(title: str, body: str) -> tuple[int, dict[str, bool]]:
    text = f"{title} {body}".strip()
    first_person = bool(FIRST_PERSON_RE.search(text))
    pain_signal = bool(PAIN_RE.search(text))
    coordination_signal = bool(COORD_RE.search(text))
    promotional_signal = bool(PROMO_RE.search(text))

    score = 0
    if first_person:
        score += 2
    if pain_signal:
        score += 2
    if coordination_signal:
        score += 1
    if promotional_signal:
        score -= 3

    return score, {
        "first_person": first_person,
        "pain_signal": pain_signal,
        "coordination_signal": coordination_signal,
        "promotional_signal": promotional_signal,
    }


def parse_term_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip().lower() for item in value.split(",") if item.strip()]


def matches_text_filters(text: str, include_any: list[str], exclude_any: list[str]) -> bool:
    haystack = text.lower()
    if include_any and not any(term in haystack for term in include_any):
        return False
    if exclude_any and any(term in haystack for term in exclude_any):
        return False
    return True


def write_json_atomic(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)


def write_markdown_report(path: Path, candidates: Iterable[Candidate]) -> None:
    lines = [
        "# Reddit Harvest Report",
        "",
        "| Subreddit | Created At (UTC) | Age(h) | High Signal | Title | Link |",
        "|---|---:|---:|---:|---|---|",
    ]
    for c in candidates:
        title = c.title.replace("|", "\\|")
        lines.append(
            f"| {c.subreddit} | {c.created_at} | {c.age_hours:.1f} | {str(c.high_signal)} | {title} | [open]({c.url}) |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def harvest(
    subreddits: list[str],
    min_hours: float,
    max_hours: float,
    timeout_seconds: int,
    max_bytes: int,
    user_agent: str,
    include_body: bool,
    request_sleep: float,
    now_utc: datetime,
    include_any: list[str],
    exclude_any: list[str],
) -> list[Candidate]:
    candidates: list[Candidate] = []

    for subreddit in subreddits:
        listing_url = f"https://old.reddit.com/r/{subreddit}/new/"
        try:
            listing_html = fetch_text(
                listing_url,
                timeout_seconds=timeout_seconds,
                max_bytes=max_bytes,
                user_agent=user_agent,
            )
        except HarvestError:
            listing_html = fetch_text_with_curl(
                listing_url,
                timeout_seconds=timeout_seconds,
                max_bytes=max_bytes,
                user_agent=user_agent,
            )
        posts = extract_posts_from_new_html(listing_html, subreddit_hint=subreddit)

        for post in posts:
            created_at_dt = parse_iso8601(post["created_at"])
            age_hours = (now_utc - created_at_dt).total_seconds() / 3600.0
            if age_hours < min_hours or age_hours > max_hours:
                continue

            if not include_body and not matches_text_filters(
                post["title"], include_any, exclude_any
            ):
                continue

            op_body = ""
            if include_body:
                old_post_url = post["url"].replace("https://www.reddit.com", "https://old.reddit.com")
                try:
                    try:
                        post_html = fetch_text(
                            old_post_url,
                            timeout_seconds=timeout_seconds,
                            max_bytes=max_bytes,
                            user_agent=user_agent,
                        )
                    except HarvestError:
                        post_html = fetch_text_with_curl(
                            old_post_url,
                            timeout_seconds=timeout_seconds,
                            max_bytes=max_bytes,
                            user_agent=user_agent,
                        )
                    op_body = extract_op_body_from_post_html(post_html)
                except HarvestError:
                    op_body = ""
                if request_sleep > 0:
                    time.sleep(request_sleep)

            if include_body and not matches_text_filters(
                f"{post['title']} {op_body}".strip(), include_any, exclude_any
            ):
                continue

            score, flags = score_candidate(post["title"], op_body)
            high_signal = score >= 3 and not flags["promotional_signal"]

            candidates.append(
                Candidate(
                    subreddit=post["subreddit"],
                    title=post["title"],
                    url=post["url"],
                    created_at=post["created_at"],
                    age_hours=round(age_hours, 2),
                    age_label=post["age_label"],
                    author=post["author"],
                    op_body=op_body,
                    first_person=flags["first_person"],
                    pain_signal=flags["pain_signal"],
                    coordination_signal=flags["coordination_signal"],
                    promotional_signal=flags["promotional_signal"],
                    high_signal_score=score,
                    high_signal=high_signal,
                )
            )

        if request_sleep > 0:
            time.sleep(request_sleep)

    candidates.sort(key=lambda c: c.created_at)
    return candidates


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--subreddits",
        type=str,
        default=",".join(DEFAULT_SUBREDDITS),
        help="Comma-separated subreddit names.",
    )
    parser.add_argument("--min-hours", type=float, default=48.0)
    parser.add_argument("--max-hours", type=float, default=72.0)
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--max-bytes", type=int, default=8_000_000)
    parser.add_argument("--sleep-seconds", type=float, default=0.2)
    parser.add_argument(
        "--user-agent",
        type=str,
        default="brain-reddit-harvest/1.0 (+https://example.local)",
        help="HTTP user-agent string.",
    )
    parser.add_argument("--no-body", action="store_true", help="Skip OP body fetch per post.")
    parser.add_argument(
        "--only-high-signal",
        action="store_true",
        help="Write only high-signal candidates to outputs.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        required=True,
        help="Output JSON file path.",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=None,
        help="Optional output markdown report path.",
    )
    parser.add_argument(
        "--include-any",
        type=str,
        default=None,
        help="Comma-separated terms; at least one must appear in the title/body.",
    )
    parser.add_argument(
        "--exclude-any",
        type=str,
        default=None,
        help="Comma-separated terms; if any appear in the title/body the post is rejected.",
    )
    parser.add_argument(
        "--now",
        type=str,
        default=None,
        help="Override now timestamp in ISO8601 with timezone (for reproducibility/tests).",
    )
    return parser


def parse_now(now_arg: str | None) -> datetime:
    if now_arg is None:
        return datetime.now(timezone.utc)
    return parse_iso8601(now_arg)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    subreddits = [s.strip() for s in args.subreddits.split(",") if s.strip()]
    if not subreddits:
        raise SystemExit("No subreddits provided.")

    now_utc = parse_now(args.now)
    include_any = parse_term_list(args.include_any)
    exclude_any = parse_term_list(args.exclude_any)

    try:
        data = harvest(
            subreddits=subreddits,
            min_hours=args.min_hours,
            max_hours=args.max_hours,
            timeout_seconds=args.timeout_seconds,
            max_bytes=args.max_bytes,
            user_agent=args.user_agent,
            include_body=not args.no_body,
            request_sleep=args.sleep_seconds,
            now_utc=now_utc,
            include_any=include_any,
            exclude_any=exclude_any,
        )

        if args.only_high_signal:
            data = [c for c in data if c.high_signal]

        payload = {
            "generated_at": now_utc.isoformat(),
            "window": {"min_hours": args.min_hours, "max_hours": args.max_hours},
            "filters": {"includeAny": include_any, "excludeAny": exclude_any},
            "count": len(data),
            "items": [asdict(c) for c in data],
        }
        write_json_atomic(args.output_json, payload)

        if args.output_md is not None:
            write_markdown_report(args.output_md, data)

        return 0
    except HarvestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
