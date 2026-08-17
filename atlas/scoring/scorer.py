"""Config-driven anomaly scoring engine for Project Atlas."""

import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from atlas.core.config import SCORING_RULES_PATH
from atlas.core.models import AnomalySignal, TimelineEvent

class AnomalyScorer:
    """Evaluates evidence against configured scoring rules to calculate Anomaly Score."""

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
        live_status: int = 200
    ) -> Tuple[int, str, List[AnomalySignal]]:
        """
        Evaluate timeline, metadata, and HTML content to produce:
        (total_score, classification, list_of_signals)
        """
        signals: List[AnomalySignal] = []

        # 1. 15+ Year Web Persistence Check
        if timeline and len(timeline) >= 2:
            years = []
            for ev in timeline:
                try:
                    if len(ev.timestamp) >= 4:
                        years.append(int(ev.timestamp[:4]))
                except ValueError:
                    pass
            if years:
                earliest_year = min(years)
                current_year = datetime.now(timezone.utc).year
                if (current_year - earliest_year) >= 15:
                    r = self.rules_map.get("persistence_15yr")
                    if r:
                        signals.append(AnomalySignal(
                            signal_id="persistence_15yr",
                            name=r["name"],
                            category=r["category"],
                            weight=r["weight"],
                            score_awarded=r["weight"],
                            description=f"First recorded in {earliest_year} ({current_year - earliest_year} years continuous lifespan).",
                            evidence_keys=["timeline_first_seen", "timeline_span_years"]
                        ))

        # 2. Resurrection Check (Gap of >= 2 years with 404/failure then return)
        if timeline and len(timeline) >= 3 and live_status == 200:
            sorted_events = sorted(timeline, key=lambda x: x.timestamp)
            has_gap = False
            last_active_year = None
            gap_description = ""

            for i in range(len(sorted_events) - 1):
                cur = sorted_events[i]
                nxt = sorted_events[i + 1]
                try:
                    y1 = int(cur.timestamp[:4])
                    y2 = int(nxt.timestamp[:4])
                    # If gap > 2 years and current or next indicates transition
                    if (y2 - y1) >= 2 and (cur.status_code in [404, 500, 502, 503] or nxt.status_code == 200):
                        has_gap = True
                        gap_description = f"Gap between {y1} (status {cur.status_code}) and {y2} (status {nxt.status_code})."
                        break
                except Exception:
                    continue

            if has_gap:
                r = self.rules_map.get("resurrection")
                if r:
                    signals.append(AnomalySignal(
                        signal_id="resurrection",
                        name=r["name"],
                        category=r["category"],
                        weight=r["weight"],
                        score_awarded=r["weight"],
                        description=f"Disappeared and subsequently returned: {gap_description}",
                        evidence_keys=["timeline_gaps", "resurrection_interval"]
                    ))

        # 3. Technology Fossil Detection
        fossil_patterns = [
            (r'generator["\']?\s+content=["\']?(Microsoft FrontPage|Macromedia|Adobe PageMill|NetObjects|Dreamweaver [1-8]|HotDog)', "Legacy Web Authoring Tool"),
            (r'(\.swf|application/x-shockwave-flash|clsid:d27cdb6e-ae6d-11cf-96b8-444553540000)', "Macromedia/Adobe Flash Embed"),
            (r'(<frameset|<frame\s+src|<applet)', "HTML Frameset or Java Applet"),
            (r'<!DOCTYPE\s+html\s+PUBLIC\s+"-//W3C//DTD\s+HTML\s+3\.2', "HTML 3.2 Specification DTD"),
            (r'<!DOCTYPE\s+html\s+PUBLIC\s+"-//W3C//DTD\s+XHTML\s+1\.0\s+Transitional', "XHTML 1.0 Transitional DTD"),
            (r'(<marquee|<blink|<font\s+color|<center>)', "Deprecated 1990s Formatting Tags"),
        ]

        detected_fossils = []
        for pattern, label in fossil_patterns:
            if re.search(pattern, html_content, re.IGNORECASE):
                detected_fossils.append(label)

        if detected_fossils:
            r = self.rules_map.get("technology_fossil")
            if r:
                signals.append(AnomalySignal(
                    signal_id="technology_fossil",
                    name=r["name"],
                    category=r["category"],
                    weight=r["weight"],
                    score_awarded=r["weight"],
                    description=f"Detected legacy markers: {', '.join(detected_fossils)}.",
                    evidence_keys=["fossil_signatures"]
                ))

        # 4. Robots.txt Anomaly / Sitemap
        robots_info = metadata.get("robots_txt", {})
        if robots_info.get("has_unusual_disallows"):
            r = self.rules_map.get("robots_txt_anomaly")
            if r:
                signals.append(AnomalySignal(
                    signal_id="robots_txt_anomaly",
                    name=r["name"],
                    category=r["category"],
                    weight=r["weight"],
                    score_awarded=r["weight"],
                    description="Robots.txt contains anomalous disallows or hidden paths.",
                    evidence_keys=["robots_disallows"]
                ))

        sitemap_info = metadata.get("sitemap", {})
        if sitemap_info.get("is_hidden_or_unlisted"):
            r = self.rules_map.get("hidden_sitemap")
            if r:
                signals.append(AnomalySignal(
                    signal_id="hidden_sitemap",
                    name=r["name"],
                    category=r["category"],
                    weight=r["weight"],
                    score_awarded=r["weight"],
                    description="Discovered unlisted XML sitemap at non-standard endpoint.",
                    evidence_keys=["sitemap_url"]
                ))

        # 5. Open Directory / Forgotten Archive
        if "<title>Index of /" in html_content or "<h1>Index of /" in html_content:
            r = self.rules_map.get("forgotten_archive")
            if r:
                signals.append(AnomalySignal(
                    signal_id="forgotten_archive",
                    name=r["name"],
                    category=r["category"],
                    weight=r["weight"],
                    score_awarded=r["weight"],
                    description="Target is an open Apache/Nginx directory listing.",
                    evidence_keys=["directory_listing"]
                ))

        # Calculate Total Score
        total_score = sum(s.score_awarded for s in signals)

        # Determine Classification
        if total_score >= 8:
            classification = "Tier-1 Major Web Anomaly"
        elif total_score >= 5:
            classification = "Tier-2 Significant Historical Anomaly"
        elif total_score >= 2:
            classification = "Tier-3 Minor Temporal / Structural Anomaly"
        else:
            classification = "Standard Web Surface"

        return total_score, classification, signals
