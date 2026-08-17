"""Unit tests for Anomaly Scorer."""

import unittest
from atlas.core.models import TimelineEvent
from atlas.scoring.scorer import AnomalyScorer

class TestAnomalyScorer(unittest.TestCase):

    def setUp(self):
        self.scorer = AnomalyScorer()

    def test_persistence_signal(self):
        events = [
            TimelineEvent(timestamp="20010101000000", datetime_iso="2001-01-01T00:00:00Z", source="wayback", status_code=200),
            TimelineEvent(timestamp="20260101000000", datetime_iso="2026-01-01T00:00:00Z", source="live", status_code=200)
        ]
        score, classification, signals = self.scorer.evaluate(
            timeline=events,
            metadata={},
            html_content="<html><body>Standard modern content</body></html>",
            live_status=200
        )
        signal_ids = [s.signal_id for s in signals]
        self.assertIn("persistence_15yr", signal_ids)
        self.assertGreaterEqual(score, 2)

    def test_technology_fossil_detection(self):
        html = '<html><head><meta name="GENERATOR" content="Microsoft FrontPage 4.0"></head><body><marquee>Old Web</marquee></body></html>'
        score, classification, signals = self.scorer.evaluate(
            timeline=[],
            metadata={},
            html_content=html,
            live_status=200
        )
        signal_ids = [s.signal_id for s in signals]
        self.assertIn("technology_fossil", signal_ids)
        self.assertGreaterEqual(score, 4)

    def test_open_directory_detection(self):
        html = '<html><head><title>Index of /archive/1998</title></head><body><h1>Index of /archive/1998</h1></body></html>'
        score, classification, signals = self.scorer.evaluate(
            timeline=[],
            metadata={},
            html_content=html,
            live_status=200
        )
        signal_ids = [s.signal_id for s in signals]
        self.assertIn("forgotten_archive", signal_ids)
        self.assertGreaterEqual(score, 3)

if __name__ == "__main__":
    unittest.main()
