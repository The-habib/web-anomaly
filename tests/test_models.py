"""Unit tests for Atlas data models."""

import unittest
from atlas.core.models import (
    ArtifactType, EvidenceArtifact, TimelineEvent, AnomalySignal, Finding, Experiment, ExperimentStatus
)

class TestAtlasModels(unittest.TestCase):

    def test_evidence_artifact_creation(self):
        art = EvidenceArtifact(
            artifact_id="art_001",
            artifact_type=ArtifactType.SCREENSHOT,
            relative_path="evidence/screenshots/test.png",
            file_name="test.png",
            sha256="abc12345",
            size_bytes=1024
        )
        self.assertEqual(art.artifact_type, ArtifactType.SCREENSHOT)
        self.assertEqual(art.size_bytes, 1024)

    def test_timeline_event_creation(self):
        ev = TimelineEvent(
            timestamp="20050101120000",
            datetime_iso="2005-01-01T12:00:00Z",
            source="wayback",
            status_code=200,
            content_length=5000,
            mime_type="text/html"
        )
        self.assertEqual(ev.status_code, 200)
        self.assertEqual(ev.source, "wayback")

    def test_finding_serialization(self):
        finding = Finding(
            finding_id="ATLAS-20260817-TEST001",
            target_url="https://example.com",
            canonical_domain="example.com",
            anomaly_score=5,
            classification="Tier-2 Significant Historical Anomaly",
            human_summary="Test human summary."
        )
        data = finding.model_dump()
        self.assertEqual(data["finding_id"], "ATLAS-20260817-TEST001")
        self.assertEqual(data["anomaly_score"], 5)

    def test_experiment_model(self):
        exp = Experiment(
            experiment_id="0001",
            title="Test Experiment",
            hypothesis="Testing persistence of static pages."
        )
        self.assertEqual(exp.status, ExperimentStatus.PROPOSED)
        self.assertEqual(exp.experiment_id, "0001")

if __name__ == "__main__":
    unittest.main()
