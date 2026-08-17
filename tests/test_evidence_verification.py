"""Unit tests for Evidence Artifact verification and cryptographic integrity."""

import unittest
import tempfile
import hashlib
from pathlib import Path
from atlas.core.models import EvidenceArtifact, ArtifactType

class TestEvidenceVerification(unittest.TestCase):

    def test_sha256_integrity_match(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            test_content = b"Scientific evidence test bytes 12345"
            f.write(test_content)
            f_path = Path(f.name)

        try:
            expected_hash = hashlib.sha256(test_content).hexdigest()
            art = EvidenceArtifact(
                artifact_id="art_test_001",
                artifact_type=ArtifactType.HTML,
                relative_path=str(f_path),
                file_name=f_path.name,
                sha256=expected_hash,
                size_bytes=len(test_content)
            )

            # Read disk bytes and verify
            with open(f_path, "rb") as af:
                actual_hash = hashlib.sha256(af.read()).hexdigest()

            self.assertEqual(actual_hash, art.sha256)
        finally:
            f_path.unlink()

    def test_sha256_tampering_detection(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Original content")
            f_path = Path(f.name)

        try:
            original_hash = hashlib.sha256(b"Original content").hexdigest()
            art = EvidenceArtifact(
                artifact_id="art_test_002",
                artifact_type=ArtifactType.JSON,
                relative_path=str(f_path),
                file_name=f_path.name,
                sha256=original_hash,
                size_bytes=16
            )

            # Modify file (simulate corruption / tampering)
            with open(f_path, "wb") as af:
                af.write(b"Tampered content!")

            with open(f_path, "rb") as af:
                tampered_hash = hashlib.sha256(af.read()).hexdigest()

            self.assertNotEqual(tampered_hash, art.sha256)
        finally:
            f_path.unlink()

if __name__ == "__main__":
    unittest.main()
