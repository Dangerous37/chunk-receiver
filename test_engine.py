import json
import subprocess
import sys
import unittest
from pathlib import Path

from engine import evaluate


def example():
    return json.loads(Path(__file__).with_name("example.json").read_text(encoding="utf-8"))


class AcceptanceTests(unittest.TestCase):
    def test_example_cli(self):
        proc = subprocess.run([sys.executable, "cli.py", "example.json"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), evaluate(example()))

    def test_resume_and_conflicting_retry(self):
        import tempfile
        data = example()
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "chunks.db"
            first = dict(data, chunks=data["chunks"][:1])
            self.assertEqual(evaluate(first, db)["missing"], [0])
            self.assertEqual(evaluate(first, db)["missing"], [0])
            with self.assertRaisesRegex(ValueError, "conflict"):
                evaluate(dict(data, chunks=[{"index":1,"base64":"eg=="}]), db)
            self.assertEqual(evaluate(dict(data, chunks=data["chunks"][1:]), db)["base64"], "YWJj")

    def test_corruption_rejected_before_emitting_bytes(self):
        data = example()
        data["chunks"][0]["base64"] = "eg=="
        with self.assertRaisesRegex(ValueError, "digest"):
            evaluate(data)
