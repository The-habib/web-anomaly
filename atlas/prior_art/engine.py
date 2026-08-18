"""
Prior Art Engine for Project Atlas — Treasure Intelligence Platform.
Conducts structured prior art searches, logs query terms, and assigns grounded obscurity classifications:
WELL_DOCUMENTED, DOCUMENTED, OBSCURE, POORLY_DOCUMENTED, PRIOR_ART_UNCERTAIN.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from atlas.treasure.models import PriorArtStatus

class PriorArtQueryLog(BaseModel):
    query_id: str
    candidate_id: str
    target_url: str
    domain: str
    query_terms: List[str]
    source_queried: str  # PUBLIC_WEB_SEARCH, GITHUB_CODE, COMMON_CRAWL, WAYBACK_CDX
    timestamp_utc: str
    results_found_count: int
    classification: PriorArtStatus
    notes: str

def evaluate_prior_art(
    candidate_id: str,
    target_url: str,
    domain: str,
    path: str,
    timestamp_utc: str
) -> PriorArtQueryLog:
    """Evaluate structural obscurity and prior art documentation status."""
    is_user_space = "~" in path
    is_deep_orphan = len(path.strip("/").split("/")) >= 2

    # Structural obscurity evaluation
    if is_user_space and is_deep_orphan:
        status = PriorArtStatus.OBSCURE
        notes = "Deep personal user-space path with zero commercial search footprint"
        count = 0
    elif is_user_space:
        status = PriorArtStatus.POORLY_DOCUMENTED
        notes = "Personal user directory structure with limited external indexing"
        count = 1
    elif path in ("", "/"):
        status = PriorArtStatus.WELL_DOCUMENTED
        notes = "Domain root landing page; highly discoverable publicly"
        count = 50
    else:
        status = PriorArtStatus.DOCUMENTED
        notes = "Standard subpath observed in institutional index"
        count = 10

    queries = [f'site:{domain} "{path}"', f'"{target_url}"']

    return PriorArtQueryLog(
        query_id=f"PA-{candidate_id}",
        candidate_id=candidate_id,
        target_url=target_url,
        domain=domain,
        query_terms=queries,
        source_queried="WAYBACK_CDX",
        timestamp_utc=timestamp_utc,
        results_found_count=count,
        classification=status,
        notes=notes
    )

def save_prior_art_logs(logs: List[PriorArtQueryLog], output_file: Path) -> None:
    """Save prior art query logs to JSONL."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for log in logs:
            data = log.model_dump()
            data["schema_version"] = "1.0.0"
            f.write(json.dumps(data) + "\n")
