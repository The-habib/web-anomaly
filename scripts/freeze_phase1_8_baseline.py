"""
Script to perform cryptographic pre-execution baseline freeze for Phase 1.8.
Generates BASELINE_MANIFEST.json, GIT_STATE.json, ENVIRONMENT.json, CONFIG_HASHES.json in audit/phase1_8/.
"""

import sys
import os
import json
import hashlib
import subprocess
import platform
from pathlib import Path
from datetime import datetime, timezone

def get_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def freeze():
    base_dir = Path("/workspaces/web-anomaly")
    audit_dir = base_dir / "audit" / "phase1_8"
    audit_dir.mkdir(parents=True, exist_ok=True)

    now_utc = datetime.now(timezone.utc).isoformat()

    # 1. GIT STATE
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=base_dir).decode().strip()
    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=base_dir).decode().strip()
    git_status = subprocess.check_output(["git", "status", "--porcelain"], cwd=base_dir).decode().strip()
    
    git_state = {
        "phase": "1.8",
        "baseline_commit": "ded7fc0",
        "current_commit": commit,
        "current_branch": branch,
        "is_clean": len(git_status) == 0,
        "frozen_at": now_utc
    }
    with open(audit_dir / "GIT_STATE.json", "w", encoding="utf-8") as f:
        json.dump(git_state, f, indent=2)

    # 2. ENVIRONMENT
    try:
        import pytest
        pytest_ver = pytest.__version__
    except Exception:
        pytest_ver = "unknown"
    try:
        import numpy
        numpy_ver = numpy.__version__
    except Exception:
        numpy_ver = "unknown"

    env_data = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "pytest_version": pytest_ver,
        "numpy_version": numpy_ver,
        "frozen_at": now_utc
    }
    with open(audit_dir / "ENVIRONMENT.json", "w", encoding="utf-8") as f:
        json.dump(env_data, f, indent=2)

    # 3. CONFIG HASHES
    config_files = [
        "atlas/core/config.py",
        "atlas/scoring/engine.py",
        "atlas/scoring/rules.py",
        "atlas/density/models.py",
        "atlas/density/sampler.py",
        "atlas/density/statistics.py",
        "atlas/density/evaluator.py",
        "atlas/density/review.py"
    ]
    config_hashes = {
        "phase": "1.8",
        "frozen_at": now_utc,
        "hashes": {}
    }
    for cf in config_files:
        p = base_dir / cf
        if p.exists():
            config_hashes["hashes"][cf] = {
                "sha256": get_sha256(p),
                "size_bytes": p.stat().st_size
            }
    with open(audit_dir / "CONFIG_HASHES.json", "w", encoding="utf-8") as f:
        json.dump(config_hashes, f, indent=2)

    # 4. BASELINE MANIFEST
    manifest = {
        "phase": "1.8",
        "title": "Phase 1.8 Pre-Execution Baseline Artifact Manifest",
        "frozen_at": now_utc,
        "phase1_7_datasets": {},
        "reports": {},
        "code_modules": {}
    }

    # Data Phase 1.7
    data_p17 = base_dir / "data" / "phase1_7"
    for p in sorted(data_p17.glob("*.*")):
        if p.is_file():
            rel = str(p.relative_to(base_dir))
            manifest["phase1_7_datasets"][rel] = {
                "sha256": get_sha256(p),
                "size_bytes": p.stat().st_size
            }

    # Reports
    rep_dir = base_dir / "reports"
    for p in sorted(rep_dir.glob("*.md")):
        if p.is_file():
            rel = str(p.relative_to(base_dir))
            manifest["reports"][rel] = {
                "sha256": get_sha256(p),
                "size_bytes": p.stat().st_size
            }

    with open(audit_dir / "BASELINE_MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[+] Baseline frozen in {audit_dir}:")
    print(f"    Datasets tracked: {len(manifest['phase1_7_datasets'])}")
    print(f"    Reports tracked:  {len(manifest['reports'])}")
    print(f"    Config hashes:    {len(config_hashes['hashes'])}")

if __name__ == "__main__":
    freeze()
