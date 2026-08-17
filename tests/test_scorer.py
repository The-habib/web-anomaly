"""Unit tests for Anomaly Scorer (Phase 0.5)."""

import unittest
from atlas.core.models import TimelineEvent, EvidenceState
from atlas.pipeline.timeline import compute_timeline_continuity
from atlas.scoring.scorer import AnomalyScorer

class TestAnomalyScorer(unittest.TestCase):

    def setUp(self):
        self.scorer = AnomalyScorer()

    def test_persistence_signal_dense(self):
        # 16 yearly captures from 2005 to 2026
        events = []
        for y in range(2005, 2027):
            events.append(TimelineEvent(
                timestamp=f"{y}0101000000",
                datetime_iso=f"{y}-01-01T00:00:00Z",
                source="wayback",
                status_code=200
            ))
        metrics = compute_timeline_continuity(events)
        score, conf, classification, state, signals = self.scorer.evaluate(
            timeline=events,
            metadata={},
            html_content="<html><body>Standard modern content</body></html>",
            live_status=200,
            timeline_metrics=metrics
        )
        signal_ids = [s.signal_id for s in signals]
        self.assertIn("persistence_15yr", signal_ids)
        self.assertGreaterEqual(score, 2)
        self.assertIn(state, (EvidenceState.VALIDATED, EvidenceState.CANDIDATE))

    def test_technology_fossil_detection(self):
        html = '<html><head><meta name="GENERATOR" content="Microsoft FrontPage 4.0"></head><body><marquee>Active Marquee</marquee></body></html>'
        score, conf, classification, state, signals = self.scorer.evaluate(
            timeline=[],
            metadata={},
            html_content=html,
            live_status=200
        )
        signal_ids = [s.signal_id for s in signals]
        self.assertIn("technology_fossil", signal_ids)
        self.assertGreaterEqual(score, 4)
        self.assertEqual(state, EvidenceState.VALIDATED)

    def test_open_directory_with_historical_files(self):
        html = '''<html><head><title>Index of /archive/1998</title></head>
<body><h1>Index of /archive/1998</h1>
<pre><a href="source.tar.gz">source.tar.gz</a>  1998-05-12 10:00  1.2M</pre>
</body></html>'''
        score, conf, classification, state, signals = self.scorer.evaluate(
            timeline=[],
            metadata={},
            html_content=html,
            live_status=200
        )
        signal_ids = [s.signal_id for s in signals]
        self.assertIn("forgotten_archive", signal_ids)
        self.assertGreaterEqual(score, 3)
        self.assertEqual(state, EvidenceState.VALIDATED)

if __name__ == "__main__":
    unittest.main()
