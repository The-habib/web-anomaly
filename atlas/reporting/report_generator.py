"""Markdown research report generator for Project Atlas findings (Phase 0.5)."""

import json
from pathlib import Path
from atlas.core.config import REPORTS_DIR
from atlas.core.models import Finding

def generate_markdown_report(finding: Finding) -> Path:
    """
    Generate a standardized, publication-grade research report in Markdown
    with rigorous scientific language and evidence state breakdowns.
    """
    report_filename = f"REPORT_{finding.finding_id}.md"
    report_path = REPORTS_DIR / report_filename

    # Format screenshot markdown if available
    screenshot_section = "*No visual screenshot captured.*"
    for art in finding.artifacts:
        if art.artifact_type == "screenshot":
            screenshot_section = f"![Target Screenshot](../{art.relative_path})"
            break

    # Format signals table
    signals_rows = []
    all_limitations = []
    for sig in finding.signals:
        state_badge = f"`[{sig.evidence_state.value}]`"
        signals_rows.append(
            f"| **{sig.name}** | `{sig.category}` | {state_badge} | {sig.confidence:.2f} | +{sig.score_awarded} | {sig.description} |"
        )
        if sig.limitations:
            for lim in sig.limitations:
                all_limitations.append(f"- **{sig.name}**: {lim}")

    signals_table = "\n".join(signals_rows) if signals_rows else "| *No anomalies detected* | - | `[OBSERVED]` | 1.00 | 0 | Standard web profile |"

    # Format timeline table summary
    tl = finding.timeline_summary
    timeline_section = f"""
- **First Recorded Snapshot**: `{tl.get('first_seen', 'N/A')}` (`{tl.get('earliest_iso', 'N/A')}`)
- **Latest Recorded Snapshot**: `{tl.get('last_seen', 'N/A')}` (`{tl.get('latest_iso', 'N/A')}`)
- **Calculated Span**: `{tl.get('years_span', 0)} years`
- **Total Historical Observations**: `{tl.get('total_captures', 0)} captures`
- **Unique Years Observed**: `{tl.get('unique_years_observed', 0)} years` ({tl.get('observed_year_ratio', 0.0) * 100:.1f}% coverage)
- **Longest Evidence Gap**: `{tl.get('longest_evidence_gap_years', 0.0)} years`
- **Continuity Classification**: `{tl.get('continuity_level', 'HISTORICAL_PRESENCE')}` (*{tl.get('continuity_claim', 'unproven')}*)
"""

    # Format artifacts table
    artifact_rows = []
    for art in finding.artifacts:
        artifact_rows.append(
            f"| `{art.artifact_type.value}` | `{art.file_name}` | `{art.sha256[:16]}...` | {art.size_bytes:,} bytes | `{art.source}` |"
        )
    artifacts_table = "\n".join(artifact_rows)

    meta = finding.metadata_summary
    metadata_formatted = f"""
- **Document Title**: {meta.get('title', 'N/A')}
- **HTML Generator / CMS**: `{meta.get('generator', 'None detected')}`
- **Outbound Links Count**: {meta.get('links_count', 0)}
- **External Scripts Count**: {meta.get('scripts_count', 0)}
- **Images Count**: {meta.get('images_count', 0)}
- **Document Type**: `{meta.get('doctype', 'HTML5/Standard')}`
"""

    limitations_formatted = "\n".join(all_limitations) if all_limitations else "- No critical observational limitations flagged."

    report_content = f"""# Research Finding Report: {finding.finding_id}

**Project Atlas — Autonomous Web Anomaly Laboratory**  
*Mission Finding Classification & Evidence Dossier*

---

## 1. Executive Summary

| Parameter | Value |
| :--- | :--- |
| **Finding ID** | `{finding.finding_id}` |
| **Target URL** | [{finding.target_url}]({finding.target_url}) |
| **Canonical Domain** | `{finding.canonical_domain}` |
| **Investigation Timestamp** | `{finding.created_at}` |
| **Anomaly Score** | **`{finding.anomaly_score}`** |
| **Confidence Score** | **`{finding.confidence:.2f}`** |
| **Overall Evidence State** | **`[{finding.evidence_state.value}]`** |
| **Classification** | **{finding.classification}** |

### Scientific Analysis
{finding.human_summary}

---

## 2. Detected Anomaly Signals & Evidence States

| Signal | Category | Evidence State | Confidence | Weight | Evidence Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
{signals_table}

---

## 3. Visual Evidence

{screenshot_section}

---

## 4. Temporal Analysis & Continuity

{timeline_section}

---

## 5. Technical Metadata

{metadata_formatted}

---

## 6. Observational Limitations & Gaps

{limitations_formatted}

---

## 7. Permanent Cryptographic Evidence Artifacts

| Type | File Name | SHA-256 Digest | Size | Source |
| :--- | :--- | :--- | :--- | :--- |
{artifacts_table}

---

## 8. Machine Summary (JSON)

```json
{json.dumps(finding.machine_summary, indent=2)}
```

---

## 9. Reproducibility

To re-run this exact investigation and reproduce the evidence chain:
```bash
{finding.reproducible_command}
```
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_path
