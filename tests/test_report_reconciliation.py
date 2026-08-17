"""Test suite for Report Reconciliation and Scientific Release Gate."""

import json
import pytest
from pathlib import Path
from atlas.research.release_gate import run_scientific_release_check

def test_release_check_passes():
    passed, report = run_scientific_release_check()
    assert passed is True
    assert report["scientific_release"] == "APPROVED"
    assert report["checks"]["dataset_integrity"] == "PASS"
    assert report["checks"]["prediction_evaluation_consistency"] == "PASS"
    assert report["checks"]["report_consistency"] == "PASS"
    assert report["checks"]["scoring_replay"] == "PASS"
    assert report["checks"]["simulation_containment"] == "PASS"

def test_report_matches_evaluation_json():
    eval_file = Path("data/benchmark_v2/evaluation.json")
    report_file = Path("reports/BENCHMARK_V2_RESULTS.md")

    assert eval_file.exists()
    assert report_file.exists()

    with open(eval_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    cm = eval_data["confusion_matrix"]
    metrics = eval_data["metrics"]

    report_text = report_file.read_text(encoding="utf-8")

    # Verify key metrics are present and match
    assert f"**{metrics['accuracy']*100:.2f}%**" in report_text or f"{metrics['accuracy']*100:.2f}%" in report_text
    assert f"**{metrics['precision']*100:.2f}%**" in report_text or f"{metrics['precision']*100:.2f}%" in report_text
