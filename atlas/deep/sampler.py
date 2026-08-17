"""Deterministic 300-Domain Study Sampler for Phase 1.5."""

import json
import random
import csv
from pathlib import Path
from typing import List, Tuple
from atlas.deep.config import DeepExperimentConfig
from atlas.deep.models import StudyDomainRecord
from atlas.provenance.manifest import compute_sha256

def sample_study_cohort(
    config: DeepExperimentConfig,
    corpus_v2_provenance_path: Path = Path("data/corpus_v2/provenance_v2.jsonl")
) -> Tuple[List[StudyDomainRecord], Path, str]:
    """
    Deterministically sample 300 domains from Corpus v2 according to category quotas.
    Returns (records, study_domains_csv_path, csv_sha256).
    """
    config.output_dir.mkdir(parents=True, exist_ok=True)
    domains_by_cat = {}

    with open(corpus_v2_provenance_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                cat = item["category"]
                domains_by_cat.setdefault(cat, []).append(item)

    rng = random.Random(config.sampling_seed)
    study_records = []
    global_idx = 1

    for cat, target_count in config.category_quotas.items():
        pool = domains_by_cat.get(cat, [])
        if len(pool) < target_count:
            raise ValueError(f"Not enough domains in category '{cat}': requested {target_count}, available {len(pool)}")

        # Sort deterministically before sampling
        sorted_pool = sorted(pool, key=lambda x: x["domain"])
        sampled = rng.sample(sorted_pool, target_count)
        # Sort sampled domains alphabetically
        sampled = sorted(sampled, key=lambda x: x["domain"])

        for item in sampled:
            study_records.append(StudyDomainRecord(
                study_id=f"study-{global_idx:04d}",
                domain=item["domain"],
                category=item["category"],
                canonical_url=item["canonical_url"],
                source_type=item["source_type"],
                source_name=item["source_name"],
                source_reference=item["source_reference"]
            ))
            global_idx += 1

    # Write study domains CSV
    out_csv = config.output_dir / "study_domains.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["study_id", "domain", "category", "canonical_url", "source_type", "source_name", "source_reference"])
        for r in study_records:
            writer.writerow([r.study_id, r.domain, r.category, r.canonical_url, r.source_type, r.source_name, r.source_reference])

    csv_sha = compute_sha256(out_csv)
    return study_records, out_csv, csv_sha
