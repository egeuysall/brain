import tempfile
import time
import unittest
from pathlib import Path

from tooling.scripts.fetch_outreach_context import (
    count_reddit_posts,
    count_x_posts,
    parse_csv_arg,
    remaining_seconds,
    validate_agents_context,
    write_json,
)


class FetchOutreachContextTests(unittest.TestCase):
    def test_validate_agents_context_accepts_expected_shape(self) -> None:
        payload = {
            "generatedAt": "2026-04-03T10:00:00Z",
            "operator": {"name": "ryva"},
            "context": {"mode": "execution"},
            "sources": {"diary": "/diary.json"},
        }
        ok, error = validate_agents_context(payload)
        self.assertTrue(ok)
        self.assertEqual(error, "")

    def test_validate_agents_context_rejects_missing_keys(self) -> None:
        payload = {
            "generatedAt": "2026-04-03T10:00:00Z",
            "operator": {},
            "context": {},
        }
        ok, error = validate_agents_context(payload)
        self.assertFalse(ok)
        self.assertIn("Missing keys", error)

    def test_count_x_posts_handles_multiple_payload_shapes(self) -> None:
        self.assertEqual(count_x_posts({"postsInWindow": [1, 2, 3]}), 3)
        self.assertEqual(count_x_posts({"posts": [1, 2]}), 2)
        self.assertEqual(count_x_posts({"posts": "bad"}), 0)
        self.assertEqual(count_x_posts(None), 0)

    def test_count_reddit_posts_handles_multiple_payload_shapes(self) -> None:
        self.assertEqual(count_reddit_posts({"count": 7}), 7)
        self.assertEqual(count_reddit_posts({"items": [1, 2, 3]}), 3)
        self.assertEqual(count_reddit_posts({"items": "bad"}), 0)
        self.assertEqual(count_reddit_posts(None), 0)

    def test_remaining_seconds_never_negative(self) -> None:
        start = time.monotonic() - 3.0
        self.assertGreaterEqual(remaining_seconds(start, 2), 0.0)
        self.assertLessEqual(remaining_seconds(start, 2), 0.01)

    def test_write_json_writes_expected_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "nested" / "out.json"
            payload = {"ok": True, "count": 2}
            write_json(output, payload)
            self.assertTrue(output.exists())
            self.assertIn('"ok": true', output.read_text(encoding="utf-8"))

    def test_parse_csv_arg_uses_default_for_none_or_empty(self) -> None:
        default = ["EngineeringManagers", "devops"]
        self.assertEqual(parse_csv_arg(None, default), default)
        self.assertEqual(parse_csv_arg("", default), default)

    def test_parse_csv_arg_trims_and_filters_values(self) -> None:
        parsed = parse_csv_arg(" CTO , EngineeringManagers, , devops ", ["fallback"])
        self.assertEqual(parsed, ["CTO", "EngineeringManagers", "devops"])


if __name__ == "__main__":
    unittest.main()
