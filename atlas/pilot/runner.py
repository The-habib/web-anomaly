"""Batch-based evidence capture and pilot scan orchestrator for Project Atlas.
Supports strict LIVE mode (real HTTP + Wayback queries) and isolated SIMULATION mode.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timezone

from atlas.pilot.config import PilotConfig
from atlas.pilot.models import (
    PilotDomainRecord, PilotEvidenceCapture, PilotBatchManifest, PilotManifest
)
from atlas.provenance.manifest import compute_sha256
from atlas.live.guard import assert_live_mode, set_experiment_mode
from atlas.live.models import LiveEvidenceRecord, ArchiveEvidenceRecord, EvidenceFailureRecord

def run_pilot_scan(
    pilot_records: List[PilotDomainRecord],
    config: Optional[PilotConfig] = None,
    resume: bool = False,
    mode: str = "LIVE",
    max_workers: int = 6
) -> Tuple[List[PilotEvidenceCapture], PilotManifest]:
    """
    Execute 200-domain pilot scan across 4 checkpointed batches.
    In 'LIVE' mode: queries live websites and historical archives directly.
    In 'SIMULATION' mode: uses isolated test fixtures.
    """
    if config is None:
        config = PilotConfig()

    set_experiment_mode(mode)
    if mode == "LIVE":
        assert_live_mode("Pilot Scan Execution")

    config.evidence_path.mkdir(parents=True, exist_ok=True)
    config.checkpoints_path.mkdir(parents=True, exist_ok=True)
    raw_artifacts_dir = config.evidence_path / "raw_artifacts"
    raw_artifacts_dir.mkdir(parents=True, exist_ok=True)

    all_evidence: List[PilotEvidenceCapture] = []
    live_records: List[LiveEvidenceRecord] = []
    archive_records: List[ArchiveEvidenceRecord] = []
    all_failures: List[EvidenceFailureRecord] = []
    batches_completed = 0

    num_batches = (len(pilot_records) + config.batch_size - 1) // config.batch_size

    for batch_idx in range(num_batches):
        batch_num = batch_idx + 1
        start_i = batch_idx * config.batch_size
        end_i = min(start_i + config.batch_size, len(pilot_records))
        batch_recs = pilot_records[start_i:end_i]

        batch_manifest_file = config.checkpoints_path / f"batch_{batch_num}_manifest.json"
        batch_evidence_file = config.evidence_path / f"evidence_batch_{batch_num}.jsonl"

        # Check if batch can be resumed from existing valid checkpoint
        if resume and batch_manifest_file.exists() and batch_evidence_file.exists():
            with open(batch_evidence_file, "r", encoding="utf-8") as f:
                batch_ev = [PilotEvidenceCapture.model_validate_json(line) for line in f if line.strip()]
            all_evidence.extend(batch_ev)
            batches_completed += 1
            continue

        batch_evidence: List[PilotEvidenceCapture] = []

        if mode == "LIVE":
            # Real empirical live collection
            from atlas.live.collector import collect_pilot_batch_live
            batch_results = collect_pilot_batch_live(
                batch_recs,
                raw_artifacts_dir=raw_artifacts_dir,
                max_workers=max_workers,
                timeout=8
            )
            for ev_cap, live_rec, arch_rec, fails in batch_results:
                batch_evidence.append(ev_cap)
                if live_rec:
                    live_records.append(live_rec)
                archive_records.append(arch_rec)
                all_failures.extend(fails)
        else:
            # Simulation / fixture mode for unit tests only
            from atlas.simulation.generator import generate_synthetic_evidence_profile
            for rec in batch_recs:
                ev = generate_synthetic_evidence_profile(rec)
                batch_evidence.append(ev)

        # Write batch evidence to disk
        with open(batch_evidence_file, "w", encoding="utf-8") as f:
            for ev in batch_evidence:
                f.write(ev.model_dump_json() + "\n")

        # Create batch manifest
        batch_sha = compute_sha256(batch_evidence_file)
        batch_manifest = PilotBatchManifest(
            batch_index=batch_num,
            batch_name=f"batch_{batch_num}",
            start_idx=start_i,
            end_idx=end_i,
            domain_count=len(batch_evidence),
            completed_at=datetime.now(timezone.utc).isoformat(),
            batch_evidence_sha256=batch_sha,
            domains=[r.domain for r in batch_recs]
        )
        with open(batch_manifest_file, "w", encoding="utf-8") as f:
            f.write(batch_manifest.model_dump_json(indent=2))

        all_evidence.extend(batch_evidence)
        batches_completed += 1

    # Write aggregated pilot evidence
    all_evidence_file = config.pilot_dir / "pilot_evidence.jsonl"
    with open(all_evidence_file, "w", encoding="utf-8") as f:
        for ev in all_evidence:
            f.write(ev.model_dump_json() + "\n")

    # Write live and archive specific evidence logs if in LIVE mode
    if mode == "LIVE":
        live_file = config.pilot_dir / "live_evidence.jsonl"
        with open(live_file, "w", encoding="utf-8") as f:
            for lr in live_records:
                f.write(lr.model_dump_json() + "\n")

        archive_file = config.pilot_dir / "archive_evidence.jsonl"
        with open(archive_file, "w", encoding="utf-8") as f:
            for ar in archive_records:
                f.write(ar.model_dump_json() + "\n")

        failures_file = config.pilot_dir / "failures.jsonl"
        with open(failures_file, "w", encoding="utf-8") as f:
            for fl in all_failures:
                f.write(fl.model_dump_json() + "\n")

    cat_counts = {}
    for r in pilot_records:
        cat_counts[r.category] = cat_counts.get(r.category, 0) + 1

    pilot_csv_file = config.pilot_dir / "pilot_domains.csv"
    pilot_prov_file = config.pilot_dir / "pilot_provenance.jsonl"

    csv_sha = compute_sha256(pilot_csv_file) if pilot_csv_file.exists() else ""
    prov_sha = compute_sha256(pilot_prov_file) if pilot_prov_file.exists() else ""
    ev_sha = compute_sha256(all_evidence_file)

    manifest = PilotManifest(
        experiment_id="phase1_3_live_pilot_200",
        created_at=datetime.now(timezone.utc).isoformat(),
        total_pilot_domains=len(all_evidence),
        batch_count=batches_completed,
        batch_size=config.batch_size,
        category_distribution=cat_counts,
        csv_sha256=csv_sha,
        provenance_sha256=prov_sha,
        evidence_sha256=ev_sha,
        scoring_sha256=""
    )

    manifest_file = config.pilot_dir / "pilot_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(indent=2))

    return all_evidence, manifest
