"""
Candidate Pool Extraction and Preregistered Arm Path-Ordering Engine for Phase 1.9.
Builds identical candidate-path pools per domain, then applies:
  - Treatment: Density-informed path prioritization
  - Control: Neutral deterministic random path ordering (seed=999)
Allocates exactly 10 slots per domain (1000 Treatment vs 1000 Control).
"""

import json
import random
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

from atlas.replication.models import (
    CandidatePoolRecord,
    RetrievalSlotRecord,
    Phase19ArmType,
    SlotStatus,
    AssignmentRecord
)

USER_SPACE_PATTERNS = [
    r"/~[a-zA-Z0-9_-]+",
    r"/users?/[a-zA-Z0-9_-]+",
    r"/people/[a-zA-Z0-9_-]+",
    r"/personal/[a-zA-Z0-9_-]+",
    r"/faculty/[a-zA-Z0-9_-]+",
    r"/staff/[a-zA-Z0-9_-]+",
    r"/home/[a-zA-Z0-9_-]+"
]

LEGACY_EXTENSIONS = [".html", ".htm", ".shtml", ".txt", ".cgi", ".pl", ".php3", ".phtml"]

def compute_density_priority(path: str, capture_count: int = 1, first_year: int = 2000) -> float:
    """
    Compute frozen density-informed retrieval priority score for candidate path.
    """
    score = 10.0

    # User space bonus (+40)
    for pat in USER_SPACE_PATTERNS:
        if re.search(pat, path, re.IGNORECASE):
            score += 40.0
            break

    # Legacy extension bonus (+15)
    for ext in LEGACY_EXTENSIONS:
        if path.lower().endswith(ext):
            score += 15.0
            break

    # Age bonus (older paths get higher priority)
    if first_year < 2005:
        score += 20.0
    elif first_year < 2012:
        score += 10.0

    # Depth penalty (shallow paths preferred over deeply nested modern subdirectories)
    depth = path.strip("/").count("/")
    if depth > 4:
        score -= 10.0

    return max(1.0, score)

def build_phase1_9_candidate_pools(
    assignments_file: Path = Path("data/phase1_9/assignments.jsonl"),
    p15_candidates_file: Path = Path("data/phase1_5/path_candidates.jsonl"),
    p17_candidates_file: Path = Path("data/phase1_7/deep_candidates.jsonl"),
    output_dir: Path = Path("data/phase1_9"),
    control_seed: int = 999
) -> Tuple[List[CandidatePoolRecord], List[RetrievalSlotRecord]]:
    """
    Build candidate pools and 10-slot retrieval schedules for all 200 domains.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(assignments_file, "r", encoding="utf-8") as f:
        assignments = [AssignmentRecord(**json.loads(l)) for l in f if l.strip()]

    target_domains = {a.domain: a for a in assignments}

    # Load candidate paths from historical sources
    domain_paths_map: Dict[str, Dict[str, Dict]] = defaultdict(dict)

    if p15_candidates_file.exists():
        with open(p15_candidates_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                dom = rec.get("domain")
                if dom in target_domains:
                    p = rec.get("path", "/")
                    if p not in domain_paths_map[dom]:
                        domain_paths_map[dom][p] = {
                            "path": p,
                            "url": rec.get("candidate_url", f"https://{dom}{p}"),
                            "first_year": rec.get("first_observed_year", 2000),
                            "last_year": rec.get("last_observed_year", 2024),
                            "captures": rec.get("capture_count", 1)
                        }

    if p17_candidates_file.exists():
        with open(p17_candidates_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                dom = rec.get("domain")
                if dom in target_domains:
                    p = rec.get("path", "/")
                    if p not in domain_paths_map[dom]:
                        domain_paths_map[dom][p] = {
                            "path": p,
                            "url": rec.get("candidate_url", f"https://{dom}{p}"),
                            "first_year": rec.get("first_observed_year", 2000),
                            "last_year": rec.get("last_observed_year", 2024),
                            "captures": rec.get("capture_count", 1)
                        }

    pool_records: List[CandidatePoolRecord] = []
    slot_records: List[RetrievalSlotRecord] = []

    for a in assignments:
        dom = a.domain
        path_dict = domain_paths_map.get(dom, {})
        candidate_items = list(path_dict.values())

        pool_rec = CandidatePoolRecord(
            domain=dom,
            category=a.category,
            arm=a.arm,
            total_candidates_found=len(candidate_items),
            candidate_paths=[item["path"] for item in candidate_items],
            has_full_exposure=len(candidate_items) >= 10
        )
        pool_records.append(pool_rec)

        # Ordering strategy based on preregistered Arm
        if a.arm == Phase19ArmType.TREATMENT:
            # Density-informed ranking
            scored_candidates = []
            for item in candidate_items:
                p_score = compute_density_priority(
                    item["path"],
                    capture_count=item.get("captures", 1),
                    first_year=item.get("first_year", 2000)
                )
                scored_candidates.append((p_score, item["path"], item))
            # Sort by priority descending, then path ascending for determinism
            scored_candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
            ordered_items = [sc[2] for sc in scored_candidates]
        else:
            # Control: Neutral deterministic random shuffle
            # Seed combines global control seed + domain hash for independence across domains
            dom_seed = control_seed + (abs(hash(dom)) % 100000)
            c_rng = random.Random(dom_seed)
            shuffled_items = list(candidate_items)
            c_rng.shuffle(shuffled_items)
            ordered_items = shuffled_items

        # Allocate exactly 10 slots
        for slot_idx in range(1, 11):
            if slot_idx <= len(ordered_items):
                item = ordered_items[slot_idx - 1]
                p_score = compute_density_priority(item["path"], item.get("captures", 1), item.get("first_year", 2000))
                slot_records.append(RetrievalSlotRecord(
                    domain=dom,
                    slot_number=slot_idx,
                    arm=a.arm,
                    blinded_arm_label=a.blinded_arm_label,
                    candidate_url=item["url"],
                    path=item["path"],
                    path_priority=p_score if a.arm == Phase19ArmType.TREATMENT else 0.0,
                    path_order_rank=slot_idx,
                    status=SlotStatus.SUCCESS,
                    http_status=None,
                    html_sha256=None,
                    artifact_path=None
                ))
            else:
                # Slot exists in budget but pool is exhausted
                slot_records.append(RetrievalSlotRecord(
                    domain=dom,
                    slot_number=slot_idx,
                    arm=a.arm,
                    blinded_arm_label=a.blinded_arm_label,
                    candidate_url=f"https://{dom}/",
                    path="/",
                    path_priority=0.0,
                    path_order_rank=slot_idx,
                    status=SlotStatus.EMPTY_POOL_EXHAUSTED,
                    http_status=None,
                    html_sha256=None,
                    artifact_path=None
                ))

    with open(output_dir / "candidate_pools.jsonl", "w", encoding="utf-8") as f:
        for p in pool_records:
            f.write(p.model_dump_json() + "\n")

    with open(output_dir / "retrieval_slots.jsonl", "w", encoding="utf-8") as f:
        for s in slot_records:
            f.write(s.model_dump_json() + "\n")

    return pool_records, slot_records

if __name__ == "__main__":
    pools, slots = build_phase1_9_candidate_pools()
    print(f"[+] Candidate pools built: {len(pools)} domain pools, {len(slots)} retrieval slots allocated.")
