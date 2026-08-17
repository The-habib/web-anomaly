"""Unit tests for Phase 1 Checkpointing and Resumability."""

import unittest
import tempfile
import json
from pathlib import Path
from atlas.phase1.scanner import get_completed_domains

class TestPhase1Resumability(unittest.TestCase):

    def test_checkpoint_recovery(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ckpt_dir = Path(tmpdir) / "checkpoints"
            ckpt_dir.mkdir()

            # Mock batch 1
            b1 = ckpt_dir / "batch-001.json"
            with open(b1, "w", encoding="utf-8") as f:
                json.dump({
                    "batch_id": "batch-001",
                    "completed_domains": ["harvard.edu", "mit.edu", "stanford.edu"]
                }, f)

            # Mock batch 2
            b2 = ckpt_dir / "batch-002.json"
            with open(b2, "w", encoding="utf-8") as f:
                json.dump({
                    "batch_id": "batch-002",
                    "completed_domains": ["nasa.gov", "nih.gov"]
                }, f)

            import atlas.phase1.scanner as sc
            old_ckpt = sc.PHASE1_CHECKPOINTS_DIR
            sc.PHASE1_CHECKPOINTS_DIR = ckpt_dir

            try:
                completed = get_completed_domains()
                self.assertEqual(len(completed), 5)
                self.assertIn("harvard.edu", completed)
                self.assertIn("nasa.gov", completed)
            finally:
                sc.PHASE1_CHECKPOINTS_DIR = old_ckpt

if __name__ == "__main__":
    unittest.main()
