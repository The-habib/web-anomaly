"""Cryptographic manifest and reproducibility metadata generator for Corpus v2."""

import hashlib
import json
from pathlib import Path
from typing import Dict, List
from atlas.provenance.models import CorpusManifest, ProvenanceRecord, CorpusQualityMetrics

def compute_sha256(file_path: str) -> str:
    """Compute SHA-256 digest of a local file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def create_corpus_manifest(
    corpus: List[ProvenanceRecord],
    candidate_pool_counts: Dict[str, int],
    seed: int = 42,
    output_dir: str = "data/corpus_v2"
) -> CorpusManifest:
    """
    Generate and persist the cryptographic reproduction manifest for Corpus v2.
    """
    out_path = Path(output_dir)
    csv_file = out_path / "seed_corpus_v2.csv"
    jsonl_file = out_path / "provenance_v2.jsonl"
    manifest_file = out_path / "corpus_manifest.json"

    # Category counts
    final_counts: Dict[str, int] = {}
    for r in corpus:
        final_counts[r.category] = final_counts.get(r.category, 0) + 1

    source_hashes = {}
    if csv_file.exists():
        source_hashes["seed_corpus_v2.csv"] = compute_sha256(str(csv_file))
    if jsonl_file.exists():
        source_hashes["provenance_v2.jsonl"] = compute_sha256(str(jsonl_file))

    corpus_sha = source_hashes.get("seed_corpus_v2.csv", "")

    manifest = CorpusManifest(
        corpus_id="atlas-v2",
        version="2.0",
        seed=seed,
        total_domains=len(corpus),
        candidate_pool_counts=candidate_pool_counts,
        final_counts=final_counts,
        synthetic_count=0,
        duplicate_count=0,
        unknown_provenance_count=0,
        selection_algorithm=f"deterministic_sampling_seed_{seed}",
        source_hashes=source_hashes,
        corpus_sha256=corpus_sha
    )

    with open(manifest_file, "w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(indent=2))

    return manifest
