import importlib.util
import json
import os
import stat
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "golf-oclock"
    / "scripts"
    / "golfoclock.py"
)
SPEC = importlib.util.spec_from_file_location("golfoclock", SCRIPT)
golfoclock = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(golfoclock)


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, route, body):
        self.calls.append((route, body))
        return self.responses.pop(0)


class GolfOClockTests(unittest.TestCase):
    def test_normalize_origin(self):
        self.assertEqual(
            golfoclock.normalize_api_root("https://example.golfoclock.com/"),
            "https://example.golfoclock.com/api/api-o-clock",
        )

    def test_rejects_non_https_base_url(self):
        with self.assertRaises(golfoclock.ConfigurationError):
            golfoclock.normalize_api_root("http://example.golfoclock.com")

    def test_environment_key_takes_precedence(self):
        with patch.dict(os.environ, {"GOLFOCLOCK_API_KEY": " env-secret "}):
            self.assertEqual(golfoclock.load_api_key(), "env-secret")

    def test_rejects_reverse_date_range(self):
        with self.assertRaises(golfoclock.ConfigurationError):
            golfoclock.validate_date_range(date(2026, 8, 2), date(2026, 8, 1))

    def test_reservation_pagination(self):
        client = FakeClient(
            [
                {"reservations": [{"id": "r1"}], "nextCursor": "cursor-1"},
                {"reservations": [{"id": "r2"}], "nextCursor": None},
            ]
        )
        result = golfoclock.fetch_reservations(
            client, date(2026, 8, 1), date(2026, 8, 2), "confirmed", 500
        )
        self.assertEqual(result["count"], 2)
        self.assertFalse(result["truncated"])
        self.assertEqual(client.calls[1][1]["startAfter"], "cursor-1")
        self.assertEqual(
            client.calls[0][1]["filters"][-1], ["status", "==", "confirmed"]
        )

    def test_reservation_cap_reports_truncation(self):
        client = FakeClient(
            [{"reservations": [{"id": "r1"}], "nextCursor": "cursor-1"}]
        )
        result = golfoclock.fetch_reservations(
            client, date(2026, 8, 1), date(2026, 8, 1), None, 1
        )
        self.assertTrue(result["truncated"])

    def test_rejects_non_allowlisted_route(self):
        client = golfoclock.Client("secret", "https://example.golfoclock.com")
        with self.assertRaises(golfoclock.ConfigurationError):
            client.post("RESERVATIONS/create", {})

    def test_written_output_is_owner_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "nested" / "result.json"
            golfoclock.write_result({"ok": True}, output, compact=False)
            self.assertEqual(json.loads(output.read_text()), {"ok": True})
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)


if __name__ == "__main__":
    unittest.main()
