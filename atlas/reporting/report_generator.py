"""Markdown research report generator for Project Atlas findings."""

import json
from pathlib import Path
from atlas.core.config import REPORTS_DIR
from atlas.core.models import Finding

def generate_markdown_report(finding: Finding) -> Path:
    """
    Generate a standardized, publication-grade research report in Markdown.
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
    for sig in finding.signals:
        signals_rows.append(
            f"| **{sig.name}** | `{sig.category}` | +{sig.score_awarded} | {sig.description} |"
        )
    signals_table = "\n".join(signals_rows) if signals_rows else "| *No anomalies detected* | - | 0 | Standard web profile |"

    # Format timeline table summary
    tl = finding.timeline_summary
    timeline_section = f"""
- **First Recorded Snapshot**: `{tl.get('first_seen', 'N/A')}` (`{tl.get('earliest_iso', 'N/A')}`)
- **Latest Recorded Snapshot**: `{tl.get('last_seen', 'N/A')}` (`{tl.get('latest_iso', 'N/A')}`)
- **Calculated Lifespan**: `{tl.get('span_years', 0)} years`
- **Total Historical Observations**: `{tl.get('total_events', 0)}`
"""

    # Format artifacts table
    artifact_rows = []
    for art in finding.artifacts:
        artifact_rows.append(
            f"| `{art.artifact_type.value}` | `{art.file_name}` | `{art.sha256[:16]}...` | {art.size_bytes:,} bytes |"
        )
    artifacts_table = "\n".join(artifact_rows)

    meta = finding.metadata_summary
    metadata_formatted = f"""
- **Document Title**: {meta.get('title', 'N/A')}
- **HTML Generator / CMS**: `{meta.get('generator', 'None detected')}`
- **Outbound Links Count**: {meta.get('links_count', 0)}
- **External Scripts Count**: {meta.get('scripts_count', 0)}
- **Images Count**: {meta.get('images_count', 0)}
"""

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
| **Classification** | **{finding.classification}** |

### Human Analysis
{finding.human_summary}

---

## 2. Detected Anomaly Signals

| Signal | Category | Weight | Evidence Description |
| :--- | :--- | :--- | :--- |
{signals_table}

---

## 3. Visual Evidence

{screenshot_section}

---

## 4. Temporal Analysis & Timeline

{timeline_section}

---

## 5. Technical Metadata

{metadata_formatted}

---

## 6. Permanent Evidence Artifacts

| Type | File Name | SHA-256 Digest | Size |
| :--- | :--- | :--- | :--- |
{artifacts_table}

---

## 7. Machine Summary (JSON)

```json
{json.dumps(finding.machine_summary, indent=2)}
```

---

## 8. Reproducibility

To re-run this exact investigation and reproduce the evidence chain:
```bash
{finding.reproducible_command}
```
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_path
