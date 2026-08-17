"""Unified temporal timeline builder and continuity analytics engine (Phase 0.5)."""

import json
import hashlib
from datetime import datetime, timezone
from typing import List, Tuple, Dict, Any
from atlas.core.config import TIMELINE_DIR
from atlas.core.models import (
    ArtifactType, EvidenceArtifact, TimelineEvent,
    ContinuityLevel, TimelineContinuityMetrics
)

def compute_timeline_continuity(events: List[TimelineEvent]) -> TimelineContinuityMetrics:
    """
    Compute rigorous temporal metrics, coverage ratios, and continuity classifications.
    """
    metrics = TimelineContinuityMetrics()
    if not events:
        return metrics

    sorted_events = sorted(events, key=lambda e: e.timestamp)
    metrics.total_captures = len(sorted_events)
    metrics.first_seen = sorted_events[0].timestamp
    metrics.last_seen = sorted_events[-1].timestamp
    metrics.earliest_iso = sorted_events[0].datetime_iso
    metrics.latest_iso = sorted_events[-1].datetime_iso

    sources = set()
    years = []
    failure_events = []

    for ev in sorted_events:
        if ev.source:
            sources.add(ev.source.split(" ")[0])
        if len(ev.timestamp) >= 4:
            try:
                y = int(ev.timestamp[:4])
                years.append(y)
            except ValueError:
                pass
        if ev.status_code in (404, 410, 500, 502, 503):
            failure_events.append(ev)

    metrics.archive_sources = sorted(list(sources))
    metrics.has_documented_failures = len(failure_events) > 0

    if years:
        min_year = min(years)
        max_year = max(years)
        metrics.years_span = max_year - min_year
        unique_years = sorted(list(set(years)))
        metrics.unique_years_observed = len(unique_years)

        total_possible_years = metrics.years_span + 1
        metrics.observed_year_ratio = round(metrics.unique_years_observed / max(1, total_possible_years), 3)
        metrics.average_captures_per_year = round(metrics.total_captures / max(1, total_possible_years), 2)

    # Compute longest evidence gap
    max_gap_years = 0.0
    for i in range(len(sorted_events) - 1):
        cur = sorted_events[i]
        nxt = sorted_events[i + 1]
        try:
            y1 = int(cur.timestamp[:4]) + (int(cur.timestamp[4:6]) - 1) / 12.0 if len(cur.timestamp) >= 6 else float(cur.timestamp[:4])
            y2 = int(nxt.timestamp[:4]) + (int(nxt.timestamp[4:6]) - 1) / 12.0 if len(nxt.timestamp) >= 6 else float(nxt.timestamp[:4])
            gap = max(0.0, y2 - y1)
            if gap > max_gap_years:
                max_gap_years = gap
        except Exception:
            continue

    metrics.longest_evidence_gap_years = round(max_gap_years, 2)

    # Classify continuity level based on empirical density
    if metrics.years_span >= 15:
        if metrics.unique_years_observed <= 2 or metrics.total_captures <= 3:
            metrics.continuity_level = ContinuityLevel.HISTORICAL_PRESENCE
            metrics.continuity_claim = "sparse_two_point_presence"
        elif metrics.observed_year_ratio >= 0.85 and metrics.longest_evidence_gap_years <= 2.0 and metrics.total_captures >= 30:
            metrics.continuity_level = ContinuityLevel.CONTINUOUS_PRESENCE
            metrics.continuity_claim = "verified_high_density_continuity"
        elif metrics.observed_year_ratio >= 0.65 and metrics.longest_evidence_gap_years <= 3.5 and metrics.total_captures >= 15:
            metrics.continuity_level = ContinuityLevel.HIGH_CAPTURE_CONTINUITY
            metrics.continuity_claim = "substantial_continuity_with_minor_gaps"
        elif metrics.observed_year_ratio >= 0.40 and metrics.longest_evidence_gap_years <= 6.0:
            metrics.continuity_level = ContinuityLevel.LONG_SPAN_PRESENCE
            metrics.continuity_claim = "long_span_with_significant_gaps"
        else:
            metrics.continuity_level = ContinuityLevel.MULTI_PERIOD_PRESENCE
            metrics.continuity_claim = "multi_period_unproven_continuity"
    elif metrics.years_span >= 5:
        if metrics.unique_years_observed <= 2 or metrics.total_captures <= 3:
            metrics.continuity_level = ContinuityLevel.HISTORICAL_PRESENCE
            metrics.continuity_claim = "sparse_presence"
        elif metrics.observed_year_ratio >= 0.60:
            metrics.continuity_level = ContinuityLevel.HIGH_CAPTURE_CONTINUITY
            metrics.continuity_claim = "moderate_span_continuous"
        else:
            metrics.continuity_level = ContinuityLevel.MULTI_PERIOD_PRESENCE
            metrics.continuity_claim = "multi_period_presence"
    else:
        metrics.continuity_level = ContinuityLevel.HISTORICAL_PRESENCE
        metrics.continuity_claim = "short_span_presence"

    # Identify failure intervals
    if failure_events:
        for f in failure_events:
            metrics.failure_intervals.append({
                "timestamp": f.timestamp,
                "status_code": f.status_code,
                "source": f.source
            })

    return metrics

def build_unified_timeline(
    url: str,
    output_prefix: str,
    wayback_events: List[TimelineEvent],
    cc_events: List[TimelineEvent],
    live_event: TimelineEvent = None
) -> Tuple[List[TimelineEvent], TimelineContinuityMetrics, EvidenceArtifact]:
    """
    Merge, deduplicate, sort chronologically, and analyze historical events.
    Returns (List[TimelineEvent], TimelineContinuityMetrics, EvidenceArtifact).
    """
    all_events = list(wayback_events) + list(cc_events)
    if live_event:
        all_events.append(live_event)

    unique_map = {}
    for ev in all_events:
        key = (ev.timestamp, ev.source, ev.status_code)
        if key not in unique_map:
            unique_map[key] = ev

    sorted_events = sorted(unique_map.values(), key=lambda e: e.timestamp)
    metrics = compute_timeline_continuity(sorted_events)

    timeline_filename = f"{output_prefix}_timeline.json"
    timeline_path = TIMELINE_DIR / timeline_filename

    timeline_data = {
        "url": url,
        "metrics": metrics.model_dump(),
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
        source="aggregated_archives",
        collection_method="cdx_fusion",
        metadata=metrics.model_dump()
    )

    return sorted_events, metrics, artifact
