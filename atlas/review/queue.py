"""
Review Queue Prioritizer Subsystem for Project Atlas.
Orders review candidates balancing research priority, evidence completeness, category diversity,
and unique path characteristics without altering underlying scientific truth.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ReviewQueueItem(BaseModel):
    queue_position: int
    candidate_id: str
    packet_id: str
    target_url: str
    domain: str
    category: str
    research_priority: float
    evidence_complete: bool
    queue_score: float
    reason: str

def build_prioritized_review_queue(
    review_packets: List[Dict[str, Any]],
    output_file: Optional[Path] = None
) -> List[ReviewQueueItem]:
    """Sort and structure review queue items with diversity awareness."""
    category_counts: Dict[str, int] = {}
    items = []

    for pkt in review_packets:
        cid = pkt.get("candidate_id", "")
        pid = pkt.get("packet_id", "")
        url = pkt.get("target_url", "")
        dom = pkt.get("domain", "")
        cat = pkt.get("domain_category", "General")
        
        # Priority components
        has_evidence = bool(pkt.get("sha256_hash"))
        cap_count = pkt.get("historical_capture_count", 0)
        feat_count = len(pkt.get("html_features_detected", []))

        # Diversity penalty for overrepresented categories
        seen_cat = category_counts.get(cat, 0)
        diversity_factor = max(0.5, 1.0 - (seen_cat * 0.05))

        queue_score = round(((feat_count * 5.0) + (min(10, cap_count) * 1.5) + (10.0 if has_evidence else 0.0)) * diversity_factor, 2)
        category_counts[cat] = seen_cat + 1

        items.append(ReviewQueueItem(
            queue_position=0,
            candidate_id=cid,
            packet_id=pid,
            target_url=url,
            domain=dom,
            category=cat,
            research_priority=queue_score,
            evidence_complete=has_evidence,
            queue_score=queue_score,
            reason=f"Features: {feat_count}, Captures: {cap_count}, Evidence: {has_evidence}"
        ))

    # Sort descending by queue_score
    items.sort(key=lambda x: x.queue_score, reverse=True)
    for idx, item in enumerate(items, 1):
        item.queue_position = idx

    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            for it in items:
                data = it.model_dump()
                data["schema_version"] = "1.0.0"
                f.write(json.dumps(data) + "\n")

    return items
