"""Comprehensive unit tests for Pilot and Benchmark Subsystems."""

import pytest
from pathlib import Path
from atlas.pilot.config import PilotConfig
from atlas.pilot.sampler import sample_pilot_corpus
from atlas.pilot.runner import run_pilot_scan
from atlas.pilot.scoring import score_pilot_evidence, score_single_evidence
from atlas.pilot.review import generate_blind_dossiers, record_human_review
from atlas.pilot.benchmark_runner import run_benchmark_v1_evaluation
from atlas.provenance.builder import build_benchmark_v1

def test_pilot_sampler_distribution():
    config = PilotConfig()
    records, csv_p, prov_p = sample_pilot_corpus(config)

    assert len(records) == 200
    assert csv_p.exists()
    assert prov_p.exists()

    cat_counts = {}
    for r in records:
        cat_counts[r.category] = cat_counts.get(r.category, 0) + 1

    assert cat_counts["Universities"] == 40
    assert cat_counts["Government"] == 40
    assert cat_counts["Nonprofits"] == 30
    assert cat_counts["Long-running companies"] == 30
    assert cat_counts["Open-source/project sites"] == 30
    assert cat_counts["Personal/independent sites"] == 30

def test_pilot_scan_and_checkpoints(tmp_path):
    config = PilotConfig(
        output_dir=tmp_path / "pilot_test",
        evidence_path=tmp_path / "pilot_test" / "evidence",
        checkpoints_path=tmp_path / "pilot_test" / "checkpoints"
    )
    records, _, _ = sample_pilot_corpus(config)
    evidence, manifest = run_pilot_scan(records[:20], config, resume=False, mode="SIMULATION")

    assert len(evidence) == 20
    assert manifest.total_pilot_domains == 20
    assert manifest.batch_count >= 1

def test_pilot_scoring():
    config = PilotConfig()
    records, _, _ = sample_pilot_corpus(config)
    evidence, _ = run_pilot_scan(records, config, resume=True)
    scores, score_p = score_pilot_evidence(evidence, config)

    assert len(scores) == 200
    assert score_p.exists()
    for s in scores:
        assert 0.0 <= s.raw_anomaly_score <= 100.0
        assert 0.0 <= s.confidence <= 1.0
        assert s.classification in ("ORDINARY", "CANDIDATE_ANOMALY", "HIGH_ANOMALY")

def test_blind_dossier_score_hiding():
    config = PilotConfig()
    records, _, _ = sample_pilot_corpus(config)
    evidence, _ = run_pilot_scan(records, config, resume=True)
    scores, _ = score_pilot_evidence(evidence, config)
    dossiers, dos_p = generate_blind_dossiers(evidence, scores, config)

    assert len(dossiers) == 20
    assert dos_p.exists()

    # Verify score-hiding: model should NOT contain score, rank, or triggered_rules
    for d in dossiers:
        d_dict = d.model_dump()
        assert "raw_anomaly_score" not in d_dict
        assert "anomaly_score" not in d_dict
        assert "rank" not in d_dict
        assert "triggered_rules" not in d_dict

def test_human_reviews_recording():
    config = PilotConfig()
    records, _, _ = sample_pilot_corpus(config)
    evidence, _ = run_pilot_scan(records, config, resume=True)
    scores, _ = score_pilot_evidence(evidence, config)
    dossiers, _ = generate_blind_dossiers(evidence, scores, config)
    reviews, rev_p = record_human_review(dossiers, scores, config)

    assert len(reviews) == 20
    assert rev_p.exists()
    for r in reviews:
        assert r.blind_verdict in ("REAL_ANOMALY", "ORDINARY_FOSSIL", "ORDINARY_MODERN", "ARCHIVE_ARTIFACT", "INCONCLUSIVE")
        assert r.confidence in ("HIGH", "MEDIUM", "LOW")

def test_benchmark_v1_evaluation(tmp_path):
    from atlas.pilot.benchmark_runner import run_benchmark_v2_evaluation, build_benchmark_v2
    test_bench_dir = tmp_path / "test_benchmark"
    build_benchmark_v2(test_bench_dir)
    eval_res = run_benchmark_v2_evaluation(benchmark_dir=test_bench_dir, mode="SIMULATION")

    assert eval_res["total_domains"] == 30
    assert "accuracy" in eval_res["metrics"]
    assert "precision" in eval_res["metrics"]
    assert "confusion_matrix" in eval_res
