"""
Mobile-First Human Review Console & Session Engine for Project Atlas.
Provides evidence-only review interface with strict neutrality:
- Shows raw HTML, capture dates, HTTP status, and evidence digests.
- Collects human verdicts (CLEAR_TREASURE, POTENTIAL_TREASURE, ORDINARY, INSUFFICIENT_EVIDENCE).
- Supports offline session export/import with SHA-256 session integrity checks.
- Enforces zero model leakage (never displays anomaly scores, priorities, strategies, or DNA).
"""

import json
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from pydantic import BaseModel, Field
from atlas.review.packet_v2 import ReviewPacketV2, validate_packet_v2_neutrality

VALID_VERDICTS = ["CLEAR_TREASURE", "POTENTIAL_TREASURE", "ORDINARY", "INSUFFICIENT_EVIDENCE"]

class ReviewRecordV2(BaseModel):
    """Immutable Human Review Record."""
    review_id: str
    reviewer_id: str
    candidate_id: str
    packet_id: str
    packet_version: str = "2.0.0"
    verdict: str
    confidence: float
    notes: str
    timestamp_utc: str
    review_duration_seconds: Optional[float] = None
    packet_sha256: str
    review_version: int = 1
    supersedes_review_id: Optional[str] = None

class ReviewSession(BaseModel):
    session_id: str
    reviewer_id: str
    created_at_utc: str
    updated_at_utc: str
    total_packets: int
    reviewed_count: int
    remaining_count: int
    current_index: int
    reviews: List[ReviewRecordV2] = Field(default_factory=list)
    session_sha256: str = ""

def load_review_packets_v2(
    review_v2_dir: Path = Path("data/treasure_runs/TREASURE_RUN_0003/review_v2")
) -> List[ReviewPacketV2]:
    """Load sanitized ReviewPacketV2 records."""
    packets_file = review_v2_dir / "review_packets_v2.jsonl"
    if not packets_file.exists():
        raise FileNotFoundError(f"Review packets not found at {packets_file}. Run sampler first.")

    packets = []
    with open(packets_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                p = ReviewPacketV2(**json.loads(line.strip()))
                is_valid, violations = validate_packet_v2_neutrality(p.model_dump())
                if not is_valid:
                    raise PermissionError(f"Neutrality Violation in packet {p.review_packet_id}: {violations}")
                packets.append(p)
    return packets

def get_review_status(
    review_v2_dir: Path = Path("data/treasure_runs/TREASURE_RUN_0003/review_v2")
) -> Dict[str, Any]:
    """Get neutral review dashboard status without score distributions."""
    state_file = review_v2_dir / "review_session_state.json"
    manifest_file = review_v2_dir / "review_manifest.json"

    total = 0
    reviewed = 0
    remaining = 0
    curr_idx = 0

    if state_file.exists():
        with open(state_file, "r", encoding="utf-8") as f:
            st = json.load(f)
        total = st.get("total_packets", 0)
        reviewed = st.get("reviewed_count", 0)
        remaining = st.get("remaining_count", total)
        curr_idx = st.get("current_packet_index", 0)
    elif manifest_file.exists():
        with open(manifest_file, "r", encoding="utf-8") as f:
            m = json.load(f)
        total = m.get("total_packets", 0)
        remaining = total

    # Count actual reviews recorded
    events_file = review_v2_dir / "review_events.jsonl"
    recorded_reviews = 0
    unique_reviewers = set()
    if events_file.exists():
        with open(events_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line.strip())
                    recorded_reviews += 1
                    if "reviewer_id" in r:
                        unique_reviewers.add(r["reviewer_id"])

    return {
        "total_packets": total,
        "reviewed_count": reviewed or recorded_reviews,
        "remaining_count": max(0, total - (reviewed or recorded_reviews)),
        "current_packet_index": curr_idx,
        "reviewer_count": len(unique_reviewers) or (1 if recorded_reviews > 0 else 0),
        "review_state": "READY_FOR_HUMAN_REVIEW" if (reviewed or recorded_reviews) == 0 else ("IN_PROGRESS" if (reviewed or recorded_reviews) < total else "REVIEW_COMPLETE")
    }

def render_packet_console(packet: ReviewPacketV2, current_index: int, total_count: int) -> str:
    """Render mobile-first vertical layout for terminal / console review."""
    lines = []
    lines.append("=" * 65)
    lines.append(f"  PROJECT ATLAS — EVIDENCE REVIEW CONSOLE ({current_index + 1}/{total_count})")
    lines.append(f"  Packet ID:    {packet.review_packet_id}")
    lines.append(f"  Candidate ID: {packet.candidate_id}")
    lines.append("=" * 65)
    lines.append("\n[1. SOURCE METADATA]")
    lines.append(f"  URL:          {packet.source_url}")
    lines.append(f"  HTTP Status:  {packet.current_http_status}")
    lines.append(f"  Content-Type: {packet.content_type}")
    lines.append(f"  Observed At:  {packet.collection_timestamp_utc}")
    
    lines.append("\n[2. HISTORICAL CAPTURE EVIDENCE]")
    if packet.historical_captures:
        for c in packet.historical_captures:
            lines.append(f"  - [{c.timestamp_utc[:10]}] Source: {c.archive_source} (Status: {c.http_status})")
    else:
        lines.append("  - No earlier historical capture records supplied in packet.")

    lines.append("\n[3. EVIDENCE ARTIFACTS & INTEGRITY]")
    lines.append(f"  Raw HTML Path: {packet.raw_html_reference}")
    for k, h in packet.evidence_hashes.items():
        lines.append(f"  SHA-256 ({k}): {h}")

    if packet.navigation_scope:
        lines.append("\n[4. NAVIGATION CONTEXT]")
        lines.append(f"  Root URL:       {packet.navigation_scope.root_url}")
        lines.append(f"  Links Checked:  {packet.navigation_scope.links_inspected_count}")
        lines.append(f"  Direct Link:    {'FOUND' if packet.navigation_scope.direct_link_found else 'NOT FOUND ON ROOT'}")

    lines.append("\n[5. REVIEWER PROMPTS]")
    lines.append("  - What is unusual or historically noteworthy about this surface?")
    lines.append("  - Is this page still functioning as an authentic public web artifact?")
    lines.append("  - Would an ordinary web user easily find this without deep discovery?")

    lines.append("\n[6. VERDICT CONTROLS]")
    lines.append("  [1] CLEAR_TREASURE         (Authentic surviving historical/obscure artifact)")
    lines.append("  [2] POTENTIAL_TREASURE     (Interesting surface requiring further research)")
    lines.append("  [3] ORDINARY               (Modern, generic, boilerplate, or common page)")
    lines.append("  [4] INSUFFICIENT_EVIDENCE  (Artifact missing or unable to verify)")
    lines.append("-" * 65)
    return "\n".join(lines)

def submit_human_review(
    packet_id: str,
    reviewer_id: str,
    verdict: str,
    confidence: float,
    notes: str,
    review_v2_dir: Path = Path("data/treasure_runs/TREASURE_RUN_0003/review_v2"),
    review_duration_seconds: Optional[float] = None
) -> ReviewRecordV2:
    """Submit a validated human review record."""
    if verdict not in VALID_VERDICTS:
        raise ValueError(f"Invalid verdict '{verdict}'. Must be one of: {VALID_VERDICTS}")
    if not (0.0 <= confidence <= 1.0):
        raise ValueError("Confidence must be between 0.0 and 1.0")

    # Anti-bot validation
    reviewer_lower = reviewer_id.strip().lower()
    if not reviewer_id or any(k in reviewer_lower for k in ("machine", "auto", "system", "bot", "synthetic")):
        raise PermissionError(f"Machine/System reviewer ID prohibited ('{reviewer_id}'). Genuine human reviewer required.")

    packets = load_review_packets_v2(review_v2_dir)
    target_pkt = next((p for p in packets if p.review_packet_id == packet_id or p.candidate_id == packet_id), None)
    if not target_pkt:
        raise KeyError(f"Review packet '{packet_id}' not found.")

    pkt_hash = hashlib.sha256(target_pkt.model_dump_json().encode("utf-8")).hexdigest()
    rev_id = f"REV_{reviewer_id}_{target_pkt.review_packet_id}_{int(time.time())}"
    now_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    rec = ReviewRecordV2(
        review_id=rev_id,
        reviewer_id=reviewer_id,
        candidate_id=target_pkt.candidate_id,
        packet_id=target_pkt.review_packet_id,
        packet_version=target_pkt.packet_version,
        verdict=verdict,
        confidence=confidence,
        notes=notes,
        timestamp_utc=now_utc,
        review_duration_seconds=review_duration_seconds,
        packet_sha256=pkt_hash,
        review_version=1
    )

    # Append to review_events.jsonl
    events_file = review_v2_dir / "review_events.jsonl"
    with open(events_file, "a", encoding="utf-8") as f:
        f.write(rec.model_dump_json() + "\n")

    # Update session state
    state_file = review_v2_dir / "review_session_state.json"
    if state_file.exists():
        with open(state_file, "r", encoding="utf-8") as f:
            st = json.load(f)
        completed = st.get("completed_reviews", [])
        if target_pkt.review_packet_id not in [c.get("packet_id") for c in completed]:
            completed.append({"packet_id": target_pkt.review_packet_id, "verdict": verdict})
        st["reviewed_count"] = len(completed)
        st["remaining_count"] = max(0, st.get("total_packets", 51) - len(completed))
        st["completed_reviews"] = completed
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(st, f, indent=2)

    return rec

def export_review_session(
    output_file: Path,
    reviewer_id: str = "HUMAN_ARCHAEOLOGIST_01",
    review_v2_dir: Path = Path("data/treasure_runs/TREASURE_RUN_0003/review_v2")
) -> Path:
    """Export review session bundle for offline evaluation."""
    packets = load_review_packets_v2(review_v2_dir)
    events_file = review_v2_dir / "review_events.jsonl"
    existing_reviews = []
    if events_file.exists():
        with open(events_file, "r", encoding="utf-8") as f:
            existing_reviews = [ReviewRecordV2(**json.loads(l)) for l in f if l.strip()]

    now_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    session = ReviewSession(
        session_id=f"SESS_{int(time.time())}",
        reviewer_id=reviewer_id,
        created_at_utc=now_utc,
        updated_at_utc=now_utc,
        total_packets=len(packets),
        reviewed_count=len(existing_reviews),
        remaining_count=len(packets) - len(existing_reviews),
        current_index=len(existing_reviews),
        reviews=existing_reviews
    )
    sess_json = session.model_dump_json(indent=2)
    session.session_sha256 = hashlib.sha256(sess_json.encode("utf-8")).hexdigest()

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(session.model_dump_json(indent=2))

    print(f"[+] Review session exported to {output_file} (SHA-256: {session.session_sha256[:12]}...)")
    return output_file
