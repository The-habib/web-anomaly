"""Unit tests for Phase 1 Seed Corpus generation and reproducibility."""

import unittest
import tempfile
import csv
from pathlib import Path
from atlas.phase1.corpus import generate_seed_corpus, normalize_domain

class TestPhase1Corpus(unittest.TestCase):

    def test_normalize_domain(self):
        self.assertEqual(normalize_domain("https://WWW.Example.COM/path/"), "www.example.com")
        self.assertEqual(normalize_domain("HTTP://Stanford.EDU:8080"), "stanford.edu")
        self.assertEqual(normalize_domain("  mit.edu  "), "mit.edu")

    def test_deterministic_seed_reproducibility(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out1 = Path(tmpdir) / "c1.csv"
            out2 = Path(tmpdir) / "c2.csv"

            dist = {"Universities": 10, "Government": 10}
            recs1, _ = generate_seed_corpus(seed=42, target_distribution=dist, output_path=out1)
            recs2, _ = generate_seed_corpus(seed=42, target_distribution=dist, output_path=out2)

            self.assertEqual(len(recs1), 20)
            self.assertEqual(len(recs2), 20)
            # Exact deterministic equality
            self.assertEqual([r["domain"] for r in recs1], [r["domain"] for r in recs2])

    def test_corpus_distribution_quotas(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "test_corpus.csv"
            dist = {
                "Universities": 20,
                "Government": 20,
                "Nonprofits": 15,
                "Long-running companies": 15,
                "Open-source/project sites": 15,
                "Personal/independent sites": 15
            }
            recs, _ = generate_seed_corpus(seed=99, target_distribution=dist, output_path=out)
            self.assertEqual(len(recs), 100)

            # Check category counts in CSV
            counts = {}
            with open(out, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    c = row["category"]
                    counts[c] = counts.get(c, 0) + 1

            for cat, expected in dist.items():
                self.assertEqual(counts.get(cat), expected)

if __name__ == "__main__":
    unittest.main()
