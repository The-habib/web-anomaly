"""Offline scoring runner for Project Atlas Phase 1 executing against frozen evidence."""

import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple

from atlas.core.models import (
    TimelineEvent, TimelineContinuityMetrics,
    EvidenceState, AnomalySignal
)
from atlas.scoring.scorer import AnomalyScorer
from atlas.core.config import SCORING_RULES_PATH
from atlas.phase1.config import (
    PHASE1_RAW_EVIDENCE_DIR, PHASE1_FROZEN_DIR,
    SCAN_RESULTS_JSONL, FINDINGS_JSONL, NEAR_MISSES_JSONL,
    SCORING_VERSION, 
)
from atlas.core.logger import logger

def run_phase1_scoring() -> Dict[str, Any]:
    """
    Execute offline scoring against frozen raw evidence dossiers.
    Produces scan_results.jsonl, findings.jsonl, and near_misses.jsonl.
    """
    logger.info("Executing Phase 1 offline scoring against frozen evidence...")
    scorer = AnomalyScorer()

    # Calculate scoring rules config hash
    with open(SCORING_RULES_PATH, "rb") as rf:
        config_hash = hashlib.sha256(rf.read()).hexdigest()

    scoring_timestamp = datetime.now(timezone.utc).isoformat()

    all_results = []
    findings = []
    near_misses = []

    if not PHASE1_RAW_EVIDENCE_DIR.exists():
        logger.error(f"Raw evidence directory {PHASE1_RAW_EVIDENCE_DIR} does not exist.")
        return {"status": "ERROR_NO_EVIDENCE"}

    for domain_dir in sorted(PHASE1_RAW_EVIDENCE_DIR.iterdir()):
        if not domain_dir.is_dir():
            continue

        raw_bundle_path = domain_dir / "raw_bundle.json"
        if not raw_bundle_path.exists():
            continue

        try:
            with open(raw_bundle_path, "r", encoding="utf-8") as f:
                raw_bundle = json.load(f)

            domain = raw_bundle["domain"]
            canonical_url = raw_bundle["canonical_url"]
            category = raw_bundle.get("category", "Unknown")
            preflight = raw_bundle.get("preflight", {})
            live = raw_bundle.get("live_evidence", {})
            metadata = live.get("metadata", {})
            status_code = live.get("status_code", 200)

            # Load HTML content if present
            html_content = ""
            html_file = domain_dir / "rendered.html"
            if html_file.exists():
                with open(html_file, "r", encoding="utf-8", errors="replace") as hf:
                    html_content = hf.read()

            # Load Timeline events and metrics
            timeline_events = []
            timeline_file = domain_dir / "timeline.json"
            tl_metrics = None
            if timeline_file.exists():
                with open(timeline_file, "r", encoding="utf-8") as tf:
                    tl_data = json.load(tf)
                    for ev_dict in tl_data.get("events", []):
                        timeline_events.append(TimelineEvent(**ev_dict))
                    if "metrics" in tl_data:
                        tl_metrics = TimelineContinuityMetrics(**tl_data["metrics"])

            # Run Scorer
            score, conf, classification, state, signals = scorer.evaluate(
                timeline=timeline_events,
                metadata=metadata,
                html_content=html_content,
                live_status=status_code,
                timeline_metrics=tl_metrics
            )

            result_entry = {
                "domain": domain,
                "canonical_url": canonical_url,
                "category": category,
                "scoring_version": SCORING_VERSION,
                "config_hash": config_hash,
                "scored_at": scoring_timestamp,
                "anomaly_score": score,
                "confidence": conf,
                "classification": classification,
                "evidence_state": state.value,
                "signals_count": len(signals),
                "signals": [s.model_dump() for s in signals],
                "timeline_metrics": tl_metrics.model_dump() if tl_metrics else {},
                "preflight_status": preflight.get("status"),
                "artifacts_count": len(raw_bundle.get("raw_artifacts", []))
            }

            all_results.append(result_entry)

            # High/medium scoring findings (Score >= 2)
            if score >= 2:
                findings.append(result_entry)

            # Near misses (Score == 1 or (Score == 0 and conf >= 0.85 and tl_metrics and tl_metrics.years_span >= 10))
            if score in (3, 4) or (score == 1 and conf >= 0.60):
                near_misses.append(result_entry)

        except Exception as e:
            logger.error(f"Error scoring domain {domain_dir.name}: {e}")

    # Write data/scan_results.jsonl
    with open(SCAN_RESULTS_JSONL, "w", encoding="utf-8") as sf:
        for r in all_results:
            sf.write(json.dumps(r) + "\n")

    # Write data/findings.jsonl
    with open(FINDINGS_JSONL, "w", encoding="utf-8") as ff:
        for r in sorted(findings, key=lambda x: (x["anomaly_score"], x["confidence"]), reverse=True):
            ff.write(json.dumps(r) + "\n")

    # Write data/near_misses.jsonl
    with open(NEAR_MISSES_JSONL, "w", encoding="utf-8") as nf:
        for r in near_misses:
            nf.write(json.dumps(r) + "\n")

    logger.info(f"Offline scoring complete: {len(all_results)} scored, {len(findings)} findings, {len(near_misses)} near misses.")
    return {
        "status": "SCORED",
        "total_scored": len(all_results),
        "total_findings": len(findings),
        "total_near_misses": len(near_misses)
    }
