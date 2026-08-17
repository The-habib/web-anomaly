"""Permanent reconciliation and consistency test suite for Phase 1.1."""

import unittest
import csv
import json
import hashlib
from pathlib import Path
from collections import Counter

from atlas.scoring.scorer import AnomalyScorer
from atlas.core.models import TimelineEvent, TimelineContinuityMetrics

class TestPhase11Audit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root_dir = Path(__file__).resolve().parent.parent
        cls.data_dir = cls.root_dir / "data"
        cls.evidence_dir = cls.root_dir / "experiments" / "0002" / "evidence"

    def test_corpus_count_reconciliation(self):
        """Corpus CSV must contain exactly 1,000 rows and 1,000 unique domains."""
        corpus_path = self.data_dir / "seed_corpus.csv"
        self.assertTrue(corpus_path.exists())

        with open(corpus_path, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

        self.assertEqual(len(reader), 1000)
        unique_domains = set(r["domain"] for r in reader)
        self.assertEqual(len(unique_domains), 1000)

    def test_review_count_and_verdict_reconciliation(self):
        """Human review dataset must contain exactly 23 persisted reviews matching reconciled totals."""
        reviews_path = self.data_dir / "human_reviews.jsonl"
        self.assertTrue(reviews_path.exists())

        reviews = []
        with open(reviews_path, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    reviews.append(json.loads(l))

        self.assertEqual(len(reviews), 23)
        verdicts = Counter(r.get("human_verdict") for r in reviews)
        self.assertEqual(verdicts["POTENTIAL_ANOMALY"], 2)
        self.assertEqual(verdicts["ORDINARY"], 20)
        self.assertEqual(verdicts["FALSE_NEGATIVE_CANDIDATE"], 1)
        self.assertEqual(verdicts.get("FALSE_POSITIVE", 0), 0)

    def test_candidate_score_replay_determinism(self):
        """Score replay against frozen dossiers must deterministically reproduce candidate scores."""
        scorer = AnomalyScorer()
        expected_scores = {
            "tilde.town": (4, 0.86),
            "tilde.club": (4, 0.86),
            "cmu.edu": (2, 0.48)
        }

        for domain, (exp_score, exp_conf) in expected_scores.items():
            slug = domain.replace(":", "_").replace("/", "_").replace(".", "_")
            domain_dir = self.evidence_dir / "raw" / slug
            self.assertTrue(domain_dir.exists(), f"Missing raw directory for {domain}")

            html_content = ""
            if (domain_dir / "rendered.html").exists():
                with open(domain_dir / "rendered.html", "r", encoding="utf-8", errors="replace") as hf:
                    html_content = hf.read()

            with open(domain_dir / "raw_bundle.json", "r", encoding="utf-8") as f:
                bundle = json.load(f)
            with open(domain_dir / "timeline.json", "r", encoding="utf-8") as tf:
                tl_data = json.load(tf)

            events = [TimelineEvent(**e) for e in tl_data.get("events", [])]
            tl_metrics = TimelineContinuityMetrics(**tl_data["metrics"]) if "metrics" in tl_data else None

            score, conf, _, _, _ = scorer.evaluate(
                timeline=events,
                metadata=bundle.get("live_evidence", {}).get("metadata", {}),
                html_content=html_content,
                live_status=bundle.get("live_evidence", {}).get("status_code", 200),
                timeline_metrics=tl_metrics
            )

            self.assertEqual(score, exp_score, f"Score mismatch for {domain}")
            self.assertEqual(round(conf, 2), exp_conf, f"Confidence mismatch for {domain}")

    def test_provenance_completeness(self):
        """All 1,000 domains must have a complete provenance record."""
        prov_path = self.data_dir / "corpus_provenance.jsonl"
        self.assertTrue(prov_path.exists())

        prov_records = []
        with open(prov_path, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    prov_records.append(json.loads(l))

        self.assertEqual(len(prov_records), 1000)
        synthetic_count = sum(1 for r in prov_records if r.get("provenance_state") == "SYNTHETIC")
        real_count = sum(1 for r in prov_records if r.get("provenance_state") in ("PUBLIC_DATASET", "PUBLIC_DIRECTORY"))
        self.assertEqual(synthetic_count, 99)
        self.assertEqual(real_count, 901)

if __name__ == "__main__":
    unittest.main()
