"""
Matched-Pair Stratified Randomization Engine for Phase 1.9.
Ensures equal baseline density, balanced category representation, and pre-registered assignment.
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

from atlas.replication.models import (
    Phase19DomainRecord,
    BlockPairRecord,
    AssignmentRecord,
    Phase19ArmType,
    PathOrderStrategy
)

CATEGORY_QUOTAS = {
    "Universities": 40,
    "Government": 40,
    "Nonprofits": 30,
    "Long-running companies": 30,
    "Open-source/project sites": 30,
    "Personal/independent sites": 30
}

CATEGORY_PREFIXES = {
    "Universities": "UNI",
    "Government": "GOV",
    "Nonprofits": "NPO",
    "Long-running companies": "CORP",
    "Open-source/project sites": "OSS",
    "Personal/independent sites": "IND"
}

def build_phase1_9_sample(
    population_file: Path = Path("data/phase1_7/population_density.jsonl"),
    holdout_file: Path = Path("data/phase1_7/holdout_manifest.json"),
    output_dir: Path = Path("data/phase1_9"),
    seed: int = 4219
) -> Tuple[List[Phase19DomainRecord], List[BlockPairRecord], List[AssignmentRecord]]:
    """
    Construct density matched-pair randomized sample for Phase 1.9.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(population_file, "r", encoding="utf-8") as f:
        all_domains = [json.loads(l) for l in f if l.strip()]

    with open(holdout_file, "r", encoding="utf-8") as f:
        holdout_data = json.load(f)
        holdout_domains = set(holdout_data.get("domains", []))

    # Eligible pool (exclude holdout)
    eligible = [d for d in all_domains if d["domain"] not in holdout_domains]

    by_category = defaultdict(list)
    for d in eligible:
        by_category[d["category"]].append(d)

    rng = random.Random(seed)

    population_records: List[Phase19DomainRecord] = []
    block_records: List[BlockPairRecord] = []
    assignment_records: List[AssignmentRecord] = []

    for category, quota in CATEGORY_QUOTAS.items():
        candidates = by_category[category]
        # Sort by d_raw descending, breaking ties with domain name for perfect determinism
        candidates_sorted = sorted(candidates, key=lambda x: (x.get("d_raw", 0), x["domain"]), reverse=True)
        selected_for_cat = candidates_sorted[:quota]

        prefix = CATEGORY_PREFIXES.get(category, "CAT")
        num_pairs = quota // 2

        for i in range(num_pairs):
            d1_data = selected_for_cat[i * 2]
            d2_data = selected_for_cat[i * 2 + 1]

            d1 = Phase19DomainRecord(**d1_data)
            d2 = Phase19DomainRecord(**d2_data)

            block_id = f"{prefix}_{i:02d}"

            # Flip coin for treatment assignment
            coin = rng.random() < 0.5
            if coin:
                t_dom, c_dom = d1, d2
            else:
                t_dom, c_dom = d2, d1

            block = BlockPairRecord(
                block_id=block_id,
                category=category,
                treatment_domain=t_dom.domain,
                control_domain=c_dom.domain,
                treatment_d_raw=t_dom.d_raw,
                control_d_raw=c_dom.d_raw,
                d_raw_delta=abs(t_dom.d_raw - c_dom.d_raw),
                random_seed=seed
            )
            block_records.append(block)

            # Treatment Assignment
            assignment_records.append(AssignmentRecord(
                domain=t_dom.domain,
                category=category,
                block_id=block_id,
                arm=Phase19ArmType.TREATMENT,
                blinded_arm_label="COHORT_ALPHA",
                path_strategy=PathOrderStrategy.DENSITY_PRIORITIZED,
                fixed_slot_budget=10,
                d_raw=t_dom.d_raw,
                density_tier=t_dom.density_tier
            ))

            # Control Assignment
            assignment_records.append(AssignmentRecord(
                domain=c_dom.domain,
                category=category,
                block_id=block_id,
                arm=Phase19ArmType.CONTROL,
                blinded_arm_label="COHORT_BETA",
                path_strategy=PathOrderStrategy.NEUTRAL_RANDOM,
                fixed_slot_budget=10,
                d_raw=c_dom.d_raw,
                density_tier=c_dom.density_tier
            ))

            population_records.extend([t_dom, c_dom])

    # Write datasets
    with open(output_dir / "population.jsonl", "w", encoding="utf-8") as f:
        for p in population_records:
            f.write(p.model_dump_json() + "\n")

    with open(output_dir / "blocks.jsonl", "w", encoding="utf-8") as f:
        for b in block_records:
            f.write(b.model_dump_json() + "\n")

    with open(output_dir / "assignments.jsonl", "w", encoding="utf-8") as f:
        for a in assignment_records:
            f.write(a.model_dump_json() + "\n")

    return population_records, block_records, assignment_records

if __name__ == "__main__":
    pop, blocks, assignments = build_phase1_9_sample()
    print(f"[+] Sample built: {len(pop)} domains, {len(blocks)} matched pairs, {len(assignments)} assignments.")
