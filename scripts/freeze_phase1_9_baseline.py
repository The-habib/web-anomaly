"""
Freeze Phase 1.9 replication baseline, environment, git state, and config digests.
"""

import os
import sys
import json
import hashlib
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    root = Path("/workspaces/web-anomaly")
    out_dir = root / "audit" / "phase1_9"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Environment
    env = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "os": platform.system(),
        "working_directory": str(root)
    }
    with open(out_dir / "ENVIRONMENT.json", "w", encoding="utf-8") as f:
        json.dump(env, f, indent=2)

    # 2. Git State
    git_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip()
    git_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root).decode().strip()
    git_status = subprocess.check_output(["git", "status", "--porcelain"], cwd=root).decode().strip()

    git_state = {
        "commit_hash": git_head,
        "branch": git_branch,
        "status": git_status,
        "baseline_phase": "Phase 1.8 Certified Baseline"
    }
    with open(out_dir / "GIT_STATE.json", "w", encoding="utf-8") as f:
        json.dump(git_state, f, indent=2)

    # 3. Config Hashes
    configs = [
        "atlas/config.py",
        "atlas/scorer.py",
        "atlas/rules.py",
        "atlas/pilot/scoring.py",
        "atlas/deep/runner.py",
        "atlas/density/models.py",
        "atlas/research/independent_stats.py"
    ]
    config_hashes = {}
    for c in configs:
        cp = root / c
        if cp.exists():
            config_hashes[c] = compute_sha256(cp)

    with open(out_dir / "CONFIG_HASHES.json", "w", encoding="utf-8") as f:
        json.dump(config_hashes, f, indent=2)

    # 4. Baseline Manifest
    manifest = {
        "phase": "1.9",
        "title": "Controlled Replication of Path-Density Prioritization",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "baseline_commit": git_head,
        "tracked_datasets": [
            "data/corpus_v2/provenance_v2.jsonl",
            "data/phase1_7/population_density.jsonl",
            "data/phase1_7/holdout_manifest.json",
            "audit/phase1_8/independent_statistical_results.json",
            "audit/phase1_8/release_gate.json"
        ],
        "dataset_hashes": {
            p: compute_sha256(root / p) for p in [
                "data/corpus_v2/provenance_v2.jsonl",
                "data/phase1_7/population_density.jsonl",
                "data/phase1_7/holdout_manifest.json",
                "audit/phase1_8/independent_statistical_results.json",
                "audit/phase1_8/release_gate.json"
            ] if (root / p).exists()
        }
    }
    with open(out_dir / "BASELINE_MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("[+] Phase 1.9 baseline frozen successfully in audit/phase1_9/.")

if __name__ == "__main__":
    main()
