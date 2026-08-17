"""
Sampling, Density Tier Derivation & Category-Matched Arm Assignment for Phase 1.7.
"""

import json
import random
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple, Any

from atlas.density.models import (
    PopulationDensityRecord,
    DensityTier,
    StudyAssignmentRecord,
    ArmType
)

def compute_density_percentiles(density_records: List[PopulationDensityRecord]) -> Dict[str, Any]:
    """Compute overall and category-specific distribution percentiles."""
    raw_vals = [r.d_raw for r in density_records]
    if not raw_vals:
        return {}

    overall_stats = {
        "count": len(raw_vals),
        "min": int(np.min(raw_vals)),
        "max": int(np.max(raw_vals)),
        "mean": round(float(np.mean(raw_vals)), 2),
        "median": float(np.median(raw_vals)),
        "p75": float(np.percentile(raw_vals, 75)),
        "p90": float(np.percentile(raw_vals, 90)),
        "p95": float(np.percentile(raw_vals, 95)),
        "p99": float(np.percentile(raw_vals, 99))
    }

    category_stats = {}
    by_cat = defaultdict(list)
    for r in density_records:
        by_cat[r.category].append(r.d_raw)

    for cat, vals in by_cat.items():
        category_stats[cat] = {
            "count": len(vals),
            "mean": round(float(np.mean(vals)), 2),
            "median": float(np.median(vals)),
            "p75": float(np.percentile(vals, 75)),
            "p95": float(np.percentile(vals, 95))
        }

    return {"overall": overall_stats, "by_category": category_stats}

def assign_density_tiers_and_sample_arms(
    density_records: List[PopulationDensityRecord],
    output_dir: Path = Path("data/phase1_7"),
    seed: int = 42,
    holdout_size: int = 200,
    arm_size: int = 100
) -> Tuple[List[StudyAssignmentRecord], Dict[str, Any]]:
    """
    Derive empirical density tiers, reserve unseen holdout set, and sample category-matched arms.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    # 1. Percentiles & Tier Cutoffs
    stats = compute_density_percentiles(density_records)
    p50 = stats["overall"]["median"]
    p75 = stats["overall"]["p75"]
    p95 = stats["overall"]["p95"]

    # Assign tiers to all records
    for r in density_records:
        if r.d_raw >= p95:
            r.density_tier = DensityTier.EXTREME
        elif r.d_raw >= p75:
            r.density_tier = DensityTier.HIGH
        elif r.d_raw >= p50:
            r.density_tier = DensityTier.MEDIUM
        else:
            r.density_tier = DensityTier.LOW

    # Write density tiers
    with open(output_dir / "density_tiers.jsonl", "w", encoding="utf-8") as f:
        for r in density_records:
            entry = {
                "domain": r.domain,
                "category": r.category,
                "d_raw": r.d_raw,
                "density_tier": r.density_tier.value,
                "d_user": r.d_user,
                "d_legacy": r.d_legacy,
                "d_diversity": r.d_diversity
            }
            f.write(json.dumps(entry) + "\n")

    # 2. Holdout Reservation (N=200) Stratified by Category
    by_category = defaultdict(list)
    for r in density_records:
        by_category[r.category].append(r)

    holdout_domains = []
    eligible_pool = []

    holdout_quota_per_cat = {
        "Universities": 40,
        "Government": 40,
        "Nonprofits": 30,
        "Long-running companies": 30,
        "Open-source/project sites": 30,
        "Personal/independent sites": 30
    }

    for cat, records in by_category.items():
        shuffled = list(records)
        rng.shuffle(shuffled)
        quota = holdout_quota_per_cat.get(cat, int(len(records) * (holdout_size / len(density_records))))
        holdout_domains.extend(shuffled[:quota])
        eligible_pool.extend(shuffled[quota:])

    holdout_manifest = {
        "holdout_seed": seed,
        "total_holdout_domains": len(holdout_domains),
        "category_distribution": dict(Counter(r.category for r in holdout_domains)),
        "domains": [r.domain for r in sorted(holdout_domains, key=lambda x: x.domain)]
    }
    with open(output_dir / "holdout_manifest.json", "w", encoding="utf-8") as f:
        json.dump(holdout_manifest, f, indent=2)

    # 3. Sample Arm U (Uniform) & Arm D (Density Prioritized) from Eligible Pool (N=800)
    eligible_by_cat = defaultdict(list)
    for r in eligible_pool:
        eligible_by_cat[r.category].append(r)

    arm_quota_per_cat = {
        "Universities": 20,
        "Government": 20,
        "Nonprofits": 15,
        "Long-running companies": 15,
        "Open-source/project sites": 15,
        "Personal/independent sites": 15
    }

    arm_u_records: List[PopulationDensityRecord] = []
    arm_d_records: List[PopulationDensityRecord] = []

    for cat, records in eligible_by_cat.items():
        quota = arm_quota_per_cat.get(cat, 15)
        # Arm D: Sort by d_raw descending (upper tail)
        sorted_by_density = sorted(records, key=lambda x: x.d_raw, reverse=True)
        selected_d = sorted_by_density[:quota]
        arm_d_records.extend(selected_d)

        # Arm U: Draw uniformly from remainder
        remaining = [r for r in records if r not in selected_d]
        rng.shuffle(remaining)
        selected_u = remaining[:quota]
        arm_u_records.extend(selected_u)

    # 4. Blinded Assignment: Randomly assign STUDY_A and STUDY_B
    flip = rng.choice([True, False])
    label_u = "STUDY_A" if flip else "STUDY_B"
    label_d = "STUDY_B" if flip else "STUDY_A"

    assignments: List[StudyAssignmentRecord] = []
    for idx, r in enumerate(arm_u_records, 1):
        assignments.append(StudyAssignmentRecord(
            study_id=f"arm-u-{idx:04d}",
            domain=r.domain,
            category=r.category,
            arm=ArmType.UNIFORM,
            blinded_arm_label=label_u,
            d_raw=r.d_raw,
            density_tier=r.density_tier,
            is_holdout=False
        ))

    for idx, r in enumerate(arm_d_records, 1):
        assignments.append(StudyAssignmentRecord(
            study_id=f"arm-d-{idx:04d}",
            domain=r.domain,
            category=r.category,
            arm=ArmType.DENSITY_PRIORITIZED,
            blinded_arm_label=label_d,
            d_raw=r.d_raw,
            density_tier=r.density_tier,
            is_holdout=False
        ))

    # Deterministic sort
    assignments.sort(key=lambda x: (x.arm.value, x.category, x.domain))

    with open(output_dir / "study_assignment.jsonl", "w", encoding="utf-8") as f:
        for a in assignments:
            f.write(a.model_dump_json() + "\n")

    metadata = {
        "stats": stats,
        "holdout_count": len(holdout_domains),
        "eligible_pool_count": len(eligible_pool),
        "arm_u_count": len(arm_u_records),
        "arm_d_count": len(arm_d_records),
        "blinded_mapping": {"UNIFORM": label_u, "DENSITY_PRIORITIZED": label_d}
    }

    return assignments, metadata
