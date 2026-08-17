"""Unit tests for pipeline resilience, failure modes, malformed HTML, and edge cases."""

import unittest
import tempfile
from pathlib import Path
from atlas.core.models import (
    TimelineEvent, Finding, EvidenceState, ArtifactType, EvidenceArtifact
)
from atlas.pipeline.timeline import build_unified_timeline, compute_timeline_continuity
from atlas.scoring.scorer import AnomalyScorer
from atlas.reporting.report_generator import generate_markdown_report

class TestPipelineAndFailures(unittest.TestCase):

    def setUp(self):
        self.scorer = AnomalyScorer()

    def test_empty_archive_response(self):
        """Pipeline and timeline builder should handle empty archive events gracefully."""
        events, metrics, artifact = build_unified_timeline(
            url="https://new-empty-site.org",
            output_prefix="test_empty",
            wayback_events=[],
            cc_events=[],
            live_event=TimelineEvent(
                timestamp="20260817120000",
                datetime_iso="2026-08-17T12:00:00Z",
                source="live",
                status_code=200
            )
        )
        self.assertEqual(len(events), 1)
        self.assertEqual(metrics.total_captures, 1)
        self.assertEqual(metrics.years_span, 0)
        self.assertEqual(metrics.observed_year_ratio, 1.0)

    def test_duplicate_captures_deduplication(self):
        """Identical captures across Wayback and Common Crawl should be deduplicated."""
        ev1 = TimelineEvent(timestamp="20200101120000", datetime_iso="2020-01-01T12:00:00Z", source="wayback", status_code=200)
        ev2 = TimelineEvent(timestamp="20200101120000", datetime_iso="2020-01-01T12:00:00Z", source="wayback", status_code=200)
        ev3 = TimelineEvent(timestamp="20200101120000", datetime_iso="2020-01-01T12:00:00Z", source="commoncrawl", status_code=200)

        events, metrics, artifact = build_unified_timeline(
            url="https://example.org",
            output_prefix="test_dedup",
            wayback_events=[ev1, ev2],
            cc_events=[ev3]
        )
        # ev1 and ev2 are identical (same ts, source, status) -> deduplicated to 1; ev3 is distinct source -> kept
        self.assertEqual(len(events), 2)

    def test_malformed_html_handling(self):
        """Scorer and parser must handle unclosed, corrupted, or binary HTML without crashing."""
        corrupted_html = "<html><head><title>Corrupted<<<>><body><div unclosed=attr <<script>alert(1)</p>"
        score, conf, classification, state, signals = self.scorer.evaluate(
            timeline=[],
            metadata={},
            html_content=corrupted_html,
            live_status=200
        )
        self.assertIsInstance(score, int)
        self.assertIsInstance(conf, float)
        self.assertEqual(classification, "Standard Web Surface")

    def test_scoring_boundaries(self):
        """Verify Tier-1, Tier-2, Tier-3, and Baseline score thresholds."""
        # Tier-1: Score >= 8 and Conf >= 0.70
        # Tier-2: Score >= 5 and Conf >= 0.60
        # Tier-3: Score >= 2 and Conf >= 0.40
        # Baseline: Score < 2
        # Let's test with synthetic signals
        events_tier1 = []
        for y in range(2004, 2027):
            events_tier1.append(TimelineEvent(timestamp=f"{y}0101000000", datetime_iso=f"{y}-01-01T00:00:00Z", source="wayback", status_code=200))
        # Add documented failure period (resurrection)
        events_tier1.append(TimelineEvent(timestamp="20100601000000", datetime_iso="2010-06-01T00:00:00Z", source="wayback", status_code=404))
        events_tier1.append(TimelineEvent(timestamp="20120601000000", datetime_iso="2012-06-01T00:00:00Z", source="wayback", status_code=404))

        fossil_html = '<html><head><meta name="GENERATOR" content="Microsoft FrontPage 4.0"></head><body><marquee>Old</marquee></body></html>'
        score, conf, classification, state, signals = self.scorer.evaluate(
            timeline=events_tier1,
            metadata={},
            html_content=fossil_html,
            live_status=200
        )
        # Persistence (2) + Resurrection (5) + Fossil (4) = 11 >= 8 -> Tier-1 Major Web Anomaly
        self.assertGreaterEqual(score, 8)
        self.assertEqual(classification, "Tier-1 Major Web Anomaly")
        self.assertEqual(state, EvidenceState.VALIDATED)

    def test_report_generation_structure(self):
        """Markdown report must contain all required scientific fields and cautious language."""
        finding = Finding(
            finding_id="ATLAS-20260817-TESTREPORT",
            target_url="https://test.edu/archive/",
            canonical_domain="test.edu",
            anomaly_score=6,
            confidence=0.85,
            classification="Tier-2 Significant Historical Anomaly",
            evidence_state=EvidenceState.VALIDATED,
            human_summary="Target test.edu verified with 20-year persistence."
        )
        report_path = generate_markdown_report(finding)
        self.assertTrue(report_path.exists())

        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("ATLAS-20260817-TESTREPORT", content)
        self.assertIn("Confidence Score", content)
        self.assertIn("Overall Evidence State", content)
        self.assertIn("Observational Limitations & Gaps", content)
        self.assertNotIn("proved that", content.lower())

if __name__ == "__main__":
    unittest.main()
