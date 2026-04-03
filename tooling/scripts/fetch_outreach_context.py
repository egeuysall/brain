#!/usr/bin/env python3
"""Fetch outreach context with bounded runtime and reliable fallbacks.

This script consolidates three inputs used by outreach automations:
1) Canonical Ryva operator context (`agents.json`)
2) X post candidates (r.jina/DDG based)
3) Reddit high-signal candidates (old.reddit listing harvest)

Security and reliability defaults:
- HTTPS-only remote fetches
- Bounded retries and per-step timeouts
- Global runtime budget (default 170s) to stay below 3-minute jobs
- No credential hardcoding
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AGENTS_CONTEXT_URL = "https://egeuysal.com/agents.json"
DEFAULT_X_QUERIES = [
    "site:x.com standup waste engineering team status",
    "site:x.com engineering manager slack chaos status",
    "site:x.com PR confusion review context status",
    "site:x.com who owns this bug status",
    "site:x.com context is scattered in slack status",
    "site:x.com things falling through cracks engineering status",
]
DEFAULT_SUBREDDITS = [
    "EngineeringManagers",
    "ExperiencedDevs",
    "ProductManagement",
    "projectmanagement",
    "devops",
    "startups",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, required=True, help="Consolidated output JSON path."
    )
    parser.add_argument(
        "--budget-seconds",
        type=int,
        default=170,
        help="Global max runtime budget for this script.",
    )
    parser.add_argument(
        "--days-window",
        type=int,
        default=14,
        help="Max post age window in days for X/Reddit candidates.",
    )
    parser.add_argument(
        "--max-x-links-per-query",
        type=int,
        default=6,
        help="Per-query X link discovery cap.",
    )
    parser.add_argument(
        "--max-x-hydrated",
        type=int,
        default=80,
        help="Max hydrated X posts before truncation.",
    )
    return parser.parse_args()


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def remaining_seconds(start_monotonic: float, budget_seconds: int) -> float:
    return max(0.0, float(budget_seconds) - (time.monotonic() - start_monotonic))


def ensure_https(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(f"Refusing non-HTTPS URL: {url}")


def fetch_json_with_retries(
    url: str, timeout_seconds: int, retries: int, max_bytes: int
) -> dict[str, Any]:
    ensure_https(url)
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "brain-outreach-fetch/1.0",
        },
        method="GET",
    )
    delay = 1.0
    last_error: Exception | None = None

    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Unexpected HTTP status {resp.status}")
                body = resp.read(max_bytes + 1)
                if len(body) > max_bytes:
                    raise RuntimeError("Response exceeded max-bytes guardrail")
                payload = json.loads(body.decode("utf-8"))
                if not isinstance(payload, dict):
                    raise RuntimeError("Expected JSON object")
                return payload
        except (urllib.error.URLError, json.JSONDecodeError, RuntimeError) as exc:
            last_error = exc
            if attempt >= retries:
                break
            time.sleep(delay)
            delay = min(delay * 2.0, 8.0)

    raise RuntimeError(f"Failed fetching JSON from {url}: {last_error}")


def validate_agents_context(payload: dict[str, Any]) -> tuple[bool, str]:
    required_keys = {"generatedAt", "operator", "context", "sources"}
    missing = sorted(required_keys - set(payload.keys()))
    if missing:
        return False, f"Missing keys: {', '.join(missing)}"
    if not isinstance(payload.get("sources"), dict):
        return False, "Expected object for sources"
    return True, ""


def run_step(
    command: list[str], cwd: Path, timeout_seconds: int, output_file: Path | None
) -> dict[str, Any]:
    started = time.monotonic()
    result: dict[str, Any] = {
        "command": command,
        "timeoutSeconds": timeout_seconds,
        "ok": False,
    }
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        duration = time.monotonic() - started
        result.update(
            {
                "durationSeconds": round(duration, 2),
                "exitCode": proc.returncode,
                "stdoutTail": proc.stdout[-4000:],
                "stderrTail": proc.stderr[-4000:],
                "ok": proc.returncode == 0,
            }
        )
        if output_file is not None:
            result["outputFile"] = str(output_file)
    except subprocess.TimeoutExpired:
        duration = time.monotonic() - started
        result.update(
            {
                "durationSeconds": round(duration, 2),
                "error": f"Step timed out after {timeout_seconds}s",
                "ok": False,
            }
        )
    return result


def read_json_file(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def count_x_posts(payload: dict[str, Any] | None) -> int:
    if not payload:
        return 0
    posts_in_window = payload.get("postsInWindow")
    if isinstance(posts_in_window, list):
        return len(posts_in_window)
    posts = payload.get("posts")
    if isinstance(posts, list):
        return len(posts)
    return 0


def count_reddit_posts(payload: dict[str, Any] | None) -> int:
    if not payload:
        return 0
    count = payload.get("count")
    if isinstance(count, int):
        return count
    items = payload.get("items")
    if isinstance(items, list):
        return len(items)
    return 0


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    args = parse_args()
    start = time.monotonic()
    root = Path(__file__).resolve().parents[2]
    runtime_dir = args.out.parent
    runtime_dir.mkdir(parents=True, exist_ok=True)

    agents_out = runtime_dir / "agents-context.json"
    x_out = runtime_dir / "x-candidates.json"
    reddit_out = runtime_dir / "reddit-candidates.json"

    steps: dict[str, Any] = {}
    agents_payload: dict[str, Any] | None = None
    agents_ok = False
    agents_error = ""

    # Step 1: canonical context
    if remaining_seconds(start, args.budget_seconds) >= 8:
        try:
            agents_payload = fetch_json_with_retries(
                AGENTS_CONTEXT_URL,
                timeout_seconds=10,
                retries=2,
                max_bytes=1_000_000,
            )
            agents_ok, agents_error = validate_agents_context(agents_payload)
            if agents_ok:
                write_json(agents_out, agents_payload)
            else:
                agents_payload = None
        except Exception as exc:  # noqa: BLE001
            agents_error = str(exc)
            agents_ok = False
    else:
        agents_error = "Skipped due to low remaining budget"

    steps["agentsContext"] = {
        "ok": agents_ok,
        "error": agents_error,
        "outputFile": str(agents_out) if agents_ok else None,
    }

    # Step 2: X candidates with fallback
    x_step: dict[str, Any] = {"ok": False, "fallbackUsed": False}
    x_payload: dict[str, Any] | None = None
    x_queries_arg = ",".join(DEFAULT_X_QUERIES)
    x_timeout = int(max(0, min(80, remaining_seconds(start, args.budget_seconds) - 45)))
    if x_timeout >= 20:
        primary_cmd = [
            sys.executable,
            "tooling/scripts/fetch_x_posts_via_jina_ddg.py",
            "--out",
            str(x_out),
            "--queries",
            x_queries_arg,
            "--max-links-per-query",
            str(args.max_x_links_per_query),
            "--max-hydrated",
            str(args.max_x_hydrated),
            "--sleep-ms",
            "80",
            "--days",
            str(max(1, args.days_window)),
        ]
        primary = run_step(
            primary_cmd, cwd=root, timeout_seconds=x_timeout, output_file=x_out
        )
        x_step["primary"] = primary
        if primary.get("ok"):
            x_payload = read_json_file(x_out)
            x_step["ok"] = x_payload is not None and count_x_posts(x_payload) > 0

    if not x_step["ok"]:
        fallback_timeout = int(
            max(0, min(45, remaining_seconds(start, args.budget_seconds) - 25))
        )
        if fallback_timeout >= 15:
            x_step["fallbackUsed"] = True
            fallback_cmd = [
                sys.executable,
                "tooling/scripts/find_x_candidates_quick.py",
                "--out",
                str(x_out),
                "--max-links-per-query",
                "4",
                "--max-hydrate",
                "50",
                "--workers",
                "6",
            ]
            fallback = run_step(
                fallback_cmd,
                cwd=root,
                timeout_seconds=fallback_timeout,
                output_file=x_out,
            )
            x_step["fallback"] = fallback
            if fallback.get("ok"):
                x_payload = read_json_file(x_out)
                x_step["ok"] = x_payload is not None and count_x_posts(x_payload) > 0

    x_step["postCount"] = count_x_posts(x_payload)
    x_step["outputFile"] = str(x_out) if x_payload else None
    steps["xCandidates"] = x_step

    # Step 3: Reddit candidates
    reddit_payload: dict[str, Any] | None = None
    reddit_timeout = int(
        max(0, min(70, remaining_seconds(start, args.budget_seconds) - 5))
    )
    reddit_step: dict[str, Any] = {"ok": False, "fallbackUsed": False}
    if reddit_timeout >= 15:
        max_hours = max(24.0, float(args.days_window) * 24.0)
        reddit_cmd = [
            sys.executable,
            "tooling/scripts/reddit_harvest.py",
            "--subreddits",
            ",".join(DEFAULT_SUBREDDITS),
            "--min-hours",
            "0",
            "--max-hours",
            str(int(max_hours)),
            "--timeout-seconds",
            "10",
            "--sleep-seconds",
            "0.1",
            "--no-body",
            "--only-high-signal",
            "--output-json",
            str(reddit_out),
        ]
        reddit_run = run_step(
            reddit_cmd,
            cwd=root,
            timeout_seconds=reddit_timeout,
            output_file=reddit_out,
        )
        reddit_step["primary"] = reddit_run
        if reddit_run.get("ok"):
            reddit_payload = read_json_file(reddit_out)
            reddit_step["ok"] = (
                reddit_payload is not None and count_reddit_posts(reddit_payload) > 0
            )
            # If strict high-signal filtering returns zero, retry a broader pull.
            if not reddit_step["ok"]:
                fallback_timeout = int(
                    max(0, min(35, remaining_seconds(start, args.budget_seconds) - 5))
                )
                if fallback_timeout >= 10:
                    reddit_step["fallbackUsed"] = True
                    fallback_cmd = [
                        sys.executable,
                        "tooling/scripts/reddit_harvest.py",
                        "--subreddits",
                        ",".join(DEFAULT_SUBREDDITS),
                        "--min-hours",
                        "0",
                        "--max-hours",
                        str(int(max_hours)),
                        "--timeout-seconds",
                        "10",
                        "--sleep-seconds",
                        "0.1",
                        "--no-body",
                        "--output-json",
                        str(reddit_out),
                    ]
                    fallback_run = run_step(
                        fallback_cmd,
                        cwd=root,
                        timeout_seconds=fallback_timeout,
                        output_file=reddit_out,
                    )
                    reddit_step["fallback"] = fallback_run
                    if fallback_run.get("ok"):
                        reddit_payload = read_json_file(reddit_out)
                        reddit_step["ok"] = (
                            reddit_payload is not None
                            and count_reddit_posts(reddit_payload) > 0
                        )
    else:
        reddit_step["error"] = "Skipped due to low remaining budget"

    reddit_step["postCount"] = count_reddit_posts(reddit_payload)
    reddit_step["outputFile"] = str(reddit_out) if reddit_payload else None
    steps["redditCandidates"] = reddit_step

    elapsed = time.monotonic() - start
    within_budget = elapsed <= args.budget_seconds

    summary = {
        "generatedAt": now_utc_iso(),
        "kind": "outreach-fetch-context",
        "runtime": {
            "budgetSeconds": args.budget_seconds,
            "elapsedSeconds": round(elapsed, 2),
            "withinBudget": within_budget,
        },
        "sources": {
            "agentsContextUrl": AGENTS_CONTEXT_URL,
            "xDaysWindow": max(1, args.days_window),
            "redditDaysWindow": max(1, args.days_window),
        },
        "results": steps,
        "totals": {
            "xPosts": count_x_posts(x_payload),
            "redditPosts": count_reddit_posts(reddit_payload),
            "anyUsableSignals": (
                count_x_posts(x_payload) + count_reddit_posts(reddit_payload)
            )
            > 0,
        },
        "files": {
            "agentsContext": str(agents_out) if agents_ok else None,
            "xCandidates": str(x_out) if x_payload else None,
            "redditCandidates": str(reddit_out) if reddit_payload else None,
        },
    }

    write_json(args.out, summary)
    print(json.dumps(summary["runtime"], indent=2))

    if not within_budget:
        return 2
    if not summary["totals"]["anyUsableSignals"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
