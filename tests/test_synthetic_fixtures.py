"""Synthetic edge case fixture tests verifying exact evidence state assignments."""

import unittest
from atlas.core.models import TimelineEvent, EvidenceState, ContinuityLevel
from atlas.pipeline.timeline import compute_timeline_continuity
from atlas.scoring.scorer import AnomalyScorer

class TestSyntheticFixtures(unittest.TestCase):

    def setUp(self):
        self.scorer = AnomalyScorer()

    def test_case_a_sparse_two_point_timeline(self):
        """Case A: Capture in 2001 and 2026 only with no intermediate data -> INSUFFICIENT, Score 0."""
        events = [
            TimelineEvent(timestamp="20010510120000", datetime_iso="2001-05-10T12:00:00Z", source="wayback", status_code=200),
            TimelineEvent(timestamp="20260817180000", datetime_iso="2026-08-17T18:00:00Z", source="live", status_code=200)
        ]
        metrics = compute_timeline_continuity(events)
        self.assertEqual(metrics.continuity_level, ContinuityLevel.HISTORICAL_PRESENCE)
        self.assertEqual(metrics.observed_year_ratio, 0.077)  # 2 years out of 26
        self.assertEqual(metrics.longest_evidence_gap_years, 25.25)

        score, conf, classification, state, signals = self.scorer.evaluate(
            timeline=events,
            metadata={},
            html_content="<html><body>Test</body></html>",
            live_status=200,
            timeline_metrics=metrics
        )
        self.assertEqual(score, 0)
        p_sig = [s for s in signals if s.signal_id == "persistence_15yr"][0]
        self.assertEqual(p_sig.evidence_state, EvidenceState.INSUFFICIENT)
        self.assertEqual(p_sig.score_awarded, 0)

    def test_case_b_documented_failure_resurrection(self):
        """Case B: Active 2008-2010, Documented 404s 2011-2016, Active return 2018-2026 -> VALIDATED Resurrection (+5)."""
        events = [
            TimelineEvent(timestamp="20080601000000", datetime_iso="2008-06-01T00:00:00Z", source="wayback", status_code=200),
            TimelineEvent(timestamp="20100801000000", datetime_iso="2010-08-01T00:00:00Z", source="wayback", status_code=200),
            TimelineEvent(timestamp="20120501000000", datetime_iso="2012-05-01T00:00:00Z", source="wayback", status_code=404),
            TimelineEvent(timestamp="20150301000000", datetime_iso="2015-03-01T00:00:00Z", source="wayback", status_code=404),
            TimelineEvent(timestamp="20180901000000", datetime_iso="2018-09-01T00:00:00Z", source="wayback", status_code=200),
            TimelineEvent(timestamp="20260817000000", datetime_iso="2026-08-17T00:00:00Z", source="live", status_code=200),
        ]
        score, conf, classification, state, signals = self.scorer.evaluate(
            timeline=events,
            metadata={},
            html_content="<html><body>Resurrected Domain</body></html>",
            live_status=200
        )
        res_sig = [s for s in signals if s.signal_id == "resurrection"][0]
        self.assertEqual(res_sig.evidence_state, EvidenceState.VALIDATED)
        self.assertEqual(res_sig.score_awarded, 5)
        self.assertGreaterEqual(res_sig.confidence, 0.85)

    def test_case_c_archive_gap_without_failures_is_not_resurrection(self):
        """Case C: Long archive gap with NO failure records must NOT trigger resurrection (+0)."""
        events = [
            TimelineEvent(timestamp="20050101000000", datetime_iso="2005-01-01T00:00:00Z", source="wayback", status_code=200),
            TimelineEvent(timestamp="20200101000000", datetime_iso="2020-01-01T00:00:00Z", source="wayback", status_code=200),
            TimelineEvent(timestamp="20260101000000", datetime_iso="2026-01-01T00:00:00Z", source="live", status_code=200)
        ]
        score, conf, classification, state, signals = self.scorer.evaluate(
            timeline=events,
            metadata={},
            html_content="<html><body>Gap Page</body></html>",
            live_status=200
        )
        res_sig = [s for s in signals if s.signal_id == "resurrection"][0]
        self.assertEqual(res_sig.evidence_state, EvidenceState.INSUFFICIENT)
        self.assertEqual(res_sig.score_awarded, 0)

    def test_case_d_active_technology_fossil(self):
        """Case D: Real HTML with active frameset and FrontPage meta tag -> VALIDATED fossil (+4)."""
        html = """<html>
<head>
    <meta name="GENERATOR" content="Microsoft FrontPage 3.0">
    <title>Active 1998 Frameset</title>
</head>
<frameset cols="20%,80%">
    <frame src="menu.html" name="menu">
    <frame src="main.html" name="main">
</frameset>
</html>"""
        score, conf, classification, state, signals = self.scorer.evaluate(
            timeline=[],
            metadata={},
            html_content=html,
            live_status=200
        )
        fossil_sig = [s for s in signals if s.signal_id == "technology_fossil"][0]
        self.assertEqual(fossil_sig.evidence_state, EvidenceState.VALIDATED)
        self.assertEqual(fossil_sig.score_awarded, 4)
        self.assertGreaterEqual(fossil_sig.confidence, 0.85)

    def test_case_e_dense_continuous_presence(self):
        """Case E: Dense historical timeline (yearly captures from 2004 to 2026) -> CONTINUOUS_PRESENCE / VALIDATED (+2)."""
        events = []
        for year in range(2004, 2027):
            for month in (1, 6):
                ts = f"{year}{month:02d}01120000"
                events.append(TimelineEvent(
                    timestamp=ts,
                    datetime_iso=f"{year}-{month:02d}-01T12:00:00Z",
                    source="wayback",
                    status_code=200
                ))
        metrics = compute_timeline_continuity(events)
        self.assertEqual(metrics.continuity_level, ContinuityLevel.CONTINUOUS_PRESENCE)
        self.assertGreaterEqual(metrics.observed_year_ratio, 0.95)

        score, conf, classification, state, signals = self.scorer.evaluate(
            timeline=events,
            metadata={},
            html_content="<html><body>Dense History</body></html>",
            live_status=200,
            timeline_metrics=metrics
        )
        p_sig = [s for s in signals if s.signal_id == "persistence_15yr"][0]
        self.assertEqual(p_sig.evidence_state, EvidenceState.VALIDATED)
        self.assertEqual(p_sig.score_awarded, 2)
        self.assertGreaterEqual(p_sig.confidence, 0.90)

if __name__ == "__main__":
    unittest.main()
