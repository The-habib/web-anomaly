"""Master Evidence Pipeline for Project Atlas (Phase 0.5)."""

import time
import json
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Optional, List

from atlas.core.config import (
    JSON_DIR, FINDINGS_DIR, REPORTS_DIR,
    DEFAULT_USER_AGENT
)
from atlas.core.logger import logger
from atlas.core.models import (
    ArtifactType, EvidenceArtifact, Finding, TimelineEvent, EvidenceState
)
from atlas.pipeline.screenshot import capture_screenshot
from atlas.pipeline.html_extractor import fetch_and_extract_html
from atlas.pipeline.wayback_client import query_wayback_timeline
from atlas.pipeline.commoncrawl_client import query_commoncrawl_timeline
from atlas.pipeline.timeline import build_unified_timeline
from atlas.scoring.scorer import AnomalyScorer
from atlas.reporting.report_generator import generate_markdown_report

class EvidencePipeline:
    """End-to-end evidence collection, analysis, scoring, and reporting pipeline."""

    def __init__(self):
        self.scorer = AnomalyScorer()

    def run(self, url: str) -> Finding:
        """
        Execute full 10-stage research pipeline on a target URL.
        """
        start_time = time.time()
        logger.info(f"Starting Project Atlas Evidence Pipeline for: {url}")

        # 1. URL Validation & Canonicalization
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        parsed = urlparse(url)
        canonical_domain = parsed.netloc or parsed.path
        timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        clean_name = canonical_domain.replace(":", "_").replace("/", "_").replace(".", "_")
        prefix = f"{clean_name}_{timestamp_slug}"
        finding_id = f"ATLAS-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{prefix[:16]}"

        artifacts: List[EvidenceArtifact] = []

        # 2. Capture Screenshot
        logger.info("[2/10] Capturing high-resolution Playwright screenshot...")
        ss_art, ss_err = capture_screenshot(url, prefix)
        if ss_art:
            artifacts.append(ss_art)

        # 3. Rendered HTML, Metadata & Clean Text
        logger.info("[3/10] Fetching rendered HTML and extracting metadata...")
        html_res = fetch_and_extract_html(url, prefix)
        if html_res.get("html_artifact"):
            artifacts.append(html_res["html_artifact"])
        if html_res.get("metadata_artifact"):
            artifacts.append(html_res["metadata_artifact"])

        # 4. Wayback Machine Historical Query
        logger.info("[4/10] Querying Internet Archive Wayback Machine...")
        wb_events, wb_summary = query_wayback_timeline(url)

        # 5. Common Crawl Historical Query
        logger.info("[5/10] Querying Common Crawl indexes...")
        cc_events, cc_summary = query_commoncrawl_timeline(url)

        # 6. Unified Timeline Construction
        logger.info("[6/10] Constructing unified temporal timeline...")
        live_now_ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        live_iso = datetime.now(timezone.utc).isoformat()
        live_event = TimelineEvent(
            timestamp=live_now_ts,
            datetime_iso=live_iso,
            source="live",
            status_code=html_res.get("status_code", 200),
            content_length=len(html_res.get("html_content", "")),
            mime_type=html_res.get("headers", {}).get("content-type", "text/html"),
            notes="Live inspection during pipeline execution"
        )

        unified_events, tl_metrics, tl_artifact = build_unified_timeline(
            url, prefix, wb_events, cc_events, live_event
        )
        artifacts.append(tl_artifact)

        # 7. Anomaly Scoring with Confidence and Evidence State
        logger.info("[7/10] Calculating Anomaly Score and Confidence...")
        score, confidence, classification, overall_state, signals = self.scorer.evaluate(
            timeline=unified_events,
            metadata=html_res.get("metadata", {}),
            html_content=html_res.get("html_content", ""),
            live_status=html_res.get("status_code", 200),
            timeline_metrics=tl_metrics
        )

        # 8. Save Comprehensive Evidence JSON
        logger.info("[8/10] Serializing complete evidence package...")
        evidence_json_filename = f"{prefix}_evidence.json"
        evidence_json_path = JSON_DIR / evidence_json_filename

        state_breakdown = {}
        for s in signals:
            state_key = s.evidence_state.value
            state_breakdown[state_key] = state_breakdown.get(state_key, 0) + 1
        
        evidence_payload = {
            "finding_id": finding_id,
            "target_url": url,
            "canonical_domain": canonical_domain,
            "timestamp": live_iso,
            "anomaly_score": score,
            "confidence": confidence,
            "classification": classification,
            "evidence_state": overall_state.value,
            "signals": [s.model_dump() for s in signals],
            "timeline_metrics": tl_metrics.model_dump(),
            "metadata": html_res.get("metadata", {}),
            "evidence_state_breakdown": state_breakdown,
            "artifacts": [a.model_dump() for a in artifacts]
        }

        with open(evidence_json_path, "w", encoding="utf-8") as f:
            json.dump(evidence_payload, f, indent=2)

        with open(evidence_json_path, "rb") as f:
            ev_bytes = f.read()

        ev_artifact = EvidenceArtifact(
            artifact_id=f"art_ev_{prefix}",
            artifact_type=ArtifactType.JSON,
            relative_path=str(evidence_json_path.relative_to(JSON_DIR.parent.parent)),
            file_name=evidence_json_filename,
            sha256=hashlib.sha256(ev_bytes).hexdigest(),
            size_bytes=len(ev_bytes),
            source="pipeline_engine",
            collection_method="serialization",
            metadata={"anomaly_score": score, "confidence": confidence}
        )
        artifacts.append(ev_artifact)

        # 9. Formulate Finding Model
        human_summary = (
            f"Target {url} analyzed with Anomaly Score {score} (Confidence: {confidence:.2f}, Classification: {classification}). "
            f"Observed {len(signals)} signals across a {tl_metrics.years_span}-year span with {tl_metrics.continuity_level.value} continuity."
        )

        finding = Finding(
            finding_id=finding_id,
            target_url=url,
            canonical_domain=canonical_domain,
            created_at=live_iso,
            anomaly_score=score,
            confidence=confidence,
            classification=classification,
            evidence_state=overall_state,
            signals=signals,
            artifacts=artifacts,
            timeline_summary=tl_metrics.model_dump(),
            metadata_summary=html_res.get("metadata", {}),
            evidence_state_breakdown=state_breakdown,
            human_summary=human_summary,
            machine_summary=evidence_payload,
            reproducible_command=f"python3 scripts/run_pipeline.py {url}",
            verification_status="verified_on_creation"
        )

        # Save finding in findings/
        finding_file = FINDINGS_DIR / f"{finding_id}.json"
        with open(finding_file, "w", encoding="utf-8") as f:
            f.write(finding.model_dump_json(indent=2))

        # 10. Generate Markdown Report
        logger.info("[10/10] Generating comprehensive Markdown research report...")
        report_path = generate_markdown_report(finding)
        logger.info(f"Report successfully written to: {report_path}")

        duration_total = (time.time() - start_time) * 1000
        logger.log_action(
            "run_evidence_pipeline",
            url,
            duration_total,
            True,
            extra={"finding_id": finding_id, "score": score, "confidence": confidence, "state": overall_state.value}
        )

        return finding
