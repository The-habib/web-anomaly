"""Blind evidence collection engine for Project Atlas Phase 1 (Thread-Safe)."""

import os
import json
import time
import hashlib
import threading
import requests
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup

from atlas.core.config import DEFAULT_USER_AGENT
from atlas.core.models import (
    TimelineEvent, TimelineContinuityMetrics,
    EvidenceArtifact, ArtifactType, EvidenceState
)
from atlas.pipeline.wayback_client import query_wayback_timeline
from atlas.pipeline.commoncrawl_client import query_commoncrawl_timeline
from atlas.pipeline.timeline import compute_timeline_continuity, build_unified_timeline
from atlas.phase1.config import (
    PHASE1_RAW_EVIDENCE_DIR, FETCH_TIMEOUT,
    ARCHIVE_TIMEOUT, MAX_HISTORICAL_CAPTURES, MAX_PAGE_SIZE_BYTES
)
from atlas.core.logger import logger

_PARSER_LOCK = threading.Lock()

def extract_clean_text(html: str) -> str:
    """Thread-safe clean text extraction using trafilatura with BeautifulSoup fallback."""
    if not html:
        return ""
    try:
        import trafilatura
        with _PARSER_LOCK:
            txt = trafilatura.extract(html)
            if txt:
                return txt
    except Exception:
        pass

    try:
        soup = BeautifulSoup(html, "html.parser")
        for elem in soup(["script", "style", "nav", "footer", "header"]):
            elem.extract()
        return soup.get_text(separator=" ", strip=True)
    except Exception:
        return ""

def collect_domain_evidence(
    domain_record: Dict[str, str],
    preflight_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Collect raw evidence for a single domain under the blind collection protocol.
    Stores raw files in experiments/0002/evidence/raw/<domain_slug>/.
    """
    domain = domain_record["domain"]
    clean_domain = domain.replace(":", "_").replace("/", "_").replace(".", "_")
    target_url = preflight_info.get("final_url") or f"https://{domain}"
    domain_dir = PHASE1_RAW_EVIDENCE_DIR / clean_domain
    domain_dir.mkdir(parents=True, exist_ok=True)

    collection_timestamp = datetime.now(timezone.utc).isoformat()
    start_time = time.time()

    evidence_dossier = {
        "domain": domain,
        "canonical_url": target_url,
        "category": domain_record.get("category", "Unknown"),
        "collection_timestamp": collection_timestamp,
        "preflight": preflight_info,
        "live_evidence": {},
        "archive_evidence": {},
        "timeline_metrics": {},
        "raw_artifacts": []
    }

    # -------------------------------------------------------------
    # 1. Live Fetch & Extraction (if preflight succeeded)
    # -------------------------------------------------------------
    html_content = ""
    clean_text = ""
    metadata = {}
    status_code = preflight_info.get("status_code", 0)

    if preflight_info.get("status") == "SUCCESS":
        try:
            session = requests.Session()
            session.headers.update({"User-Agent": DEFAULT_USER_AGENT})
            resp = session.get(target_url, timeout=FETCH_TIMEOUT, stream=True)
            status_code = resp.status_code

            # Read content with budget limit
            raw_bytes = resp.raw.read(MAX_PAGE_SIZE_BYTES + 1024, decode_content=True)
            encoding = resp.encoding or "utf-8"
            html_content = raw_bytes.decode(encoding, errors="replace")

            # Parse with BeautifulSoup & thread-safe text extractor
            soup = BeautifulSoup(html_content, "html.parser")
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            clean_text = extract_clean_text(html_content)

            # Extract generator, doctype, links
            gen_meta = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "generator"})
            generator = gen_meta["content"] if gen_meta and gen_meta.get("content") else "None"
            doctype = str(soup.contents[0]) if soup.contents and "DOCTYPE" in str(soup.contents[0]) else "HTML5/Standard"

            metadata = {
                "title": title,
                "generator": generator,
                "doctype": doctype,
                "links_count": len(soup.find_all("a")),
                "scripts_count": len(soup.find_all("script")),
                "images_count": len(soup.find_all("img")),
                "headers": dict(resp.headers),
                "content_length": len(raw_bytes)
            }

            # Save HTML artifact
            html_file = domain_dir / "rendered.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            html_sha = hashlib.sha256(raw_bytes).hexdigest()
            evidence_dossier["raw_artifacts"].append({
                "type": "html",
                "file_name": "rendered.html",
                "relative_path": f"evidence/raw/{clean_domain}/rendered.html",
                "sha256": html_sha,
                "size_bytes": len(raw_bytes)
            })

            # Save Text artifact
            text_file = domain_dir / "extracted_text.txt"
            with open(text_file, "w", encoding="utf-8") as f:
                f.write(clean_text)

        except Exception as e:
            metadata["fetch_error"] = str(e)

    evidence_dossier["live_evidence"] = {
        "status_code": status_code,
        "metadata": metadata,
        "text_length": len(clean_text)
    }

    # -------------------------------------------------------------
    # 2. Archive Timeline Queries (Wayback + Common Crawl)
    # -------------------------------------------------------------
    wb_events = []
    cc_events = []

    # Wayback Machine CDX Query
    try:
        wb_events, wb_summary = query_wayback_timeline(domain, limit=MAX_HISTORICAL_CAPTURES, timeout=5)
        evidence_dossier["archive_evidence"]["wayback_summary"] = wb_summary
    except Exception as e:
        evidence_dossier["archive_evidence"]["wayback_error"] = str(e)

    # Common Crawl Query
    try:
        cc_events, cc_summary = query_commoncrawl_timeline(domain, limit=20, timeout=5)
        evidence_dossier["archive_evidence"]["commoncrawl_summary"] = cc_summary
    except Exception as e:
        evidence_dossier["archive_evidence"]["commoncrawl_error"] = str(e)

    # -------------------------------------------------------------
    # 3. Build Unified Timeline & Metrics
    # -------------------------------------------------------------
    live_event = None
    if status_code and status_code > 0:
        live_event = TimelineEvent(
            timestamp=datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
            datetime_iso=collection_timestamp,
            source="live",
            status_code=status_code,
            content_length=len(html_content),
            mime_type=metadata.get("headers", {}).get("content-type", "text/html"),
            notes="Live inspection during Phase 1 blind scan"
        )

    all_events = list(wb_events) + list(cc_events)
    if live_event:
        all_events.append(live_event)

    # Deduplicate
    unique_events = {}
    for ev in all_events:
        key = (ev.timestamp, ev.source, ev.status_code)
        if key not in unique_events:
            unique_events[key] = ev

    sorted_events = sorted(unique_events.values(), key=lambda x: x.timestamp)
    tl_metrics = compute_timeline_continuity(sorted_events)
    evidence_dossier["timeline_metrics"] = tl_metrics.model_dump()

    # Save Timeline JSON
    timeline_file = domain_dir / "timeline.json"
    with open(timeline_file, "w", encoding="utf-8") as f:
        json.dump({
            "domain": domain,
            "metrics": tl_metrics.model_dump(),
            "events": [e.model_dump() for e in sorted_events]
        }, f, indent=2)

    with open(timeline_file, "rb") as f:
        tl_bytes = f.read()

    evidence_dossier["raw_artifacts"].append({
        "type": "timeline",
        "file_name": "timeline.json",
        "relative_path": f"evidence/raw/{clean_domain}/timeline.json",
        "sha256": hashlib.sha256(tl_bytes).hexdigest(),
        "size_bytes": len(tl_bytes)
    })

    # Save Complete Raw Bundle
    bundle_file = domain_dir / "raw_bundle.json"
    with open(bundle_file, "w", encoding="utf-8") as f:
        json.dump(evidence_dossier, f, indent=2)

    with open(bundle_file, "rb") as f:
        b_bytes = f.read()

    evidence_dossier["raw_artifacts"].append({
        "type": "json",
        "file_name": "raw_bundle.json",
        "relative_path": f"evidence/raw/{clean_domain}/raw_bundle.json",
        "sha256": hashlib.sha256(b_bytes).hexdigest(),
        "size_bytes": len(b_bytes)
    })

    duration_ms = (time.time() - start_time) * 1000
    evidence_dossier["duration_ms"] = round(duration_ms, 2)
    return evidence_dossier
