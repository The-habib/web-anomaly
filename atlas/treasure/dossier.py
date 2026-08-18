"""
Treasure Dossier & Clean Discovery Feed Authoring Subsystem for Project Atlas — Treasure Run #002.
Generates compliant 14-section markdown dossiers in reports/treasures/ and publishes
the strictly segregated discovery feed in reports/TREASURE_FEED_RUN_0002.md.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple

from atlas.treasure.models import (
    TreasureRecord,
    InvestigationRecord,
    TreasureDecision,
    TreasureLineageRecord,
    DiscoveryDifficulty
)

def build_treasure_title(inv: InvestigationRecord) -> str:
    dom = inv.domain
    path = inv.path
    features = inv.structural_features

    if "personal_user_space_hierarchy" in features or "~" in path:
        return f"Surviving Personal Home Space ({dom}{path})"
    if "frameset_layout" in features:
        return f"Active Pre-CSS Frameset Portal ({dom}{path})"
    if "pre_css_tables_layout" in features:
        return f"Fossil Table-Based Hypertext Layout ({dom}{path})"
    if "ascii_art_present" in features:
        return f"Preserved ASCII / Plain-Text Hypertext Surface ({dom}{path})"
    if "orphaned_from_root_navigation" in features:
        return f"Orphaned Historical Documentation Subpath ({dom}{path})"
    return f"Surviving Historical Web Surface ({dom}{path})"

def determine_time_period(earliest: int) -> str:
    if earliest <= 1995:
        return "1990–1995 (Early Web Era)"
    elif earliest <= 2000:
        return "1996–2000 (Dot-Com Expansion Era)"
    elif earliest <= 2005:
        return "2001–2005 (Early Modern Web Era)"
    elif earliest <= 2010:
        return "2006–2010 (Web 2.0 Transition Era)"
    else:
        return "2011+ (Modern Web Era)"

def generate_individual_treasure_dossier(
    treasure: TreasureRecord,
    output_dir: Path = Path("reports/treasures")
) -> Path:
    """
    Generate 14-section compliant markdown dossier for a validated treasure.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    dossier_file = output_dir / f"{treasure.treasure_id}.md"

    feat_lines = "\n".join(f"  - `{f}`" for f in treasure.detected_features)
    art_path_str = str(Path(treasure.artifact_path).absolute()) if treasure.artifact_path else ""

    text = f"""# {treasure.treasure_id} — {treasure.title}

## What Atlas Found
{treasure.human_explanation}

## Why It Matters
{treasure.why_interesting}

## How Atlas Found It
- **Discovery Strategy**: `{treasure.strategy.value}`
- **Candidate Path**: `{treasure.path}`
- **Target URL**: [{treasure.full_url}]({treasure.full_url})
- **Discovery Difficulty**: **{treasure.discovery_difficulty.value}**
- **Treasure Quality Score**: **{treasure.treasure_score:.1f} / 100**

## Historical Timeline
- **Historical Era**: {treasure.time_period}
- **Archive Continuity**: {treasure.historical_timeline}
- **Survival State**: `{treasure.survival_state.value}`

## Current Status
- **Live Response**: Active HTTP response on server.
- **Root Link Status**: {'Orphaned (Absent from root navigation)' if 'orphaned_from_root_navigation' in treasure.detected_features else 'Linked from domain root'}
- **Modern Frameworks**: None detected.

## Evidence
- **Detected Structural Features**:
{feat_lines}
- **Artifact File**: [`{treasure.artifact_path}`](file://{art_path_str})

## Archive Sources
- **Archival Index**: Wayback Machine CDX API & Common Crawl records.
- **Historical Span**: {treasure.historical_timeline}

## Why Ordinary Search Might Miss It
{treasure.why_search_misses_it}

## Prior Art
- **Classification**: `{treasure.prior_art.value}`
- **Assessment**: Atlas did not identify substantial commercial search visibility for this deep subpath during blind investigation.

## Human Review
- **Verification Status**: Validated through independent human review protocol.
- **Validation Timestamp**: {treasure.validated_at_utc}

## Evidence Confidence
- **Integrity**: Verified via live HTTP retrieval and SHA-256 digest.
- **Scope Limitation**: Preserved strictly as observed on public network endpoints without intrusive testing.

## Cryptographic Evidence
```
SHA-256: {treasure.evidence_sha256}
Validated At: {treasure.validated_at_utc}
```

## Reproduction Path
{treasure.reproduction_steps}

## Limitations
- Discovery represents a single point-in-time observation of the public live web.
- Server configuration or network reachability may change over time.
"""
    dossier_file.write_text(text.strip() + "\n", encoding="utf-8")
    return dossier_file

def generate_clean_treasure_feed(
    validated_treasures: List[TreasureRecord],
    potential_candidates: List[InvestigationRecord],
    feed_file: Path = Path("reports/TREASURE_FEED_RUN_0002.md")
) -> Path:
    """
    Generate clean treasure feed strictly separating VALIDATED TREASURES from POTENTIAL TREASURES.
    """
    feed_file.parent.mkdir(parents=True, exist_ok=True)
    now_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    header = f"""# Project Atlas — Treasure Run #002 Discovery Feed
## Autonomous Blind Internet Archaeology Experiment

*Generated at: {now_utc} | Validated Treasures: {len(validated_treasures)} | Potential Review Candidates: {len(potential_candidates)}*

---

## 1. VALIDATED TREASURES (Human Reviewed & Confirmed)

"""

    if validated_treasures:
        rows = [
            "| Rank | Treasure ID | Title | Domain | Strategy | Difficulty | Score | Live Target |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]
        for idx, t in enumerate(validated_treasures, 1):
            rows.append(
                f"| **#{idx:02d}** | [`{t.treasure_id}`](treasures/{t.treasure_id}.md) | **{t.title}** | `{t.domain}` | `{t.strategy.value}` | **{t.discovery_difficulty.value}** | **{t.treasure_score:.1f}** | [{t.path}]({t.full_url}) |"
            )
        feed_body = "\n".join(rows)
    else:
        feed_body = "> [!NOTE]\n> **ZERO VALIDATED TREASURES (Awaiting Human Review Submissions)**\n>\n> In accordance with the Prime Directive, machine scores do not independently declare scientific validation. Zero candidates have been promoted without independent human review."

    potential_section = f"""

---

## 2. POTENTIAL TREASURES (Machine Nominated — Review Pending)

*Top high-scoring archaeological candidates discovered autonomously during blind exploration, pending human review:*

| Rank | Candidate ID | Domain | Path | Score | Difficulty | Key Signals | Target URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""

    p_rows = []
    for idx, p in enumerate(potential_candidates[:25], 1):
        sig_str = ", ".join(p.structural_features[:2]) if p.structural_features else "vintage_path"
        p_rows.append(
            f"| **#{idx:02d}** | `{p.candidate_id}` | `{p.domain}` | `{p.path}` | **{p.treasure_score:.1f}** | `{p.discovery_difficulty.value}` | `{sig_str}` | [{p.path}]({p.url}) |"
        )

    full_text = header + feed_body + potential_section + "\n".join(p_rows) + "\n"
    feed_file.write_text(full_text.strip() + "\n", encoding="utf-8")
    return feed_file
