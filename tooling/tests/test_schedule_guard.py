import unittest
from datetime import datetime, timezone

from tooling.scripts.schedule_guard import should_run


class ScheduleGuardTests(unittest.TestCase):
    def test_manual_event_always_runs(self) -> None:
        now = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
        self.assertTrue(should_run("workflow_dispatch", now, "America/Chicago", 6, 0))

    def test_schedule_runs_at_6am_chicago_in_cst(self) -> None:
        now = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
        self.assertTrue(should_run("schedule", now, "America/Chicago", 6, 0))

    def test_schedule_runs_at_6am_chicago_in_cdt(self) -> None:
        now = datetime(2026, 3, 20, 11, 0, tzinfo=timezone.utc)
        self.assertTrue(should_run("schedule", now, "America/Chicago", 6, 0))

    def test_schedule_skips_wrong_local_time(self) -> None:
        now = datetime(2026, 3, 20, 12, 0, tzinfo=timezone.utc)
        self.assertFalse(should_run("schedule", now, "America/Chicago", 6, 0))


if __name__ == "__main__":
    unittest.main()
