"""Evidence freezing engine and cryptographic immutability manager for Phase 1."""

import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

from atlas.phase1.config import (
    PHASE1_DIR, PHASE1_RAW_EVIDENCE_DIR,
    PHASE1_FROZEN_DIR, SCORING_VERSION, SEED
)
from atlas.core.logger import logger

def freeze_collected_evidence() -> Path:
    """
    Freeze all raw collected evidence in experiments/0002/evidence/raw/,
    compute cryptographic SHA-256 manifests, and lock state to FROZEN.
    """
    logger.info("Freezing collected raw evidence for Phase 1 experiment...")
    freeze_timestamp = datetime.now(timezone.utc).isoformat()

    manifest = {
        "experiment_id": "0002",
        "phase": "Phase 1 Blind Seed-Corpus Discovery",
        "state": "FROZEN",
        "frozen_timestamp": freeze_timestamp,
        "sampling_seed": SEED,
        "scoring_version": SCORING_VERSION,
        "total_domains_frozen": 0,
        "total_artifacts_frozen": 0,
        "total_raw_bytes": 0,
        "domain_manifests": {}
    }

    if not PHASE1_RAW_EVIDENCE_DIR.exists():
        logger.warning(f"Raw evidence directory {PHASE1_RAW_EVIDENCE_DIR} does not exist.")
        return PHASE1_FROZEN_DIR / "frozen_manifest.json"

    for domain_dir in sorted(PHASE1_RAW_EVIDENCE_DIR.iterdir()):
        if domain_dir.is_dir():
            domain_slug = domain_dir.name
            domain_artifacts = []

            for f_path in sorted(domain_dir.iterdir()):
                if f_path.is_file():
                    with open(f_path, "rb") as af:
                        f_bytes = af.read()
                        f_sha = hashlib.sha256(f_bytes).hexdigest()
                        f_size = len(f_bytes)

                    manifest["total_raw_bytes"] += f_size
                    manifest["total_artifacts_frozen"] += 1
                    domain_artifacts.append({
                        "file_name": f_path.name,
                        "relative_path": f"evidence/raw/{domain_slug}/{f_path.name}",
                        "sha256": f_sha,
                        "size_bytes": f_size
                    })

            manifest["domain_manifests"][domain_slug] = {
                "artifacts_count": len(domain_artifacts),
                "artifacts": domain_artifacts
            }
            manifest["total_domains_frozen"] += 1

    frozen_manifest_path = PHASE1_FROZEN_DIR / "frozen_manifest.json"
    with open(frozen_manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    logger.info(f"Evidence frozen: {manifest['total_domains_frozen']} domains, {manifest['total_artifacts_frozen']} artifacts ({manifest['total_raw_bytes'] / (1024*1024):.2f} MB) locked in {frozen_manifest_path}")
    return frozen_manifest_path
