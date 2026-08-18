"""
Unified Multi-Dimensional Fingerprint Engine for Project Atlas.
Compiles structural, technology, and visual fingerprints into a deterministic archaeological profile.
Tracks fingerprint_version and guarantees reproducible outputs for identical artifacts.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from atlas.fingerprint.structure import compute_structure_fingerprint, HtmlStructureFingerprint
from atlas.fingerprint.technology import compute_technology_fingerprint, TechnologyFingerprint
from atlas.fingerprint.visual import compute_visual_fingerprint, VisualLayoutFingerprint

FINGERPRINT_VERSION = "1.0.0"

class UnifiedFingerprint(BaseModel):
    fingerprint_id: str
    artifact_sha256: str
    url: str
    fingerprint_version: str = FINGERPRINT_VERSION
    created_at_utc: str
    structure: HtmlStructureFingerprint
    technology: TechnologyFingerprint
    visual: VisualLayoutFingerprint
    composite_hash: str

def generate_unified_fingerprint(
    html: str,
    url: str,
    artifact_sha256: str,
    timestamp_utc: str
) -> UnifiedFingerprint:
    """Generate deterministic multi-dimensional fingerprint for a raw HTML artifact."""
    struct_fp = compute_structure_fingerprint(html)
    tech_fp = compute_technology_fingerprint(html, url)
    vis_fp = compute_visual_fingerprint(html)

    composite_repr = f"{FINGERPRINT_VERSION}:{struct_fp.structural_hash}:{tech_fp.technology_hash}:{vis_fp.visual_hash}"
    c_hash = hashlib.sha256(composite_repr.encode("utf-8")).hexdigest()[:24]

    fp_id = f"FP-{artifact_sha256[:12].upper()}"

    return UnifiedFingerprint(
        fingerprint_id=fp_id,
        artifact_sha256=artifact_sha256,
        url=url,
        fingerprint_version=FINGERPRINT_VERSION,
        created_at_utc=timestamp_utc,
        structure=struct_fp,
        technology=tech_fp,
        visual=vis_fp,
        composite_hash=c_hash
    )

def save_fingerprints(fingerprints: List[UnifiedFingerprint], output_file: Path) -> None:
    """Persist fingerprints to JSONL."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for fp in fingerprints:
            data = fp.model_dump()
            data["schema_version"] = "1.0.0"
            f.write(json.dumps(data) + "\n")
