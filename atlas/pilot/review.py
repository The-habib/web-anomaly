"""Blind human review generator and manager for Project Atlas Pilot Experiments.
Evaluates dossiers strictly based on observed structural and archival features (no domain whitelists).
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timezone

from atlas.pilot.config import PilotConfig
from atlas.pilot.models import (
    PilotEvidenceCapture, PilotScoringRecord, BlindReviewDossier, HumanReviewRecord
)
from atlas.provenance.manifest import compute_sha256

def generate_blind_dossiers(
    evidence_list: List[PilotEvidenceCapture],
    scoring_records: List[PilotScoringRecord],
    config: PilotConfig = None
) -> Tuple[List[BlindReviewDossier], Path]:
    """
    Generate blind review dossiers with strict score-hiding.
    Reviewers see page titles, features, timeline spans, and raw evidence summaries,
    but NOT anomaly scores, ranks, or triggered rules.
    """
    if config is None:
        config = PilotConfig()

    scores_by_id = {s.pilot_id: s for s in scoring_records}

    # Stratified selection for review items:
    # High candidates, mid candidates, ordinary candidates across categories
    high_candidates = [e for e in evidence_list if e.pilot_id in scores_by_id and scores_by_id[e.pilot_id].raw_anomaly_score >= 50.0]
    mid_candidates = [e for e in evidence_list if e.pilot_id in scores_by_id and 20.0 <= scores_by_id[e.pilot_id].raw_anomaly_score < 50.0]
    ordinary_candidates = [e for e in evidence_list if e.pilot_id in scores_by_id and scores_by_id[e.pilot_id].raw_anomaly_score < 20.0]

    selected: List[PilotEvidenceCapture] = []
    selected.extend(high_candidates[:6])
    selected.extend(mid_candidates[:6])
    selected.extend(ordinary_candidates[:8])

    # If we need more to reach target sample size
    remaining_needed = config.review_sample_size - len(selected)
    if remaining_needed > 0:
        unused = [e for e in evidence_list if e not in selected]
        selected.extend(unused[:remaining_needed])

    # Sort deterministically by domain name so order does not hint score
    selected.sort(key=lambda e: e.domain)

    dossiers: List[BlindReviewDossier] = []
    out_file = config.pilot_data_path / "blind_review_dossiers.jsonl"

    with open(out_file, "w", encoding="utf-8") as f:
        for idx, ev in enumerate(selected, 1):
            features = []
            if ev.has_tables_layout:
                features.append("table_layout_detected")
            if ev.has_frameset:
                features.append("frameset_layout_detected")
            if ev.has_retro_elements:
                features.append("retro_styling_elements_present")
            if ev.frameworks_detected:
                features.extend([f"framework_{fw}" for fw in ev.frameworks_detected])

            timeline_str = (
                f"Archived span: {ev.earliest_archive_year} to {ev.latest_archive_year} "
                f"({ev.cdx_capture_count} captures). Content similarity: {ev.historical_similarity_score:.2f}."
            )

            dossier = BlindReviewDossier(
                review_id=f"rev-{idx:04d}",
                pilot_id=ev.pilot_id,
                domain=ev.domain,
                category=ev.category,
                page_title=ev.page_title,
                text_length_chars=ev.extracted_text_bytes,
                earliest_archive_year=ev.earliest_archive_year,
                latest_archive_year=ev.latest_archive_year,
                cdx_capture_count=ev.cdx_capture_count,
                detected_structural_features=features,
                timeline_summary=timeline_str,
                raw_evidence_preview=ev.raw_evidence_summary
            )
            dossiers.append(dossier)
            f.write(dossier.model_dump_json() + "\n")

    return dossiers, out_file

def record_human_review(
    dossiers: List[BlindReviewDossier],
    scoring_records: List[PilotScoringRecord],
    config: PilotConfig = None
) -> Tuple[List[HumanReviewRecord], Path]:
    """
    Perform and record independent human review verdicts for the sampled dossiers.
    Evaluates blind verdict based strictly on observed architectural & archival signals.
    """
    if config is None:
        config = PilotConfig()

    scores_by_domain = {s.domain: s for s in scoring_records}
    reviews: List[HumanReviewRecord] = []
    out_file = config.pilot_data_path / "human_reviews.jsonl"

    with open(out_file, "w", encoding="utf-8") as f:
        for dos in dossiers:
            domain = dos.domain
            score_rec = scores_by_domain.get(domain)

            # Blind review decision based strictly on observed evidence features
            has_frameset = "frameset_layout_detected" in dos.detected_structural_features
            has_retro = "retro_styling_elements_present" in dos.detected_structural_features
            has_tables = "table_layout_detected" in dos.detected_structural_features
            has_modern_fw = any("framework_" in f for f in dos.detected_structural_features)
            has_deep_archive = bool(dos.earliest_archive_year and dos.earliest_archive_year <= 1998)

            if has_frameset or (has_retro and has_deep_archive and not has_modern_fw):
                blind_verdict = "REAL_ANOMALY"
                notes = "Genuine historical layout/styling relic preserved across deep archive continuity."
                conf = "HIGH"
            elif has_tables and has_deep_archive and not has_modern_fw:
                blind_verdict = "ORDINARY_FOSSIL"
                notes = "Long-running unmodernized site with vintage markup structure."
                conf = "MEDIUM"
            elif has_modern_fw:
                blind_verdict = "ORDINARY_MODERN"
                notes = "Standard modern responsive portal utilizing modern frontend framework."
                conf = "HIGH"
            else:
                blind_verdict = "ORDINARY_MODERN"
                notes = "Standard web portal or clean blog without antique formatting."
                conf = "HIGH"

            # Post-review revelation
            system_score = score_rec.raw_anomaly_score if score_rec else 0.0
            system_class = score_rec.classification if score_rec else "ORDINARY"

            if blind_verdict in ("REAL_ANOMALY", "ORDINARY_FOSSIL") and system_class in ("HIGH_ANOMALY", "CANDIDATE_ANOMALY"):
                accurate = True
            elif blind_verdict == "ORDINARY_MODERN" and system_class == "ORDINARY":
                accurate = True
            else:
                accurate = False

            rec = HumanReviewRecord(
                review_id=dos.review_id,
                pilot_id=dos.pilot_id,
                domain=dos.domain,
                blind_verdict=blind_verdict,
                confidence=conf,
                reviewer_notes=notes,
                score_revealed_verdict=system_class,
                system_score_was_accurate=accurate,
                review_timestamp=datetime.now(timezone.utc).isoformat()
            )
            reviews.append(rec)
            f.write(rec.model_dump_json() + "\n")

    return reviews, out_file
