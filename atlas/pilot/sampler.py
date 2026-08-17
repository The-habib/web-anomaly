"""Deterministic sampler for Phase 1.2 200-Domain Pilot."""

import csv
import json
import random
from pathlib import Path
from typing import List, Dict, Tuple
from atlas.pilot.config import PilotConfig
from atlas.pilot.models import PilotDomainRecord
from atlas.provenance.manifest import compute_sha256

def sample_pilot_corpus(config: PilotConfig = None) -> Tuple[List[PilotDomainRecord], Path, Path]:
    """
    Sample exactly 200 domains from Corpus v2 maintaining strict category quotas.
    Returns list of PilotDomainRecord, path to CSV, and path to Provenance JSONL.
    """
    if config is None:
        config = PilotConfig()

    corpus_csv = config.corpus_v2_path / "seed_corpus_v2.csv"
    provenance_file = config.corpus_v2_path / "provenance_v2.jsonl"

    if not corpus_csv.exists() or not provenance_file.exists():
        raise FileNotFoundError("Corpus v2 files not found. Please run build_corpus_v2() first.")

    # Read all provenance records
    records_by_cat: Dict[str, List[dict]] = {cat: [] for cat in config.category_quotas}
    with open(provenance_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            cat = rec.get("category")
            if cat in records_by_cat:
                records_by_cat[cat].append(rec)

    # Sort deterministically and sample with fixed seed
    rng = random.Random(config.seed)
    sampled_records: List[dict] = []

    for cat, quota in config.category_quotas.items():
        pool = sorted(records_by_cat[cat], key=lambda r: r["domain"])
        if len(pool) < quota:
            raise ValueError(f"Category '{cat}' has only {len(pool)} domains, requested quota is {quota}")
        sampled = rng.sample(pool, quota)
        sampled_records.extend(sampled)

    # Sort final pilot deterministically by category then domain
    sampled_records.sort(key=lambda r: (r["category"], r["domain"]))

    pilot_domain_records: List[PilotDomainRecord] = []
    out_dir = config.pilot_data_path
    out_dir.mkdir(parents=True, exist_ok=True)

    pilot_csv_path = out_dir / "pilot_domains.csv"
    pilot_prov_path = out_dir / "pilot_provenance.jsonl"

    with open(pilot_csv_path, "w", newline="", encoding="utf-8") as f_csv, \
         open(pilot_prov_path, "w", encoding="utf-8") as f_json:
        csv_writer = csv.writer(f_csv)
        csv_writer.writerow(["pilot_id", "domain", "category", "canonical_url", "source_type", "source_name", "source_reference"])

        for idx, rec in enumerate(sampled_records, 1):
            pilot_id = f"pilot-{idx:04d}"
            p_rec = PilotDomainRecord(
                pilot_id=pilot_id,
                domain=rec["domain"],
                category=rec["category"],
                canonical_url=rec["canonical_url"],
                source_type=rec["source_type"],
                source_name=rec["source_name"],
                source_reference=rec["source_reference"]
            )
            pilot_domain_records.append(p_rec)
            csv_writer.writerow([
                pilot_id,
                p_rec.domain,
                p_rec.category,
                p_rec.canonical_url,
                p_rec.source_type,
                p_rec.source_name,
                p_rec.source_reference
            ])
            f_json.write(p_rec.model_dump_json() + "\n")

    return pilot_domain_records, pilot_csv_path, pilot_prov_path
