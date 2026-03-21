#!/usr/bin/env python3
"""Sync Ryva knowledge feeds into per-entry context files + a compact index."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

FEED_URLS = {
    "diary": "https://egeuysal.com/diary.json",
    "blog": "https://egeuysal.com/blog.json",
}

REQUIRED_TOP_LEVEL_KEYS = {"generatedAt", "count", "items"}
REQUIRED_DIARY_ITEM_KEYS = {"id", "url", "day", "date", "summary", "tags", "body"}
REQUIRED_BLOG_ITEM_KEYS = {
    "id",
    "url",
    "title",
    "description",
    "publishedAt",
    "updatedAt",
    "tags",
    "image",
    "readingTime",
    "body",
}

RESOURCE_EXTENSIONS = {
    ".md",
    ".markdown",
    ".txt",
    ".pdf",
    ".doc",
    ".docx",
    ".rtf",
    ".html",
    ".csv",
    ".json",
}

SAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


class SyncError(Exception):
    """Raised when the sync process should fail closed."""


class ValidationError(SyncError):
    """Raised on untrusted or malformed input."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root path.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=20,
        help="Network timeout for each feed request.",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=6_000_000,
        help="Maximum accepted payload size per feed.",
    )
    parser.add_argument(
        "--now",
        type=str,
        default=None,
        help="Override current UTC time in ISO8601 (for tests).",
    )
    return parser.parse_args()


def parse_now(now_arg: str | None) -> datetime:
    if now_arg is None:
        return datetime.now(timezone.utc)
    try:
        value = datetime.fromisoformat(now_arg)
    except ValueError as exc:
        raise SyncError(f"Invalid --now value: {now_arg}") from exc
    if value.tzinfo is None:
        raise SyncError("--now must include timezone information")
    return value.astimezone(timezone.utc)


def ensure_https_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise SyncError(f"Refusing non-HTTPS URL: {url}")


def fetch_feed(url: str, timeout_seconds: int, max_bytes: int) -> bytes:
    ensure_https_url(url)
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "ryva-knowledge-sync/1.0",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            status = response.getcode()
            if status != 200:
                raise SyncError(f"Unexpected HTTP status {status} for {url}")

            body = response.read(max_bytes + 1)
            if len(body) > max_bytes:
                raise SyncError(f"Payload exceeds max-bytes ({max_bytes}) for {url}")
            return body
    except urllib.error.URLError as exc:
        raise SyncError(f"Failed to fetch {url}: {exc}") from exc


def parse_json_bytes(body: bytes, source_name: str) -> dict[str, Any]:
    try:
        decoded = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"Invalid UTF-8 in {source_name}") from exc

    try:
        payload = json.loads(decoded)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON in {source_name}: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValidationError(f"Expected top-level object in {source_name}")
    return payload


def validate_required_keys(obj: dict[str, Any], required: set[str], label: str) -> None:
    missing = sorted(required - obj.keys())
    if missing:
        raise ValidationError(f"Missing required keys in {label}: {', '.join(missing)}")


def validate_tags(tags: Any, label: str) -> None:
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        raise ValidationError(f"Expected string array for {label}")


def validate_diary_item(item: dict[str, Any], index: int) -> None:
    validate_required_keys(item, REQUIRED_DIARY_ITEM_KEYS, f"diary.items[{index}]")
    if not isinstance(item["id"], str):
        raise ValidationError(f"Expected string diary.items[{index}].id")
    if not isinstance(item["url"], str):
        raise ValidationError(f"Expected string diary.items[{index}].url")
    ensure_https_url(item["url"])
    if not isinstance(item["day"], int):
        raise ValidationError(f"Expected integer diary.items[{index}].day")
    if not isinstance(item["date"], str):
        raise ValidationError(f"Expected string diary.items[{index}].date")
    if not isinstance(item["summary"], str):
        raise ValidationError(f"Expected string diary.items[{index}].summary")
    if not isinstance(item["body"], str):
        raise ValidationError(f"Expected string diary.items[{index}].body")
    validate_tags(item["tags"], f"diary.items[{index}].tags")


def validate_blog_item(item: dict[str, Any], index: int) -> None:
    validate_required_keys(item, REQUIRED_BLOG_ITEM_KEYS, f"blog.items[{index}]")
    if not isinstance(item["id"], str):
        raise ValidationError(f"Expected string blog.items[{index}].id")
    if not isinstance(item["url"], str):
        raise ValidationError(f"Expected string blog.items[{index}].url")
    ensure_https_url(item["url"])
    if not isinstance(item["title"], str):
        raise ValidationError(f"Expected string blog.items[{index}].title")
    if not isinstance(item["description"], str):
        raise ValidationError(f"Expected string blog.items[{index}].description")
    if not isinstance(item["publishedAt"], str):
        raise ValidationError(f"Expected string blog.items[{index}].publishedAt")
    if item["updatedAt"] is not None and not isinstance(item["updatedAt"], str):
        raise ValidationError(f"Expected string|null blog.items[{index}].updatedAt")
    if item["image"] is not None and not isinstance(item["image"], str):
        raise ValidationError(f"Expected string|null blog.items[{index}].image")
    if not isinstance(item["readingTime"], int):
        raise ValidationError(f"Expected integer blog.items[{index}].readingTime")
    if not isinstance(item["body"], str):
        raise ValidationError(f"Expected string blog.items[{index}].body")
    validate_tags(item["tags"], f"blog.items[{index}].tags")


def validate_feed_payload(feed_name: str, payload: dict[str, Any]) -> None:
    validate_required_keys(payload, REQUIRED_TOP_LEVEL_KEYS, feed_name)

    generated_at = payload["generatedAt"]
    count = payload["count"]
    items = payload["items"]

    if not isinstance(generated_at, str):
        raise ValidationError(f"Expected string {feed_name}.generatedAt")
    if not isinstance(count, int):
        raise ValidationError(f"Expected integer {feed_name}.count")
    if not isinstance(items, list):
        raise ValidationError(f"Expected array {feed_name}.items")
    if count != len(items):
        raise ValidationError(
            f"Count mismatch in {feed_name}: count={count}, items={len(items)}"
        )

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValidationError(f"Expected object {feed_name}.items[{index}]")
        if feed_name == "diary":
            validate_diary_item(item, index)
        elif feed_name == "blog":
            validate_blog_item(item, index)
        else:
            raise ValidationError(f"Unknown feed: {feed_name}")


def make_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def atomic_write_bytes(path: Path, data: bytes) -> None:
    make_parent_dir(path)
    tmp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, dir=path.parent) as f:
            tmp_file = Path(f.name)
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_file, path)
    finally:
        if tmp_file is not None and tmp_file.exists():
            tmp_file.unlink(missing_ok=True)


def atomic_write_text(path: Path, data: str) -> None:
    atomic_write_bytes(path, data.encode("utf-8"))


def sanitize_file_stem(value: str) -> str:
    cleaned = SAFE_FILENAME_CHARS.sub("-", value).strip("-.")
    if not cleaned:
        return "entry"
    return cleaned[:120]


def build_item_records(
    source: str,
    items: list[dict[str, Any]],
    generated_at: str,
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    records: list[dict[str, Any]] = []

    for item in items:
        base = sanitize_file_stem(item["id"])
        stem = base
        seq = 2
        while f"{stem}.json" in seen:
            stem = f"{base}-{seq}"
            seq += 1
        filename = f"{stem}.json"
        seen.add(filename)

        rel_path = f"context/latest/{source}/{filename}"
        item_doc = {
            "schemaVersion": 1,
            "kind": "ryva-knowledge-item",
            "source": source,
            "id": item["id"],
            "generatedAt": generated_at,
            "entry": item,
        }

        records.append(
            {
                "id": item["id"],
                "file": rel_path,
                "filename": filename,
                "entry": item,
                "doc": item_doc,
            }
        )

    return records


def sync_item_directory(root: Path, source: str, records: list[dict[str, Any]]) -> None:
    target_dir = root / "context" / "latest" / source
    target_dir.mkdir(parents=True, exist_ok=True)
    desired_names: set[str] = set()

    for record in records:
        desired_names.add(record["filename"])
        payload = json.dumps(record["doc"], ensure_ascii=False, indent=2) + "\n"
        atomic_write_text(target_dir / record["filename"], payload)

    for existing in target_dir.glob("*.json"):
        if existing.name not in desired_names:
            existing.unlink()


def list_manual_resources(root: Path) -> dict[str, Any]:
    resources_root = root / "resources"
    resources_root.mkdir(parents=True, exist_ok=True)

    files: list[dict[str, Any]] = []
    by_category: dict[str, int] = {}

    for path in sorted(resources_root.rglob("*")):
        if not path.is_file():
            continue

        rel = path.relative_to(root).as_posix()
        if path.name in {".gitkeep", "README.md", "FORMAT.md"}:
            continue
        if any(part.startswith(".") for part in path.relative_to(resources_root).parts):
            continue
        if path.suffix.lower() not in RESOURCE_EXTENSIONS:
            continue

        parts = path.relative_to(resources_root).parts
        category = parts[0] if len(parts) > 1 else "uncategorized"
        by_category[category] = by_category.get(category, 0) + 1

        files.append(
            {
                "path": rel,
                "category": category,
                "sizeBytes": path.stat().st_size,
            }
        )

    return {
        "totalFiles": len(files),
        "byCategory": dict(sorted(by_category.items())),
        "files": files,
    }


def build_entry_index(
    source: str,
    record: dict[str, Any],
) -> dict[str, Any]:
    entry = record["entry"]
    return {
        "source": source,
        "id": entry["id"],
        "entryFile": record["file"],
        "url": entry.get("url"),
        "title": entry.get("title", entry.get("summary")),
        "publishedAt": entry.get("publishedAt", entry.get("date")),
        "updatedAt": entry.get("updatedAt"),
        "tags": entry.get("tags", []),
        "summary": entry.get("description", entry.get("summary")),
    }


def build_knowledge_payload(
    diary_payload: dict[str, Any],
    blog_payload: dict[str, Any],
    diary_records: list[dict[str, Any]],
    blog_records: list[dict[str, Any]],
    synced_at_utc: datetime,
    manual_resources: dict[str, Any],
) -> dict[str, Any]:
    entries = [build_entry_index("diary", record) for record in diary_records]
    entries.extend(build_entry_index("blog", record) for record in blog_records)

    entries.sort(
        key=lambda item: (
            item["publishedAt"] if item["publishedAt"] is not None else "",
            item["source"],
            item["id"],
        ),
        reverse=True,
    )

    synced_at = synced_at_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "schemaVersion": 3,
        "kind": "ryva-knowledge-context",
        "syncedAt": synced_at,
        "queryPolicy": {
            "defaultContext": [
                "context/latest/knowledge.json",
                "resources/**",
            ],
            "expandableContext": [
                "context/latest/diary/*.json",
                "context/latest/blog/*.json",
            ],
            "staleProtection": {
                "preferLatestSync": True,
            },
        },
        "feeds": {
            "diary": {
                "generatedAt": diary_payload["generatedAt"],
                "count": diary_payload["count"],
            },
            "blog": {
                "generatedAt": blog_payload["generatedAt"],
                "count": blog_payload["count"],
            },
        },
        "itemFiles": {
            "diary": {
                "dir": "context/latest/diary",
                "count": len(diary_records),
            },
            "blog": {
                "dir": "context/latest/blog",
                "count": len(blog_records),
            },
        },
        "resources": manual_resources,
        "totals": {
            "entries": len(entries),
            "diary": diary_payload["count"],
            "blog": blog_payload["count"],
            "manualResources": manual_resources["totalFiles"],
        },
        "entries": entries,
    }


def remove_legacy_artifacts(root: Path) -> None:
    legacy_files = [
        root / "context" / "latest" / "feeds.json",
        root / "context" / "latest" / "feeds.md",
    ]
    legacy_paths = [*legacy_files, root / "snapshots"]

    for legacy_path in legacy_paths:
        if not legacy_path.exists() and not legacy_path.is_symlink():
            continue
        if legacy_path.is_file() or legacy_path.is_symlink():
            legacy_path.unlink(missing_ok=True)
            continue
        if legacy_path.is_dir():
            shutil.rmtree(legacy_path)


def run_sync(
    root: Path,
    now_utc: datetime,
    timeout_seconds: int,
    max_bytes: int,
    fetcher: Callable[[str, int, int], bytes] = fetch_feed,
) -> dict[str, str]:
    if timeout_seconds <= 0:
        raise SyncError("timeout-seconds must be positive")
    if max_bytes <= 0:
        raise SyncError("max-bytes must be positive")

    parsed_payloads: dict[str, dict[str, Any]] = {}

    for feed_name, feed_url in FEED_URLS.items():
        raw = fetcher(feed_url, timeout_seconds, max_bytes)
        parsed = parse_json_bytes(raw, feed_name)
        validate_feed_payload(feed_name, parsed)
        parsed_payloads[feed_name] = parsed

    diary_records = build_item_records(
        source="diary",
        items=parsed_payloads["diary"]["items"],
        generated_at=parsed_payloads["diary"]["generatedAt"],
    )
    blog_records = build_item_records(
        source="blog",
        items=parsed_payloads["blog"]["items"],
        generated_at=parsed_payloads["blog"]["generatedAt"],
    )

    sync_item_directory(root, "diary", diary_records)
    sync_item_directory(root, "blog", blog_records)

    manual_resources = list_manual_resources(root)
    knowledge = build_knowledge_payload(
        diary_payload=parsed_payloads["diary"],
        blog_payload=parsed_payloads["blog"],
        diary_records=diary_records,
        blog_records=blog_records,
        synced_at_utc=now_utc,
        manual_resources=manual_resources,
    )

    knowledge_json = json.dumps(knowledge, ensure_ascii=False, indent=2) + "\n"
    knowledge_path = root / "context" / "latest" / "knowledge.json"
    write_required = True
    if knowledge_path.exists():
        try:
            write_required = knowledge_path.read_text(encoding="utf-8") != knowledge_json
        except OSError:
            write_required = True
    if write_required:
        atomic_write_text(knowledge_path, knowledge_json)

    remove_legacy_artifacts(root)

    return {
        "knowledge_json": "context/latest/knowledge.json",
        "diary_dir": "context/latest/diary",
        "blog_dir": "context/latest/blog",
    }


def main() -> int:
    args = parse_args()
    try:
        now_utc = parse_now(args.now)
        paths = run_sync(
            root=args.root.resolve(),
            now_utc=now_utc,
            timeout_seconds=args.timeout_seconds,
            max_bytes=args.max_bytes,
        )
    except SyncError as exc:
        print(f"sync failed: {exc}", file=sys.stderr)
        return 1

    print("knowledge sync completed")
    print(f"knowledge_json={paths['knowledge_json']}")
    print(f"diary_dir={paths['diary_dir']}")
    print(f"blog_dir={paths['blog_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
