import json
import unittest

from tooling.scripts.reddit_fix_json import parse_json_or_raise, sanitize_json_text


class RedditFixJsonTests(unittest.TestCase):
    def test_sanitize_removes_control_chars(self) -> None:
        raw = '{"a":"ok\u0000bad\u0007"}'
        sanitized, removed = sanitize_json_text(raw)
        self.assertEqual(removed, 2)
        self.assertEqual(sanitized, '{"a":"okbad"}')

    def test_parse_after_sanitize(self) -> None:
        raw = '{"a":"hello\u0001world","n":1}'
        sanitized, _ = sanitize_json_text(raw)
        parsed = parse_json_or_raise(sanitized)
        self.assertEqual(parsed["a"], "helloworld")
        self.assertEqual(parsed["n"], 1)

    def test_parse_json_or_raise_valid(self) -> None:
        parsed = parse_json_or_raise('{"x":1,"y":[2,3]}')
        self.assertEqual(json.dumps(parsed, sort_keys=True), '{"x": 1, "y": [2, 3]}')


if __name__ == "__main__":
    unittest.main()
