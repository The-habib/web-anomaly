"""
Review Dataset Sampler & Interleaver for Project Atlas.
Prepares 51 neutral review packets for Run #003:
- 41 Nominated Potential Treasures
- 10 Random Dismissed Controls
Interleaves candidates and controls using a deterministic seed (seed 303) so reviewers
cannot infer whether a packet is a high-scoring candidate or an ordinary control.
"""

import json
import random
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple

from atlas.treasure.models import InvestigationRecord
from atlas.review.packet_v2 import serialize_neutral_review_packet_v2, ReviewPacketV2

DEFAULT_REVIEW_SEED = 303

def build_run_003_review_v2_sample(
    run_id: str = "TREASURE_RUN_0003",
    data_dir: Path = Path("data/treasure_runs/TREASURE_RUN_0003"),
    output_v2_dir: Path = Path("data/treasure_runs/TREASURE_RUN_0003/review_v2"),
    review_seed: int = DEFAULT_REVIEW_SEED
) -> Dict[str, Any]:
    """
    Formulate and freeze the 51-packet review dataset.
    """
    output_v2_dir.mkdir(parents=True, exist_ok=True)
    inv_file = data_dir / "investigations.jsonl"
    if not inv_file.exists():
        raise FileNotFoundError(f"Investigations dataset not found at {inv_file}")

    with open(inv_file, "r", encoding="utf-8") as f:
        all_invs = [InvestigationRecord(**json.loads(l)) for l in f if l.strip()]

    # Separate into candidates and dismissed pool
    candidate_pool = [inv for inv in all_invs if inv.archaeological_score >= 35.0 or inv.treasure_score >= 35.0]
    dismissed_pool = [inv for inv in all_invs if inv.archaeological_score < 35.0 and inv.treasure_score < 35.0]

    # Select 10 random dismissed controls using deterministic seed
    rng = random.Random(review_seed)
    control_count = min(10, len(dismissed_pool))
    control_sample = rng.sample(dismissed_pool, control_count) if dismissed_pool else []

    # Tag items internally for bookkeeping without leaking into packets
    items_to_packetize: List[Tuple[InvestigationRecord, str]] = []
    for c in candidate_pool:
        items_to_packetize.append((c, "CANDIDATE"))
    for d in control_sample:
        items_to_packetize.append((d, "CONTROL"))

    # Deterministically shuffle the combined 51 items
    rng.shuffle(items_to_packetize)

    serialized_packets: List[ReviewPacketV2] = []
    order_manifest: List[Dict[str, Any]] = []
    packet_hashes: List[str] = []

    for idx, (inv, kind) in enumerate(items_to_packetize, 1):
        pkt_id = f"REV_PKT_V2_{idx:03d}"
        raw_html_path = inv.evidence_artifact_path or inv.artifact_path or ""
        
        pkt = serialize_neutral_review_packet_v2(
            investigation=inv,
            packet_id=pkt_id,
            raw_html_path=raw_html_path
        )
        serialized_packets.append(pkt)

        pkt_json_str = pkt.model_dump_json()
        pkt_hash = hashlib.sha256(pkt_json_str.encode("utf-8")).hexdigest()
        packet_hashes.append(pkt_hash)

        # Internal order manifest (kept in review_v2/ for audit, never exposed to reviewer UI)
        order_manifest.append({
            "order_index": idx,
            "packet_id": pkt_id,
            "candidate_id": inv.candidate_id,
            "domain": inv.domain,
            "path": inv.path,
            "sample_kind": kind,
            "packet_sha256": pkt_hash
        })

    # Write review_packets_v2.jsonl
    packets_file = output_v2_dir / "review_packets_v2.jsonl"
    with open(packets_file, "w", encoding="utf-8") as f:
        for p in serialized_packets:
            f.write(p.model_dump_json() + "\n")

    # Write review_order.json
    with open(output_v2_dir / "review_order.json", "w", encoding="utf-8") as f:
        json.dump(order_manifest, f, indent=2)

    # Write review_manifest.json
    all_packets_hash = hashlib.sha256("".join(packet_hashes).encode("utf-8")).hexdigest()
    manifest_data = {
        "run_id": run_id,
        "review_version": "2.0.0",
        "review_seed": review_seed,
        "total_packets": len(serialized_packets),
        "candidate_packets_count": len(candidate_pool),
        "control_packets_count": len(control_sample),
        "packets_sha256_composite": all_packets_hash,
        "packets_file": str(packets_file)
    }
    with open(output_v2_dir / "review_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    # Initialize empty session state
    session_state = {
        "run_id": run_id,
        "total_packets": len(serialized_packets),
        "reviewed_count": 0,
        "remaining_count": len(serialized_packets),
        "current_packet_index": 0,
        "completed_reviews": []
    }
    with open(output_v2_dir / "review_session_state.json", "w", encoding="utf-8") as f:
        json.dump(session_state, f, indent=2)

    # Touch empty review_events.jsonl
    (output_v2_dir / "review_events.jsonl").touch()

    print(f"[+] Review V2 dataset built: {len(candidate_pool)} candidates + {len(control_sample)} controls ({len(serialized_packets)} total packets) in {output_v2_dir}")
    return manifest_data
