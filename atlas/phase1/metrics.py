"""Metrics calculation and reproducibility manifest generator for Phase 1."""

import os
import sys
import json
import shutil
import hashlib
import platform
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

from atlas import __version__, __codename__
from atlas.core.config import SCORING_RULES_PATH
from atlas.phase1.config import (
    PHASE1_DIR, CORPUS_CSV_PATH, SCAN_RESULTS_JSONL,
    FINDINGS_JSONL, NEAR_MISSES_JSONL, HUMAN_REVIEWS_JSONL,
    PHASE1_MANIFEST_PATH, PHASE1_METRICS_PATH,
    SEED, SCORING_VERSION
)
from atlas.core.logger import logger

def compute_phase1_metrics() -> Dict[str, Any]:
    """
    Calculate comprehensive statistical matrices and generate Phase 1 manifest.
    """
    logger.info("Computing Phase 1 experimental metrics...")

    # Load data files
    scan_results = []
    if SCAN_RESULTS_JSONL.exists():
        with open(SCAN_RESULTS_JSONL, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    scan_results.append(json.loads(l))

    findings = []
    if FINDINGS_JSONL.exists():
        with open(FINDINGS_JSONL, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    findings.append(json.loads(l))

    near_misses = []
    if NEAR_MISSES_JSONL.exists():
        with open(NEAR_MISSES_JSONL, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    near_misses.append(json.loads(l))

    reviews = []
    if HUMAN_REVIEWS_JSONL.exists():
        with open(HUMAN_REVIEWS_JSONL, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    reviews.append(json.loads(l))

    total_corpus = len(scan_results) or 1000
    successful_preflights = sum(1 for r in scan_results if r.get("preflight_status") == "SUCCESS")
    high_conf_candidates = [f for f in findings if f.get("confidence", 0) >= 0.70]

    # Review metrics
    validated_anomalies = sum(1 for r in reviews if r.get("human_verdict") in ("CLEAR_ANOMALY", "POTENTIAL_ANOMALY"))
    false_positives = sum(1 for r in reviews if r.get("human_verdict") == "FALSE_POSITIVE")
    false_negatives = sum(1 for r in reviews if r.get("human_verdict") == "FALSE_NEGATIVE_CANDIDATE")

    # Storage metrics
    total_bytes = 0
    raw_dir = PHASE1_DIR / "evidence" / "raw"
    if raw_dir.exists():
        for root, _, files in os.walk(raw_dir):
            for file in files:
                total_bytes += os.path.getsize(os.path.join(root, file))

    metrics_payload = {
        "experiment_id": "0002",
        "phase": "Phase 1 Blind Seed-Corpus Discovery",
        "calculated_at": datetime.now(timezone.utc).isoformat(),
        "coverage": {
            "domains_selected": total_corpus,
            "domains_attempted": total_corpus,
            "domains_successfully_processed": len(scan_results),
            "preflight_success_count": successful_preflights,
            "preflight_success_rate": round(successful_preflights / max(1, total_corpus), 3),
            "archive_coverage_rate": round(sum(1 for r in scan_results if r.get("timeline_metrics", {}).get("total_captures", 0) > 0) / max(1, total_corpus), 3)
        },
        "discovery": {
            "candidate_count": len(findings),
            "candidate_rate": round(len(findings) / max(1, total_corpus), 4),
            "high_confidence_candidates": len(high_conf_candidates),
            "near_miss_count": len(near_misses),
            "zero_score_count": total_corpus - len(findings)
        },
        "validation_sample": {
            "sample_size": len(reviews),
            "validated_anomalies": validated_anomalies,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "observed_validation_rate": round(validated_anomalies / max(1, len(reviews)), 3),
            "sample_false_positive_rate": round(false_positives / max(1, len(reviews)), 3)
        },
        "performance_and_storage": {
            "storage_consumed_mb": round(total_bytes / (1024 * 1024), 2),
            "total_raw_evidence_bytes": total_bytes,
            "average_bytes_per_domain": round(total_bytes / max(1, total_corpus), 1)
        }
    }

    # Save data/phase1_metrics.json
    with open(PHASE1_METRICS_PATH, "w", encoding="utf-8") as mf:
        json.dump(metrics_payload, mf, indent=2)

    # Generate data/phase1_manifest.json
    generate_reproducibility_manifest(metrics_payload)

    return metrics_payload

def generate_reproducibility_manifest(metrics: Dict[str, Any]) -> Path:
    """Generate exact cryptographic reproducibility manifest."""
    git_commit = "unknown"
    try:
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        pass

    corpus_hash = ""
    if CORPUS_CSV_PATH.exists():
        with open(CORPUS_CSV_PATH, "rb") as cf:
            corpus_hash = hashlib.sha256(cf.read()).hexdigest()

    rules_hash = ""
    if SCORING_RULES_PATH.exists():
        with open(SCORING_RULES_PATH, "rb") as rf:
            rules_hash = hashlib.sha256(rf.read()).hexdigest()

    manifest = {
        "experiment_id": "0002",
        "title": "Phase 1 Blind Seed-Corpus Discovery Experiment",
        "atlas_version": __version__,
        "atlas_codename": __codename__,
        "git_commit": git_commit,
        "python_version": platform.python_version(),
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "sampling_seed": SEED,
        "scoring_version": SCORING_VERSION,
        "corpus_sha256": corpus_hash,
        "scoring_rules_sha256": rules_hash,
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "summary_metrics": metrics
    }

    with open(PHASE1_MANIFEST_PATH, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2)

    logger.info(f"Reproducibility manifest generated at {PHASE1_MANIFEST_PATH}")
    return PHASE1_MANIFEST_PATH
