"""Offline scoring engine for Phase 1.2 Pilot Experiment."""

import json
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime, timezone

from atlas.pilot.config import PilotConfig
from atlas.pilot.models import PilotEvidenceCapture, PilotScoringRecord
from atlas.provenance.manifest import compute_sha256

def score_single_evidence(ev: PilotEvidenceCapture) -> PilotScoringRecord:
    """
    Score a single frozen evidence capture using deterministic rules.
    Classification thresholds:
      - score < 40: ORDINARY
      - score 40-70: CANDIDATE_ANOMALY
      - score > 70: HIGH_ANOMALY
    """
    score = 0.0
    confidence = 0.50
    triggered = []
    breakdown = {}

    # Rule 1: High Historical Semantic Stability (Similarity >= 0.85)
    if ev.historical_similarity_score >= 0.85:
        w = 35.0
        score += w
        triggered.append("high_historical_stability")
        breakdown["high_historical_stability"] = w
        confidence += 0.20
    elif ev.historical_similarity_score >= 0.60:
        w = 15.0
        score += w
        triggered.append("moderate_historical_stability")
        breakdown["moderate_historical_stability"] = w
        confidence += 0.10

    # Rule 2: Legacy Layout Markers (Tables as layout / Framesets)
    if ev.has_frameset:
        w = 30.0
        score += w
        triggered.append("html_frameset_architecture")
        breakdown["html_frameset_architecture"] = w
        confidence += 0.15
    elif ev.has_tables_layout:
        w = 20.0
        score += w
        triggered.append("html_tables_layout")
        breakdown["html_tables_layout"] = w
        confidence += 0.10

    # Rule 3: Retro Web Elements / Unmodernized Styling
    if ev.has_retro_elements:
        w = 20.0
        score += w
        triggered.append("retro_styling_elements")
        breakdown["retro_styling_elements"] = w
        confidence += 0.10

    # Rule 4: Deep Archive Span (First seen <= 1996)
    if ev.earliest_archive_year and ev.earliest_archive_year <= 1996:
        w = 15.0
        score += w
        triggered.append("deep_archive_persistence_1996")
        breakdown["deep_archive_persistence_1996"] = w
        confidence += 0.05

    # Negative indicator: Modern Framework Presence (Anti-anomaly check)
    if ev.frameworks_detected and len(ev.frameworks_detected) > 0:
        penalty = 15.0
        score = max(0.0, score - penalty)
        triggered.append("modern_framework_penalty")
        breakdown["modern_framework_penalty"] = -penalty
        confidence = min(0.95, confidence + 0.05)

    confidence = min(1.0, max(0.1, confidence))

    if score > 70.0:
        classification = "HIGH_ANOMALY"
    elif score >= 40.0:
        classification = "CANDIDATE_ANOMALY"
    else:
        classification = "ORDINARY"

    return PilotScoringRecord(
        pilot_id=ev.pilot_id,
        domain=ev.domain,
        category=ev.category,
        raw_anomaly_score=round(score, 2),
        confidence=round(confidence, 2),
        classification=classification,
        triggered_rules=triggered,
        rule_score_breakdown=breakdown,
        evidence_hash=ev.evidence_sha256,
        scored_at=datetime.now(timezone.utc).isoformat()
    )

def score_pilot_evidence(
    evidence_list: List[PilotEvidenceCapture],
    config: PilotConfig = None
) -> Tuple[List[PilotScoringRecord], Path]:
    """
    Score all pilot evidence captures and save results to pilot_scores.jsonl.
    Updates the master pilot manifest.
    """
    if config is None:
        config = PilotConfig()

    out_file = config.pilot_data_path / "pilot_scores.jsonl"
    scoring_records: List[PilotScoringRecord] = []

    with open(out_file, "w", encoding="utf-8") as f:
        for ev in evidence_list:
            sc = score_single_evidence(ev)
            scoring_records.append(sc)
            f.write(sc.model_dump_json() + "\n")

    scores_sha256 = compute_sha256(str(out_file))

    # Update manifest
    manifest_file = config.pilot_data_path / "pilot_manifest.json"
    if manifest_file.exists():
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        manifest_data["scoring_sha256"] = scores_sha256
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

    return scoring_records, out_file
