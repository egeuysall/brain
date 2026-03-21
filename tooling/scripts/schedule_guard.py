#!/usr/bin/env python3
"""Decide whether a workflow run should execute scheduled sync."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", required=True, help="GitHub event name")
    parser.add_argument(
        "--timezone",
        default="America/Chicago",
        help="IANA timezone name used for schedule guard",
    )
    parser.add_argument(
        "--target-time",
        default="06:00",
        help="Local wall time to allow scheduled run (HH:MM)",
    )
    parser.add_argument(
        "--now",
        default=None,
        help="ISO8601 UTC time override for tests",
    )
    parser.add_argument(
        "--write-github-output",
        action="store_true",
        help="Write run_sync=<bool> to $GITHUB_OUTPUT",
    )
    return parser.parse_args()


def parse_now(now_arg: str | None) -> datetime:
    if now_arg is None:
        return datetime.now(timezone.utc)
    value = datetime.fromisoformat(now_arg)
    if value.tzinfo is None:
        raise ValueError("--now must include timezone")
    return value.astimezone(timezone.utc)


def parse_target_time(value: str) -> tuple[int, int]:
    parts = value.split(":")
    if len(parts) != 2:
        raise ValueError("--target-time must be HH:MM")

    hour = int(parts[0])
    minute = int(parts[1])
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        raise ValueError("--target-time must be HH:MM")
    return hour, minute


def should_run(event: str, now_utc: datetime, tz_name: str, target_hour: int, target_minute: int) -> bool:
    if event != "schedule":
        return True
    local = now_utc.astimezone(ZoneInfo(tz_name))
    return local.hour == target_hour and local.minute == target_minute


def write_github_output(run_sync: bool) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        raise RuntimeError("GITHUB_OUTPUT is not set")
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(f"run_sync={'true' if run_sync else 'false'}\n")


def main() -> int:
    args = parse_args()
    try:
        now_utc = parse_now(args.now)
        hour, minute = parse_target_time(args.target_time)
        run_sync = should_run(args.event, now_utc, args.timezone, hour, minute)
    except Exception as exc:  # pragma: no cover
        print(f"schedule guard failed: {exc}", file=sys.stderr)
        return 1

    if args.write_github_output:
        try:
            write_github_output(run_sync)
        except Exception as exc:  # pragma: no cover
            print(f"schedule guard failed: {exc}", file=sys.stderr)
            return 1

    print("true" if run_sync else "false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
