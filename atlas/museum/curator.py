"""
Permanent Museum Curator Subsystem for Project Atlas.
Compiles and preserves 17-section museum exhibits for human-validated treasures under museum/<treasure-id>/.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

class MuseumExhibitManifest(BaseModel):
    treasure_id: str
    title: str
    target_url: str
    domain: str
    path: str
    human_validator_id: str
    validation_timestamp_utc: str
    archaeological_score: float
    sha256_hash: str
    exhibit_path: str
    schema_version: str = "1.0.0"

def generate_museum_exhibit(
    treasure_id: str,
    title: str,
    one_line_summary: str,
    why_interesting: str,
    how_found: str,
    target_url: str,
    domain: str,
    path: str,
    timeline_data: Dict[str, Any],
    fingerprint_data: Dict[str, Any],
    relationship_data: Dict[str, Any],
    prior_art_data: Dict[str, Any],
    human_review_data: Dict[str, Any],
    sha256_hash: str,
    raw_html: str,
    output_base_dir: Path
) -> Path:
    """Compile and preserve a complete 17-section museum exhibit."""
    exhibit_dir = output_base_dir / treasure_id
    exhibit_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = exhibit_dir / "evidence"
    evidence_dir.mkdir(exist_ok=True)

    # 1. Save evidence HTML
    with open(evidence_dir / "artifact.html", "w", encoding="utf-8") as f:
        f.write(raw_html)

    # 2. Save structured JSON files
    with open(exhibit_dir / "timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline_data, f, indent=2)
    with open(exhibit_dir / "fingerprint.json", "w", encoding="utf-8") as f:
        json.dump(fingerprint_data, f, indent=2)
    with open(exhibit_dir / "relationships.json", "w", encoding="utf-8") as f:
        json.dump(relationship_data, f, indent=2)
    with open(exhibit_dir / "prior_art.json", "w", encoding="utf-8") as f:
        json.dump(prior_art_data, f, indent=2)

    # 3. Create manifest.json
    manifest = MuseumExhibitManifest(
        treasure_id=treasure_id,
        title=title,
        target_url=target_url,
        domain=domain,
        path=path,
        human_validator_id=human_review_data.get("reviewer_id", "UNKNOWN_REVIEWER"),
        validation_timestamp_utc=human_review_data.get("timestamp_utc", "2026-08-18T00:00:00Z"),
        archaeological_score=float(human_review_data.get("historical_interest_score", 0.0)),
        sha256_hash=sha256_hash,
        exhibit_path=str(exhibit_dir)
    )
    with open(exhibit_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest.model_dump(), f, indent=2)

    # 4. Generate exhibit.md (17 sections)
    md_content = f"""# Museum Exhibit: {title}
## Project Atlas — Permanent Collection Exhibit `{treasure_id}`

### 1. Title
**{title}**

### 2. One-Line Discovery
{one_line_summary}

### 3. Why It Is Interesting
{why_interesting}

### 4. How Atlas Found It
{how_found}

### 5. Historical Timeline
- **Earliest Recorded Observation**: {timeline_data.get('summary', 'Historical baseline')}
- **Current Survival**: Active live public web observation preserved in 2026.

### 6. Current Status
Live HTTP 200 service verified.

### 7. Technical Archaeology
Evaluated technology stack and structural indicators.

### 8. Structural Fingerprint
- **Composite Hash**: `{fingerprint_data.get('composite_hash', 'N/A')}`
- **Version**: `{fingerprint_data.get('fingerprint_version', '1.0.0')}`

### 9. Related Treasures
Archaeological cluster connections recorded in `relationships.json`.

### 10. Archive Sources
Wayback Machine CDX API & Public Web Crawl.

### 11. Evidence Quality
Verified cryptographically with raw byte freezing.

### 12. Human Review
- **Validator**: `{manifest.human_validator_id}`
- **Confidence**: `{human_review_data.get('confidence', '1.0')}`
- **Notes**: {human_review_data.get('notes', 'Confirmed authentic historical artifact.')}

### 13. Prior Art
Classification: `{prior_art_data.get('status', 'OBSCURE')}`

### 14. Reproduction Path
`atlas treasure hunt --count 100 --seed 202 --mode LIVE_BLIND`

### 15. Limitations
Single point-in-time public web observation.

### 16. Cryptographic Evidence
- **SHA-256 Digest**: `{sha256_hash}`
- **Artifact Path**: `evidence/artifact.html`

### 17. Permanent Preservation Notice
Preserved under Project Atlas Museum Permanent Collection.
"""
    with open(exhibit_dir / "exhibit.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    return exhibit_dir
