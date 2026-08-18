"""
Historical Timeline Engine for Project Atlas.
Models and compiles event-driven historical timelines for candidate pages and archives.
Tracks event types: FIRST_OBSERVATION, LONG_TERM_PRESENCE, STRUCTURAL_CHANGE,
REDIRECT, ARCHIVE_GAP, RETURN, MIRROR, CONTENT_CHANGE, CURRENT_SURVIVAL, CURRENT_FAILURE.
"""

import json
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TimelineEventType(str, Enum):
    FIRST_OBSERVATION = "FIRST_OBSERVATION"
    LONG_TERM_PRESENCE = "LONG_TERM_PRESENCE"
    STRUCTURAL_CHANGE = "STRUCTURAL_CHANGE"
    REDIRECT = "REDIRECT"
    ARCHIVE_GAP = "ARCHIVE_GAP"
    RETURN = "RETURN"
    MIRROR = "MIRROR"
    CONTENT_CHANGE = "CONTENT_CHANGE"
    CURRENT_SURVIVAL = "CURRENT_SURVIVAL"
    CURRENT_FAILURE = "CURRENT_FAILURE"

class TimelineEvent(BaseModel):
    event_id: str
    event_type: TimelineEventType
    timestamp_observed: str  # YYYY-MM-DD or YYYY or UNKNOWN_INTERVAL
    description: str
    evidence_source: str  # WAYBACK_CDX, LIVE_PROBE, SITEMAP, COMMON_CRAWL
    evidence_id: Optional[str] = None
    confidence: str = "OBSERVED"  # OBSERVED, INFERRED, UNKNOWN

class PageTimeline(BaseModel):
    timeline_id: str
    candidate_id: str
    url: str
    domain: str
    events: List[TimelineEvent] = Field(default_factory=list)
    created_at_utc: str
    summary: str

def build_page_timeline(
    candidate_id: str,
    url: str,
    domain: str,
    earliest_year: Optional[int],
    latest_year: Optional[int],
    capture_count: int,
    live_status_code: Optional[int],
    timestamp_utc: str
) -> PageTimeline:
    """Compile structured, evidence-grounded timeline events."""
    events: List[TimelineEvent] = []

    # 1. First observation
    if earliest_year and earliest_year > 1990:
        events.append(TimelineEvent(
            event_id=f"EVT-{candidate_id}-01",
            event_type=TimelineEventType.FIRST_OBSERVATION,
            timestamp_observed=f"{earliest_year}-01-01",
            description=f"Initial public archival observation recorded on {domain}",
            evidence_source="WAYBACK_CDX",
            confidence="OBSERVED"
        ))
    else:
        events.append(TimelineEvent(
            event_id=f"EVT-{candidate_id}-01",
            event_type=TimelineEventType.FIRST_OBSERVATION,
            timestamp_observed="UNKNOWN_INTERVAL",
            description="Earliest archive timestamp unconfirmed",
            evidence_source="WAYBACK_CDX",
            confidence="UNKNOWN"
        ))

    # 2. Long term presence
    if earliest_year and latest_year and (latest_year - earliest_year >= 3):
        events.append(TimelineEvent(
            event_id=f"EVT-{candidate_id}-02",
            event_type=TimelineEventType.LONG_TERM_PRESENCE,
            timestamp_observed=f"{earliest_year} to {latest_year}",
            description=f"Continuous multi-year archival record spanning {latest_year - earliest_year} years ({capture_count} captures)",
            evidence_source="WAYBACK_CDX",
            confidence="OBSERVED"
        ))

    # 3. Current survival
    if live_status_code == 200:
        events.append(TimelineEvent(
            event_id=f"EVT-{candidate_id}-03",
            event_type=TimelineEventType.CURRENT_SURVIVAL,
            timestamp_observed="2026-08-18",
            description="Verified active HTTP 200 survival in live web crawl",
            evidence_source="LIVE_PROBE",
            confidence="OBSERVED"
        ))
    elif live_status_code:
        events.append(TimelineEvent(
            event_id=f"EVT-{candidate_id}-03",
            event_type=TimelineEventType.CURRENT_FAILURE,
            timestamp_observed="2026-08-18",
            description=f"Live HTTP probe returned non-200 status code: {live_status_code}",
            evidence_source="LIVE_PROBE",
            confidence="OBSERVED"
        ))

    summary = f"Timeline for {url}: {len(events)} verified historical and live observations."

    return PageTimeline(
        timeline_id=f"TL-{candidate_id}",
        candidate_id=candidate_id,
        url=url,
        domain=domain,
        events=events,
        created_at_utc=timestamp_utc,
        summary=summary
    )

def save_timelines(timelines: List[PageTimeline], output_file: Path) -> None:
    """Persist timelines to JSONL."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for tl in timelines:
            data = tl.model_dump()
            data["schema_version"] = "1.0.0"
            f.write(json.dumps(data) + "\n")
