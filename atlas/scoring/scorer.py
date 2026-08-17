"""Config-driven, false-positive resistant anomaly scoring engine for Project Atlas (Phase 0.5)."""

import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from bs4 import BeautifulSoup, Comment

from atlas.core.config import SCORING_RULES_PATH
from atlas.core.models import (
    AnomalySignal, EvidenceState, TimelineEvent,
    ContinuityLevel, TimelineContinuityMetrics
)
from atlas.pipeline.timeline import compute_timeline_continuity

class AnomalyScorer:
    """
    Evaluates evidence against strict scientific criteria, calculating both
    an Anomaly Score and an orthogonal Confidence Score (0.0 to 1.0).
    """

    def __init__(self, rules_path=SCORING_RULES_PATH):
        self.rules_path = rules_path
        self.rules_data = self._load_rules()
        self.rules_map = {r["id"]: r for r in self.rules_data.get("rules", [])}

    def _load_rules(self) -> Dict[str, Any]:
        if self.rules_path.exists():
            try:
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"rules": [], "min_discovery_threshold": 4}

    def evaluate(
        self,
        timeline: List[TimelineEvent],
        metadata: Dict[str, Any],
        html_content: str,
        live_status: int = 200,
        timeline_metrics: TimelineContinuityMetrics = None
    ) -> Tuple[int, float, str, EvidenceState, List[AnomalySignal]]:
        """
        Evaluate timeline, metadata, and HTML DOM to produce:
        (total_score, confidence_score, classification, overall_evidence_state, signals)
        """
        signals: List[AnomalySignal] = []

        if timeline_metrics is None:
            timeline_metrics = compute_timeline_continuity(timeline)

        # -------------------------------------------------------------
        # 1. Temporal Persistence & Continuity Evaluation
        # -------------------------------------------------------------
        if timeline_metrics.years_span >= 15:
            r = self.rules_map.get("persistence_15yr", {"name": "15+ Year Web Persistence", "category": "temporal", "weight": 2})
            
            if timeline_metrics.continuity_level in (ContinuityLevel.CONTINUOUS_PRESENCE, ContinuityLevel.HIGH_CAPTURE_CONTINUITY):
                signals.append(AnomalySignal(
                    signal_id="persistence_15yr",
                    name=r["name"],
                    category=r["category"],
                    weight=r["weight"],
                    score_awarded=r["weight"],
                    evidence_state=EvidenceState.VALIDATED,
                    confidence=0.92 if timeline_metrics.continuity_level == ContinuityLevel.CONTINUOUS_PRESENCE else 0.80,
                    description=f"Verified historical presence across {timeline_metrics.unique_years_observed} distinct years over a {timeline_metrics.years_span}-year span with high capture density (max gap {timeline_metrics.longest_evidence_gap_years} yrs).",
                    observed_facts=[
                        f"First seen in archive: {timeline_metrics.first_seen}",
                        f"Total captures recorded: {timeline_metrics.total_captures}",
                        f"Coverage ratio: {timeline_metrics.observed_year_ratio * 100:.1f}% of years"
                    ],
                    inferences=["High capture continuity suggests stable long-term hosting and maintenance."],
                    evidence_keys=["timeline_span_years", "observed_year_ratio", "continuity_level"]
                ))
            elif timeline_metrics.continuity_level == ContinuityLevel.LONG_SPAN_PRESENCE:
                signals.append(AnomalySignal(
                    signal_id="persistence_15yr",
                    name=r["name"],
                    category=r["category"],
                    weight=r["weight"],
                    score_awarded=1,  # Reduced score for sparse continuity
                    evidence_state=EvidenceState.CANDIDATE,
                    confidence=0.55,
                    description=f"Observed span of {timeline_metrics.years_span} years, but with notable evidence gaps (longest gap: {timeline_metrics.longest_evidence_gap_years} yrs). Continuous persistence is not proven.",
                    observed_facts=[
                        f"Earliest capture: {timeline_metrics.first_seen}",
                        f"Observed in {timeline_metrics.unique_years_observed} of {timeline_metrics.years_span + 1} years"
                    ],
                    inferences=["Subject may have experienced unrecorded downtime or archival omissions."],
                    limitations=["Archive coverage is below dense verification threshold."],
                    evidence_keys=["longest_evidence_gap_years"]
                ))
            else:
                # Sparse captures (e.g. 2 captures over 20 years) -> INSUFFICIENT
                signals.append(AnomalySignal(
                    signal_id="persistence_15yr",
                    name=r["name"],
                    category=r["category"],
                    weight=r["weight"],
                    score_awarded=0,
                    evidence_state=EvidenceState.INSUFFICIENT,
                    confidence=0.20,
                    description=f"Sparse captures detected across {timeline_metrics.years_span} years ({timeline_metrics.total_captures} captures, max gap {timeline_metrics.longest_evidence_gap_years} yrs). Evidence density is insufficient to assert continuous lifespan.",
                    observed_facts=[
                        f"Isolated captures observed in {timeline_metrics.first_seen} and {timeline_metrics.last_seen}",
                        f"Observed in only {timeline_metrics.unique_years_observed} unique years"
                    ],
                    limitations=["Continuous lifespan cannot be concluded without intermediate archival records."],
                    evidence_keys=["evidence_state_insufficient"]
                ))

        # -------------------------------------------------------------
        # 2. Resurrection Detection (Requiring Documented Failure Evidence)
        # -------------------------------------------------------------
        if timeline and len(timeline) >= 3 and live_status == 200:
            sorted_events = sorted(timeline, key=lambda x: x.timestamp)
            documented_failures = []
            resurrection_gap = 0.0
            pre_failure_active = None
            post_failure_active = None

            for i in range(len(sorted_events)):
                ev = sorted_events[i]
                if ev.status_code in (404, 410, 500, 502, 503):
                    documented_failures.append(ev)
                    # Look back for active capture
                    if pre_failure_active is None and i > 0:
                        pre_failure_active = sorted_events[i - 1]
                    # Look ahead for recovery capture
                    for j in range(i + 1, len(sorted_events)):
                        if sorted_events[j].status_code == 200:
                            post_failure_active = sorted_events[j]
                            break

            r_res = self.rules_map.get("resurrection", {"name": "Domain / URL Resurrection", "category": "temporal", "weight": 5})

            if documented_failures and pre_failure_active and post_failure_active:
                try:
                    y_pre = int(pre_failure_active.timestamp[:4])
                    y_post = int(post_failure_active.timestamp[:4])
                    resurrection_gap = max(0, y_post - y_pre)
                except Exception:
                    resurrection_gap = 0

                if len(documented_failures) >= 2 and resurrection_gap >= 2:
                    # Confirmed resurrection with multi-capture documented failure
                    signals.append(AnomalySignal(
                        signal_id="resurrection",
                        name=r_res["name"],
                        category=r_res["category"],
                        weight=r_res["weight"],
                        score_awarded=r_res["weight"],
                        evidence_state=EvidenceState.VALIDATED,
                        confidence=0.88,
                        description=f"Documented failure period ({len(documented_failures)} failed captures) between {pre_failure_active.timestamp[:4]} and {post_failure_active.timestamp[:4]} followed by verified active return.",
                        observed_facts=[
                            f"Pre-failure active capture: {pre_failure_active.timestamp} (status {pre_failure_active.status_code})",
                            f"Documented failure captures: {len(documented_failures)} records with status in {[f.status_code for f in documented_failures]}",
                            f"Post-recovery active capture: {post_failure_active.timestamp} (status {post_failure_active.status_code})"
                        ],
                        inferences=["Target experienced verified offline period followed by re-activation."],
                        evidence_keys=["documented_failure_captures", "resurrection_interval"]
                    ))
                else:
                    # Single failure or short gap -> Candidate resurrection
                    signals.append(AnomalySignal(
                        signal_id="resurrection",
                        name=r_res["name"],
                        category=r_res["category"],
                        weight=r_res["weight"],
                        score_awarded=2,
                        evidence_state=EvidenceState.CANDIDATE,
                        confidence=0.45,
                        description=f"Isolated failure record detected between active periods ({pre_failure_active.timestamp[:4]} to {post_failure_active.timestamp[:4]}). Candidate resurrection.",
                        observed_facts=[f"Failure status {documented_failures[0].status_code} at {documented_failures[0].timestamp}"],
                        limitations=["Sparse failure captures; could represent transient server downtime rather than true abandonment."],
                        evidence_keys=["candidate_resurrection"]
                    ))
            elif timeline_metrics.longest_evidence_gap_years >= 3.0:
                # Large archive gap with ZERO documented failures -> Pure archive gap, NOT resurrection!
                signals.append(AnomalySignal(
                    signal_id="resurrection",
                    name="Archival Coverage Gap",
                    category="observational",
                    weight=0,
                    score_awarded=0,
                    evidence_state=EvidenceState.INSUFFICIENT,
                    confidence=0.15,
                    description=f"Archival observation gap of {timeline_metrics.longest_evidence_gap_years} years observed without documented failure records. Absence of evidence is not evidence of disappearance.",
                    observed_facts=[f"Longest unobserved gap: {timeline_metrics.longest_evidence_gap_years} years"],
                    limitations=["Archive crawlers did not visit the URL during this interval; domain status is unrecorded."],
                    evidence_keys=["archive_gap_no_failures"]
                ))

        # -------------------------------------------------------------
        # 3. DOM-Aware Technology Fossil Detection (False-Positive Resistant)
        # -------------------------------------------------------------
        if html_content:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Remove comments
            for comment in soup.find_all(string=lambda string: isinstance(string, Comment)):
                comment.extract()

            # Remove code blocks, preformatted text, blockquotes, and articles before structural checks
            content_containers = soup.find_all(["code", "pre", "samp", "kbd", "blockquote"])
            for container in content_containers:
                container.extract()

            structural_fossils = []
            meta_fossils = []

            # 3a. Root DOCTYPE inspection
            if soup.contents and "DOCTYPE" in str(soup.contents[0]):
                doctype_str = str(soup.contents[0]).upper()
                if "HTML 3.2" in doctype_str or "HTML 2.0" in doctype_str:
                    structural_fossils.append("HTML 2.0/3.2 DTD")
                elif "XHTML 1.0 TRANSITIONAL" in doctype_str:
                    structural_fossils.append("XHTML 1.0 Transitional DTD")

            # 3b. Head Generator Meta inspection
            generator_tag = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "generator"})
            if generator_tag and generator_tag.get("content"):
                gen = generator_tag["content"]
                if re.search(r"(Microsoft FrontPage|Macromedia|Adobe PageMill|NetObjects|Dreamweaver [1-8]|HotDog|Claris)", gen, re.I):
                    meta_fossils.append(f"Authoring Tool Generator: {gen}")

            # 3c. Active layout tags outside article/code blocks
            body = soup.find("body") or soup
            if soup.find("frameset") or soup.find("frame"):
                structural_fossils.append("HTML Frameset Architecture")
            if soup.find("applet"):
                structural_fossils.append("Java Applet Embed")
            if soup.find("embed", attrs={"type": re.compile(r"shockwave-flash", re.I)}) or soup.find("object", attrs={"classid": re.compile(r"d27cdb6e", re.I)}):
                structural_fossils.append("Active Flash/Shockwave Object")

            # Deprecated styling in active DOM
            deprecated_tags = body.find_all(["marquee", "blink"])
            if deprecated_tags:
                structural_fossils.append(f"Active Deprecated Tags (<{deprecated_tags[0].name}>)")

            r_fossil = self.rules_map.get("technology_fossil", {"name": "Historical Technology Fossil", "category": "technological", "weight": 4})

            all_fossil_markers = structural_fossils + meta_fossils
            if all_fossil_markers:
                signals.append(AnomalySignal(
                    signal_id="technology_fossil",
                    name=r_fossil["name"],
                    category=r_fossil["category"],
                    weight=r_fossil["weight"],
                    score_awarded=r_fossil["weight"],
                    evidence_state=EvidenceState.VALIDATED,
                    confidence=0.88,
                    description=f"Verified legacy technologies embedded in active document structure: {', '.join(all_fossil_markers)}.",
                    observed_facts=[f"Detected: {m}" for m in all_fossil_markers],
                    inferences=["Target page preserves pre-modern markup and rendering architecture."],
                    evidence_keys=["structural_fossil_signatures"]
                ))

        # -------------------------------------------------------------
        # 4. Multi-Signal Directory Index / Archive Evaluation
        # -------------------------------------------------------------
        if "<title>Index of /" in html_content or "<h1>Index of /" in html_content:
            soup_dir = BeautifulSoup(html_content, "html.parser")
            text_body = soup_dir.get_text()

            # Check for legacy file dates (1990s or 2000-2009)
            has_legacy_dates = bool(re.search(r"(199\d|200[0-9])-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])", text_body))
            # Check for legacy archive extensions
            has_archive_files = bool(re.search(r"\.(tar\.gz|tar\.bz2|zip|tgz|ps|dvi|hqx|sit|c|pas|asm)\b", text_body, re.I))

            r_arch = self.rules_map.get("forgotten_archive", {"name": "Forgotten Public File / Directory Index", "category": "content", "weight": 3})

            if has_legacy_dates and has_archive_files:
                signals.append(AnomalySignal(
                    signal_id="forgotten_archive",
                    name=r_arch["name"],
                    category=r_arch["category"],
                    weight=r_arch["weight"],
                    score_awarded=r_arch["weight"],
                    evidence_state=EvidenceState.VALIDATED,
                    confidence=0.85,
                    description="Open directory listing containing historical file modification dates and legacy archive artifacts.",
                    observed_facts=["Directory listing contains files with pre-2010 timestamps and historical archive extensions."],
                    evidence_keys=["directory_listing_historical_files"]
                ))
            elif has_archive_files:
                signals.append(AnomalySignal(
                    signal_id="forgotten_archive",
                    name=r_arch["name"],
                    category=r_arch["category"],
                    weight=r_arch["weight"],
                    score_awarded=1,
                    evidence_state=EvidenceState.CANDIDATE,
                    confidence=0.50,
                    description="Open directory listing with archive files, but lacking verified legacy timestamps.",
                    observed_facts=["Directory listing contains downloadable archives."],
                    evidence_keys=["directory_listing_files"]
                ))
            else:
                # Ordinary empty or modern default directory index -> 0 anomaly points
                signals.append(AnomalySignal(
                    signal_id="forgotten_archive",
                    name="Standard Server Directory Index",
                    category="observational",
                    weight=0,
                    score_awarded=0,
                    evidence_state=EvidenceState.OBSERVED,
                    confidence=0.90,
                    description="Default server directory index with modern or non-archaeological file listings.",
                    observed_facts=["Server directory listing is active."],
                    evidence_keys=["standard_directory_index"]
                ))

        # -------------------------------------------------------------
        # 5. Composite Score & Confidence Calculation
        # -------------------------------------------------------------
        total_score = sum(s.score_awarded for s in signals if s.evidence_state in (EvidenceState.VALIDATED, EvidenceState.CANDIDATE))
        
        # Calculate composite confidence
        active_signals = [s for s in signals if s.score_awarded > 0]
        if active_signals:
            avg_signal_conf = sum(s.confidence for s in active_signals) / len(active_signals)
            timeline_density_factor = min(1.0, (timeline_metrics.observed_year_ratio * 0.6) + (0.4 if timeline_metrics.total_captures >= 10 else 0.2))
            composite_confidence = round((avg_signal_conf * 0.7) + (timeline_density_factor * 0.3), 2)
        else:
            composite_confidence = 0.95  # Confident that this is a standard, non-anomalous page

        # Determine overall Evidence State
        if any(s.evidence_state == EvidenceState.VALIDATED and s.score_awarded > 0 for s in signals):
            overall_state = EvidenceState.VALIDATED
        elif any(s.evidence_state == EvidenceState.CANDIDATE and s.score_awarded > 0 for s in signals):
            overall_state = EvidenceState.CANDIDATE
        elif total_score == 0:
            overall_state = EvidenceState.OBSERVED
        else:
            overall_state = EvidenceState.INSUFFICIENT

        # Determine Classification
        if total_score >= 8 and composite_confidence >= 0.70:
            classification = "Tier-1 Major Web Anomaly"
        elif total_score >= 5 and composite_confidence >= 0.60:
            classification = "Tier-2 Significant Historical Anomaly"
        elif total_score >= 2 and composite_confidence >= 0.40:
            classification = "Tier-3 Minor Temporal / Structural Anomaly"
        else:
            classification = "Standard Web Surface"

        return total_score, composite_confidence, classification, overall_state, signals
