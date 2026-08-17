"""Unit tests for Phase 1 Evidence Freezing and cryptographic immutability."""

import unittest
import tempfile
import json
import hashlib
from pathlib import Path
from atlas.phase1.freezer import freeze_collected_evidence

class TestPhase1Freezer(unittest.TestCase):

    def test_evidence_freezing_manifest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_dir = Path(tmpdir) / "raw"
            frozen_dir = Path(tmpdir) / "frozen"
            raw_dir.mkdir()
            frozen_dir.mkdir()

            # Create mock domain directory with files
            d1_dir = raw_dir / "example_edu"
            d1_dir.mkdir()
            (d1_dir / "rendered.html").write_text("<html>Mock HTML</html>", encoding="utf-8")
            (d1_dir / "timeline.json").write_text('{"events": []}', encoding="utf-8")

            # Monkey-patch config paths for testing
            import atlas.phase1.freezer as fz
            old_raw = fz.PHASE1_RAW_EVIDENCE_DIR
            old_frozen = fz.PHASE1_FROZEN_DIR
            fz.PHASE1_RAW_EVIDENCE_DIR = raw_dir
            fz.PHASE1_FROZEN_DIR = frozen_dir

            try:
                manifest_path = freeze_collected_evidence()
                self.assertTrue(manifest_path.exists())

                with open(manifest_path, "r", encoding="utf-8") as mf:
                    data = json.load(mf)

                self.assertEqual(data["state"], "FROZEN")
                self.assertEqual(data["total_domains_frozen"], 1)
                self.assertEqual(data["total_artifacts_frozen"], 2)
                self.assertIn("example_edu", data["domain_manifests"])
            finally:
                fz.PHASE1_RAW_EVIDENCE_DIR = old_raw
                fz.PHASE1_FROZEN_DIR = old_frozen

if __name__ == "__main__":
    unittest.main()
