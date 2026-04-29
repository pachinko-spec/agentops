"""AnttimeRateGuard の頻度上限・Retry-After 挙動を検証する。"""
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from tools.agentops_monitor.__main__ import (
    JST,
    AnttimeRateGuard,
    jst_now,
)


class AnttimeRateGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.state_path = Path(self.tmp.name) / "anttime-rate.json"
        self.now = jst_now()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_first_event_allowed(self) -> None:
        guard = AnttimeRateGuard(self.state_path, per_minute=5, per_hour=60)
        allowed, reason = guard.check_and_record(self.now)
        self.assertTrue(allowed, reason)

    def test_per_minute_limit(self) -> None:
        guard = AnttimeRateGuard(self.state_path, per_minute=3, per_hour=60)
        for _ in range(3):
            guard.check_and_record(self.now)
        allowed, reason = guard.check_and_record(self.now)
        self.assertFalse(allowed)
        self.assertIn("60s", reason)

    def test_per_hour_limit(self) -> None:
        guard = AnttimeRateGuard(self.state_path, per_minute=100, per_hour=4)
        # 30 秒間隔で送ると分上限は超えないが時間上限は超える
        for i in range(4):
            guard.check_and_record(self.now + timedelta(minutes=i * 5))
        allowed, reason = guard.check_and_record(self.now + timedelta(minutes=22))
        self.assertFalse(allowed)
        self.assertIn("3600s", reason)

    def test_minute_window_slides(self) -> None:
        guard = AnttimeRateGuard(self.state_path, per_minute=3, per_hour=60)
        for _ in range(3):
            guard.check_and_record(self.now)
        # 70 秒後はもう古いイベントが窓から外れる
        later = self.now + timedelta(seconds=70)
        allowed, _ = guard.check_and_record(later)
        self.assertTrue(allowed)

    def test_state_persists_to_disk(self) -> None:
        guard1 = AnttimeRateGuard(self.state_path, per_minute=3, per_hour=60)
        guard1.check_and_record(self.now)
        # 別 instance を作ると state が読み込まれる
        guard2 = AnttimeRateGuard(self.state_path, per_minute=3, per_hour=60)
        for _ in range(2):
            guard2.check_and_record(self.now)
        allowed, _ = guard2.check_and_record(self.now)
        self.assertFalse(allowed)

    def test_retry_after_blocks(self) -> None:
        guard = AnttimeRateGuard(self.state_path)
        guard.record_retry_after(120, self.now)
        blocked, remaining = guard.is_blocked_by_retry_after(self.now)
        self.assertTrue(blocked)
        self.assertGreater(remaining, 0)

    def test_retry_after_expires(self) -> None:
        guard = AnttimeRateGuard(self.state_path)
        guard.record_retry_after(10, self.now)
        # 11 秒後は解除されている
        later = self.now + timedelta(seconds=11)
        blocked, _ = guard.is_blocked_by_retry_after(later)
        self.assertFalse(blocked)

    def test_corrupt_state_file_does_not_crash(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text("not json", encoding="utf-8")
        guard = AnttimeRateGuard(self.state_path)
        allowed, _ = guard.check_and_record(self.now)
        self.assertTrue(allowed)

    def test_old_events_trimmed_on_save(self) -> None:
        guard = AnttimeRateGuard(self.state_path, per_minute=100, per_hour=100)
        old_ts = (self.now - timedelta(hours=2)).timestamp()
        # 古いイベントを直接書き込む
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps({"events": [old_ts]}), encoding="utf-8")
        guard.check_and_record(self.now)
        # 保存後に古いイベントが消えていること
        data = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertNotIn(old_ts, data["events"])


if __name__ == "__main__":
    unittest.main()
