"""Unit tests for Phase 1 Ranking, Near-Misses, and Metrics."""

import unittest
import tempfile
import json
from pathlib import Path
from atlas.phase1.ranking import generate_candidate_rankings
from atlas.phase1.metrics import compute_phase1_metrics

class TestPhase1RankingAndMetrics(unittest.TestCase):

    def test_ranking_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir) / "data"
            reports_dir = Path(tmpdir) / "reports"
            data_dir.mkdir()
            reports_dir.mkdir()

            # Mock scan_results.jsonl
            scan_file = data_dir / "scan_results.jsonl"
            mock_records = [
                {"domain": "stanford.edu", "category": "Universities", "anomaly_score": 6, "confidence": 0.88, "classification": "Tier-2", "evidence_state": "VALIDATED", "signals": [{"name": "15+ Year Web Persistence", "score_awarded": 2}], "timeline_metrics": {"years_span": 25, "observed_year_ratio": 0.85, "continuity_claim": "verified"}},
                {"domain": "mit.edu", "category": "Universities", "anomaly_score": 4, "confidence": 0.75, "classification": "Tier-3", "evidence_state": "CANDIDATE", "signals": [{"name": "15+ Year Web Persistence", "score_awarded": 1}], "timeline_metrics": {"years_span": 25, "observed_year_ratio": 0.50, "continuity_claim": "moderate"}},
                {"domain": "modern-site.com", "category": "Companies", "anomaly_score": 0, "confidence": 0.95, "classification": "Standard Web Surface", "evidence_state": "OBSERVED", "signals": [], "timeline_metrics": {}}
            ]
            with open(scan_file, "w", encoding="utf-8") as f:
                for r in mock_records:
                    f.write(json.dumps(r) + "\n")

            import atlas.phase1.ranking as rk
            old_scan = rk.SCAN_RESULTS_JSONL
            old_rep = rk.PHASE1_REPORTS_DIR
            rk.SCAN_RESULTS_JSONL = scan_file
            rk.PHASE1_REPORTS_DIR = reports_dir

            try:
                reports = generate_candidate_rankings()
                self.assertIn("top_100", reports)
                self.assertTrue((reports_dir / "TOP_100_CANDIDATES.md").exists())
                self.assertTrue((reports_dir / "ZERO_SCORE_SUMMARY.md").exists())
            finally:
                rk.SCAN_RESULTS_JSONL = old_scan
                rk.PHASE1_REPORTS_DIR = old_rep

if __name__ == "__main__":
    unittest.main()
