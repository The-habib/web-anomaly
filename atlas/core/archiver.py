"""
Evidence Archiver and Compression Engine for Project Atlas.
Provides high-efficiency zstandard / gzip archiving and on-demand extraction
of raw crawled HTML evidence payloads while preserving validated discovery artifacts.
"""

import os
import shutil
import tarfile
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

VALIDATED_DISCOVERY_PATTERNS = [
    "gnu.org_software_halifax",
    "tilde.club_tilde_cslug",
    "tilde.club_~cslug",
    "thunix.net_tilde_cslug",
    "thunix.net_~cslug",
    "spacejam",
    "zombo",
    "catb",
    "textfiles",
    "toastytech"
]

def is_preserved_discovery(file_name: str) -> bool:
    """Check if file is a validated discovery or reference artifact that must remain uncompressed."""
    fn_lower = file_name.lower()
    return any(pat.lower() in fn_lower for pat in VALIDATED_DISCOVERY_PATTERNS)

def bundle_evidence_directory(
    raw_artifacts_dir: Path,
    bundle_name: str = "raw_artifacts_bulk.tar.zst",
    preserve_discoveries: bool = True
) -> Tuple[bool, str]:
    """
    Compress non-discovery raw HTML files into a zstandard archive bundle.
    """
    if not raw_artifacts_dir.exists():
        return False, f"Directory {raw_artifacts_dir} does not exist."

    html_files = list(raw_artifacts_dir.glob("*.html"))
    if not html_files:
        return False, f"No HTML files found in {raw_artifacts_dir}."

    parent_evidence_dir = raw_artifacts_dir.parent
    bundle_path = parent_evidence_dir / bundle_name

    # Determine files to compress
    files_to_pack = []
    for hf in html_files:
        if preserve_discoveries and is_preserved_discovery(hf.name):
            continue
        files_to_pack.append(hf)

    if not files_to_pack:
        return False, "No bulk files to pack (all are preserved discoveries)."

    # Create tar.zst (or tar.gz if zstd not available)
    use_zstd = shutil.which("zstd") is not None
    tar_path = parent_evidence_dir / "temp_archive.tar"

    try:
        with tarfile.open(tar_path, "w") as tar:
            for f in files_to_pack:
                tar.add(f, arcname=f.name)

        if use_zstd:
            subprocess.run(
                ["zstd", "-q", "-19", "--rm", "-f", str(tar_path), "-o", str(bundle_path)],
                check=True
            )
        else:
            bundle_path = parent_evidence_dir / "raw_artifacts_bulk.tar.gz"
            subprocess.run(
                ["gzip", "-9", "-c", str(tar_path)],
                stdout=open(bundle_path, "wb"),
                check=True
            )
            if tar_path.exists():
                tar_path.unlink()

        # Remove packed files from disk
        removed_count = 0
        for f in files_to_pack:
            try:
                f.unlink()
                removed_count += 1
            except Exception:
                pass

        return True, f"Packed {removed_count} files into {bundle_path.name} ({bundle_path.stat().st_size // 1024} KB)."
    except Exception as e:
        if tar_path.exists():
            tar_path.unlink()
        return False, f"Error bundling evidence: {str(e)}"

def extract_evidence_bundle(bundle_path: Path, target_dir: Path) -> Tuple[bool, str]:
    """
    Extract a compressed evidence bundle back into the raw_artifacts directory.
    """
    if not bundle_path.exists():
        return False, f"Bundle {bundle_path} does not exist."

    target_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        if bundle_path.suffix == ".zst":
            tar_temp = bundle_path.parent / "temp_extracted.tar"
            subprocess.run(
                ["zstd", "-d", "-q", "-f", str(bundle_path), "-o", str(tar_temp)],
                check=True
            )
            with tarfile.open(tar_temp, "r") as tar:
                tar.extractall(path=target_dir)
            if tar_temp.exists():
                tar_temp.unlink()
        else:
            with tarfile.open(bundle_path, "r:*") as tar:
                tar.extractall(path=target_dir)

        return True, f"Successfully extracted {bundle_path.name} to {target_dir}."
    except Exception as e:
        return False, f"Error extracting bundle: {str(e)}"
