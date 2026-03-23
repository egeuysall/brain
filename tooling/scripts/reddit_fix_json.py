#!/usr/bin/env python3
"""Sanitize malformed Reddit JSON payloads by removing raw C0 control chars.

Why this exists:
- Reddit endpoints can occasionally return payloads that include raw control
  characters in text fields, which breaks strict parsers (jq/json.loads).
- This script strips those bytes and optionally validates JSON afterwards.

Security/safety defaults:
- Fail closed when JSON remains invalid after sanitation (unless disabled).
- Supports max-bytes guardrail to avoid accidental huge payload processing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ALL_C0_RE = re.compile(r"[\x00-\x1F]")


class FixJsonError(Exception):
    """Raised when sanitation or validation should fail closed."""


def sanitize_json_text(raw_text: str) -> tuple[str, int]:
    """Remove all C0 control characters from a text blob.

    Returns:
        (sanitized_text, removed_count)
    """
    removed_count = len(ALL_C0_RE.findall(raw_text))
    sanitized = ALL_C0_RE.sub("", raw_text)
    return sanitized, removed_count


def parse_json_or_raise(text: str) -> object:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise FixJsonError(f"JSON decode failed: {exc}") from exc


def read_input(path: Path | None, max_bytes: int) -> str:
    if path is None:
        data = sys.stdin.buffer.read(max_bytes + 1)
    else:
        data = path.read_bytes()
    if len(data) > max_bytes:
        raise FixJsonError(f"Input exceeds --max-bytes ({max_bytes})")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FixJsonError("Input is not valid UTF-8") from exc


def write_output(path: Path | None, text: str) -> None:
    if path is None:
        sys.stdout.write(text)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=None, help="Input JSON file path. Defaults to stdin.")
    parser.add_argument("--output", type=Path, default=None, help="Output file path. Defaults to stdout.")
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output after sanitation and validation.",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=15_000_000,
        help="Maximum bytes accepted from input.",
    )
    parser.add_argument(
        "--allow-invalid",
        action="store_true",
        help="Do not fail if JSON remains invalid after sanitation.",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Emit sanitation stats to stderr.",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        raw_text = read_input(args.input, args.max_bytes)
        sanitized, removed_count = sanitize_json_text(raw_text)

        parsed = None
        if not args.allow_invalid:
            parsed = parse_json_or_raise(sanitized)

        if args.pretty:
            if parsed is None:
                parsed = parse_json_or_raise(sanitized)
            output_text = json.dumps(parsed, ensure_ascii=False, indent=2) + "\n"
        else:
            output_text = sanitized

        write_output(args.output, output_text)

        if args.stats:
            print(
                f"removed_control_chars={removed_count} input_bytes={len(raw_text.encode('utf-8'))}",
                file=sys.stderr,
            )
        return 0
    except FixJsonError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
