"""Unified temporal timeline builder and gap detection engine."""

import json
import hashlib
from datetime import datetime
from typing import List, Tuple
from atlas.core.config import TIMELINE_DIR
from atlas.core.models import ArtifactType, EvidenceArtifact, TimelineEvent

def build_unified_timeline(
    url: str,
    output_prefix: str,
    wayback_events: List[TimelineEvent],
    cc_events: List[TimelineEvent],
    live_event: TimelineEvent = None
) -> Tuple[List[TimelineEvent], dict, EvidenceArtifact]:
    """
    Merge, deduplicate, sort chronologically, and analyze historical events.
    Returns (List[TimelineEvent], timeline_analysis_dict, EvidenceArtifact).
    """
    all_events = list(wayback_events) + list(cc_events)
    if live_event:
        all_events.append(live_event)

    # Sort chronologically by timestamp
    sorted_events = sorted(all_events, key=lambda e: e.timestamp)

    analysis = {
        "total_events": len(sorted_events),
        "first_seen": sorted_events[0].timestamp if sorted_events else None,
        "last_seen": sorted_events[-1].timestamp if sorted_events else None,
        "earliest_iso": sorted_events[0].datetime_iso if sorted_events else None,
        "latest_iso": sorted_events[-1].datetime_iso if sorted_events else None,
        "span_years": 0,
        "gaps_detected": []
    }

    if sorted_events:
        try:
            y_first = int(sorted_events[0].timestamp[:4])
            y_last = int(sorted_events[-1].timestamp[:4])
            analysis["span_years"] = max(0, y_last - y_first)
        except Exception:
            pass

    # Save timeline JSON artifact
    timeline_filename = f"{output_prefix}_timeline.json"
    timeline_path = TIMELINE_DIR / timeline_filename

    timeline_data = {
        "url": url,
        "analysis": analysis,
        "events": [e.model_dump() for e in sorted_events]
    }

    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(timeline_data, f, indent=2)

    with open(timeline_path, "rb") as f:
        content_bytes = f.read()

    artifact = EvidenceArtifact(
        artifact_id=f"art_tl_{output_prefix}",
        artifact_type=ArtifactType.TIMELINE,
        relative_path=str(timeline_path.relative_to(TIMELINE_DIR.parent.parent)),
        file_name=timeline_filename,
        sha256=hashlib.sha256(content_bytes).hexdigest(),
        size_bytes=len(content_bytes),
        metadata=analysis
    )

    return sorted_events, analysis, artifact
