import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tooling.scripts.sync_knowledge import ValidationError, run_sync, validate_feed_payload


def valid_diary_payload() -> dict:
    return {
        "generatedAt": "2026-03-21",
        "count": 1,
        "items": [
            {
                "id": "2026-03-20",
                "url": "https://egeuysal.com/diary/2026-03-20/",
                "day": 15,
                "date": "2026-03-20",
                "summary": "Reset day",
                "tags": ["ryva", "experiment"],
                "body": "Diary body",
            }
        ],
    }


def valid_blog_payload() -> dict:
    return {
        "generatedAt": "2026-03-21",
        "count": 1,
        "items": [
            {
                "id": "how-ryva-works",
                "url": "https://egeuysal.com/blog/how-ryva-works/",
                "title": "How Ryva works",
                "description": "Architecture and decisions",
                "publishedAt": "2026-03-15",
                "updatedAt": None,
                "tags": ["saas"],
                "image": "https://egeuysal.com/image.png",
                "readingTime": 8,
                "body": "Blog body",
            }
        ],
    }


class SyncKnowledgeTests(unittest.TestCase):
    def test_validate_feed_payload_rejects_missing_keys(self) -> None:
        payload = valid_diary_payload()
        del payload["generatedAt"]

        with self.assertRaises(ValidationError):
            validate_feed_payload("diary", payload)

    def test_validate_feed_payload_rejects_count_mismatch(self) -> None:
        payload = valid_blog_payload()
        payload["count"] = 2

        with self.assertRaises(ValidationError):
            validate_feed_payload("blog", payload)

    def test_run_sync_writes_compact_index_and_item_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = datetime(2026, 3, 21, 11, 0, 0, tzinfo=timezone.utc)

            (root / "resources" / "articles").mkdir(parents=True, exist_ok=True)
            (root / "resources" / "newsletters").mkdir(parents=True, exist_ok=True)
            (root / "resources" / "articles" / "sample.md").write_text("# Article")
            (root / "resources" / "newsletters" / "issue-01.md").write_text("# Newsletter")

            (root / "context" / "latest" / "diary").mkdir(parents=True, exist_ok=True)
            (root / "context" / "latest" / "blog").mkdir(parents=True, exist_ok=True)
            (root / "context" / "latest" / "feeds.json").write_text("{}")
            (root / "context" / "latest" / "feeds.md").write_text("legacy")
            (root / "context" / "latest" / "diary" / "stale.json").write_text("{}")
            (root / "context" / "latest" / "blog" / "stale.json").write_text("{}")

            diary = json.dumps(valid_diary_payload()).encode("utf-8")
            blog = json.dumps(valid_blog_payload()).encode("utf-8")

            def fake_fetch(url: str, timeout_seconds: int, max_bytes: int) -> bytes:
                self.assertGreater(timeout_seconds, 0)
                self.assertGreater(max_bytes, 0)
                if url.endswith("diary.json"):
                    return diary
                if url.endswith("blog.json"):
                    return blog
                self.fail(f"unexpected URL: {url}")

            result = run_sync(
                root=root,
                now_utc=now,
                timeout_seconds=10,
                max_bytes=1_000_000,
                fetcher=fake_fetch,
            )

            self.assertEqual(result["knowledge_json"], "context/latest/knowledge.json")
            self.assertEqual(result["diary_dir"], "context/latest/diary")
            self.assertEqual(result["blog_dir"], "context/latest/blog")

            knowledge_path = root / "context" / "latest" / "knowledge.json"
            diary_dir = root / "context" / "latest" / "diary"
            blog_dir = root / "context" / "latest" / "blog"

            self.assertTrue(knowledge_path.exists())
            self.assertTrue(diary_dir.exists())
            self.assertTrue(blog_dir.exists())
            self.assertFalse((root / "context" / "latest" / "feeds.json").exists())
            self.assertFalse((root / "context" / "latest" / "feeds.md").exists())
            self.assertFalse((diary_dir / "stale.json").exists())
            self.assertFalse((blog_dir / "stale.json").exists())
            self.assertFalse((root / "snapshots").exists())

            knowledge = json.loads(knowledge_path.read_text())
            self.assertEqual(knowledge["schemaVersion"], 3)
            self.assertEqual(knowledge["kind"], "ryva-knowledge-context")
            self.assertEqual(knowledge["itemFiles"]["diary"]["count"], 1)
            self.assertEqual(knowledge["itemFiles"]["blog"]["count"], 1)
            self.assertEqual(knowledge["totals"]["entries"], 2)
            self.assertEqual(
                knowledge["queryPolicy"]["defaultContext"],
                ["context/latest/knowledge.json", "resources/**"],
            )
            self.assertIn(
                "context/latest/diary/*.json",
                knowledge["queryPolicy"]["expandableContext"],
            )
            self.assertIn(
                "context/latest/blog/*.json",
                knowledge["queryPolicy"]["expandableContext"],
            )

            entry_index = knowledge["entries"][0]
            self.assertIn("entryFile", entry_index)
            self.assertNotIn("body", entry_index)

            diary_item_files = list(diary_dir.glob("*.json"))
            blog_item_files = list(blog_dir.glob("*.json"))
            self.assertEqual(len(diary_item_files), 1)
            self.assertEqual(len(blog_item_files), 1)

            diary_item = json.loads(diary_item_files[0].read_text())
            blog_item = json.loads(blog_item_files[0].read_text())
            self.assertEqual(diary_item["kind"], "ryva-knowledge-item")
            self.assertEqual(diary_item["source"], "diary")
            self.assertIn("entry", diary_item)
            self.assertEqual(blog_item["kind"], "ryva-knowledge-item")
            self.assertEqual(blog_item["source"], "blog")

    def test_run_sync_updates_item_file_when_feed_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = datetime(2026, 3, 21, 11, 0, 0, tzinfo=timezone.utc)

            diary = json.dumps(valid_diary_payload()).encode("utf-8")
            blog_v1_payload = valid_blog_payload()
            blog_v1 = json.dumps(blog_v1_payload).encode("utf-8")

            blog_v2_payload = valid_blog_payload()
            blog_v2_payload["items"][0]["description"] = "Updated description"
            blog_v2 = json.dumps(blog_v2_payload).encode("utf-8")

            def first_fetch(url: str, timeout_seconds: int, max_bytes: int) -> bytes:
                return diary if url.endswith("diary.json") else blog_v1

            def second_fetch(url: str, timeout_seconds: int, max_bytes: int) -> bytes:
                return diary if url.endswith("diary.json") else blog_v2

            run_sync(
                root=root,
                now_utc=now,
                timeout_seconds=10,
                max_bytes=1_000_000,
                fetcher=first_fetch,
            )
            blog_file = root / "context" / "latest" / "blog" / "how-ryva-works.json"
            before = blog_file.read_text()

            run_sync(
                root=root,
                now_utc=now,
                timeout_seconds=10,
                max_bytes=1_000_000,
                fetcher=second_fetch,
            )
            after = blog_file.read_text()

            self.assertNotEqual(before, after)

    def test_run_sync_fails_closed_on_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = datetime(2026, 3, 21, 11, 0, 0, tzinfo=timezone.utc)

            def bad_fetch(url: str, timeout_seconds: int, max_bytes: int) -> bytes:
                if url.endswith("diary.json"):
                    return b"{not valid json"
                return json.dumps(valid_blog_payload()).encode("utf-8")

            with self.assertRaises(ValidationError):
                run_sync(
                    root=root,
                    now_utc=now,
                    timeout_seconds=10,
                    max_bytes=1_000_000,
                    fetcher=bad_fetch,
                )

            self.assertFalse((root / "context" / "latest" / "knowledge.json").exists())


if __name__ == "__main__":
    unittest.main()
