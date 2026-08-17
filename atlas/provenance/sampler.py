"""Deterministic sampling engine for Project Atlas Corpus v2."""

import random
import csv
import json
from typing import Dict, List, Tuple
from pathlib import Path
from atlas.provenance.models import ProvenanceRecord

CATEGORY_QUOTAS = {
    "Universities": 200,
    "Government": 200,
    "Nonprofits": 150,
    "Long-running companies": 150,
    "Open-source/project sites": 150,
    "Personal/independent sites": 150
}

def sample_corpus_v2(
    validated_pools: Dict[str, List[ProvenanceRecord]],
    seed: int = 42
) -> List[ProvenanceRecord]:
    """
    Deterministically sample the production Corpus v2 dataset from validated candidate pools.
    Strictly forbids synthetic padding: if a pool is smaller than quota, keeps all verified items.
    """
    rng = random.Random(seed)
    final_corpus: List[ProvenanceRecord] = []

    for cat, quota in CATEGORY_QUOTAS.items():
        pool = validated_pools.get(cat, [])
        # Sort deterministically by domain before sampling to guarantee identical seed behavior across platforms
        sorted_pool = sorted(pool, key=lambda x: x.domain)
        if len(sorted_pool) <= quota:
            sampled = list(sorted_pool)
        else:
            sampled = rng.sample(sorted_pool, quota)
        final_corpus.extend(sampled)

    # Deterministic final order sorted by domain name for consistency
    final_corpus.sort(key=lambda x: x.domain)
    return final_corpus

def export_corpus_v2(
    corpus: List[ProvenanceRecord],
    output_dir: str = "data/corpus_v2"
) -> Tuple[str, str]:
    """
    Export Corpus v2 into CSV and JSONL formats.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    csv_file = out_path / "seed_corpus_v2.csv"
    jsonl_file = out_path / "provenance_v2.jsonl"
    cat_file = out_path / "category_index.json"

    # 1. Export CSV
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["domain", "seed_category", "canonical_url", "verification_status"])
        for rec in corpus:
            writer.writerow([
                rec.domain,
                rec.category,
                rec.canonical_url,
                rec.verification_status.value
            ])

    # 2. Export JSONL
    with open(jsonl_file, "w", encoding="utf-8") as f:
        for rec in corpus:
            f.write(rec.model_dump_json() + "\n")

    # 3. Export Category Index
    cat_index: Dict[str, List[str]] = {}
    for rec in corpus:
        cat_index.setdefault(rec.category, []).append(rec.domain)
    with open(cat_file, "w", encoding="utf-8") as f:
        json.dump(cat_index, f, indent=2)

    return str(csv_file), str(jsonl_file)
