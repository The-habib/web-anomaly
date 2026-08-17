"""Benchmark evaluation pipeline for Project Atlas Phase 1.2."""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone

from atlas.pilot.config import PilotConfig
from atlas.pilot.models import PilotEvidenceCapture, PilotDomainRecord
from atlas.pilot.runner import _generate_realistic_domain_evidence
from atlas.pilot.scoring import score_single_evidence
from atlas.provenance.manifest import compute_sha256

def run_benchmark_v1_evaluation(config: PilotConfig = None) -> Dict[str, Any]:
    """
    Run evaluation across all 30 Benchmark v1 reference domains.
    Measures detection performance across ordinary modern, legacy fossils,
    long-running infrastructure, and edge cases.
    """
    if config is None:
        config = PilotConfig()

    benchmark_labels_file = config.benchmark_v1_path / "labels.jsonl"
    if not benchmark_labels_file.exists():
        raise FileNotFoundError("Benchmark v1 labels file not found. Run build_benchmark_v1() first.")

    benchmark_items = []
    with open(benchmark_labels_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                benchmark_items.append(json.loads(line))

    results = []
    tp = 0  # True positive: expected POTENTIAL_ANOMALY, scored CANDIDATE/HIGH
    fp = 0  # False positive: expected ORDINARY, scored CANDIDATE/HIGH
    tn = 0  # True negative: expected ORDINARY, scored ORDINARY
    fn = 0  # False negative: expected POTENTIAL_ANOMALY, scored ORDINARY

    group_results: Dict[str, Dict[str, Any]] = {
        "ordinary_modern": {"total": 0, "correct": 0, "scores": []},
        "legacy_fossil": {"total": 0, "correct": 0, "scores": []},
        "long_running": {"total": 0, "correct": 0, "scores": []},
        "edge_case": {"total": 0, "correct": 0, "scores": []}
    }

    for item in benchmark_items:
        domain = item["domain"]
        category = item["category"]
        group = item["group_type"]
        expected = item["expected_classification"]

        # Synthetic mock domain record for evidence generator
        dummy_rec = PilotDomainRecord(
            pilot_id=item["benchmark_id"],
            domain=domain,
            category=category,
            canonical_url=item["canonical_url"],
            source_type="curated_benchmark",
            source_name="Atlas Benchmark v1",
            source_reference=item["reference_rationale"]
        )

        ev = _generate_realistic_domain_evidence(dummy_rec)
        score_rec = score_single_evidence(ev)

        is_anomaly_pred = score_rec.classification in ("HIGH_ANOMALY", "CANDIDATE_ANOMALY")
        is_anomaly_expected = (expected == "POTENTIAL_ANOMALY")

        if is_anomaly_expected and is_anomaly_pred:
            tp += 1
            is_correct = True
        elif not is_anomaly_expected and not is_anomaly_pred:
            tn += 1
            is_correct = True
        elif not is_anomaly_expected and is_anomaly_pred:
            fp += 1
            is_correct = False
        else:
            fn += 1
            is_correct = False

        group_results[group]["total"] += 1
        if is_correct:
            group_results[group]["correct"] += 1
        group_results[group]["scores"].append(score_rec.raw_anomaly_score)

        results.append({
            "benchmark_id": item["benchmark_id"],
            "domain": domain,
            "group_type": group,
            "expected_classification": expected,
            "predicted_classification": score_rec.classification,
            "raw_score": score_rec.raw_anomaly_score,
            "confidence": score_rec.confidence,
            "is_correct": is_correct,
            "triggered_rules": score_rec.triggered_rules
        })

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    accuracy = (tp + tn) / len(benchmark_items) if benchmark_items else 0.0

    eval_summary = {
        "benchmark_version": "v1.0",
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "total_domains": len(benchmark_items),
        "confusion_matrix": {
            "true_positives": tp,
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn
        },
        "metrics": {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1_score, 4),
            "specificity": round(specificity, 4),
            "false_positive_rate": round(1.0 - specificity, 4),
            "false_negative_rate": round(1.0 - recall, 4)
        },
        "group_accuracy": {
            g: {
                "total": data["total"],
                "correct": data["correct"],
                "accuracy": round(data["correct"] / data["total"], 4) if data["total"] > 0 else 0.0,
                "mean_score": round(sum(data["scores"]) / len(data["scores"]), 2) if data["scores"] else 0.0
            }
            for g, data in group_results.items()
        },
        "individual_results": results
    }

    out_file = config.benchmark_v1_path / "benchmark_evaluation.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(eval_summary, f, indent=2)

    return eval_summary
