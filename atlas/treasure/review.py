"""
Blinded Review Packet Generation & Human Review Ingestion Subsystem for Project Atlas.
Generates neutral, partially-blinded review packets for human evaluation without exposing
model scores, discovery strategy names, or prior rankings.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from atlas.treasure.models import (
    InvestigationRecord,
    ReviewPacket,
    HumanReviewSubmission,
    TreasureDecision,
    CandidateState,
    TreasureRecord
)

def generate_review_packets(
    investigations: List[InvestigationRecord],
    output_file: Optional[Path] = None,
    run_id: str = "TREASURE_RUN_0003"
) -> List[ReviewPacket]:
    """
    Export neutral, partially-blind review packets for human archaeological review.
    Excludes model-derived scores, research priority, strategy names, and expected verdicts.
    """
    if output_file is None:
        output_file = Path(f"data/treasure_runs/{run_id}/review_packets.jsonl")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    packets: List[ReviewPacket] = []

    # Sort deterministically by candidate_id to avoid ranking cues
    sorted_invs = sorted(investigations, key=lambda x: x.candidate_id)

    for idx, inv in enumerate(sorted_invs, 1):
        rev_id = f"REV_PKT_{idx:04d}"
        is_linked = getattr(inv, "is_linked_from_root", True)
        struct_feats = getattr(inv, "structural_features", getattr(inv, "html_features_detected", []))
        timeline_sum = getattr(inv, "timeline_summary", "Historical record observed")
        sha_hash = getattr(inv, "live_html_sha256", getattr(inv, "sha256_hash", ""))
        art_path = getattr(inv, "evidence_artifact_path", getattr(inv, "artifact_path", ""))

        orphan_desc = "Orphaned (No link found on domain homepage)" if not is_linked else "Linked from root homepage"
        neutral_summary = (
            f"Public web surface observed on domain '{inv.domain}' at path '{inv.path}'. "
            f"Returned HTTP status {inv.live_status_code}. "
            f"Observed structural cues: {', '.join(struct_feats) if struct_feats else 'None detected'}. "
            f"Root navigation status: {orphan_desc}."
        )

        pkt = ReviewPacket(
            review_id=rev_id,
            packet_id=rev_id,
            candidate_id=inv.candidate_id,
            url=inv.url,
            target_url=inv.url,
            domain=inv.domain,
            path=inv.path,
            blinding_level="PARTIALLY_BLIND",
            live_status_code=inv.live_status_code,
            features_observed=struct_feats,
            html_features_detected=struct_feats,
            orphan_status=orphan_desc,
            timeline_observed=timeline_sum,
            evidence_sha256=sha_hash,
            sha256_hash=sha_hash,
            artifact_path=art_path or "",
            raw_evidence_path=art_path or "",
            neutral_summary=neutral_summary
        )
        packets.append(pkt)

    with open(output_file, "w", encoding="utf-8") as f:
        for p in packets:
            f.write(p.model_dump_json() + "\n")

    print(f"[+] Generated {len(packets)} blinded review packets in {output_file}.")
    return packets

def import_human_review_submissions(
    submissions_file: Path,
    investigations: List[InvestigationRecord]
) -> Tuple[List[HumanReviewSubmission], List[InvestigationRecord]]:
    """
    Import genuine human review submissions. Only submissions with verdict 'CLEAR_TREASURE'
    promote candidates to HUMAN_VALIDATED / TREASURE_VALIDATED.
    """
    if not submissions_file.exists():
        return [], []

    submissions: List[HumanReviewSubmission] = []
    with open(submissions_file, "r", encoding="utf-8") as f:
        for l in f:
            if l.strip():
                submissions.append(HumanReviewSubmission(**json.loads(l)))

    inv_map = {inv.candidate_id: inv for inv in investigations}
    promoted: List[InvestigationRecord] = []

    for sub in submissions:
        if sub.candidate_id in inv_map:
            inv = inv_map[sub.candidate_id]
            if sub.verdict == "CLEAR_TREASURE":
                inv.decision = TreasureDecision.TREASURE_VALIDATED
                inv.state = CandidateState.HUMAN_VALIDATED
                promoted.append(inv)
            elif sub.verdict == "POTENTIAL_TREASURE":
                inv.decision = TreasureDecision.POTENTIAL_TREASURE
                inv.state = CandidateState.REVIEW_PENDING
            elif sub.verdict == "ORDINARY":
                inv.decision = TreasureDecision.DISMISSED
                inv.state = CandidateState.ORDINARY
            elif sub.verdict == "INSUFFICIENT_EVIDENCE":
                inv.decision = TreasureDecision.INSUFFICIENT_EVIDENCE
                inv.state = CandidateState.INSUFFICIENT_EVIDENCE

    return submissions, promoted
