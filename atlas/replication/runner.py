"""
High-Performance Concurrent Archaeological Execution Engine for Phase 1.9.
Executes root inspection and fixed 10-slot retrieval across all 200 study domains
using a 20-worker thread pool and deterministic sorting.
"""

import json
import time
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from atlas.replication.models import (
    AssignmentRecord,
    RetrievalSlotRecord,
    Phase19ResultRecord,
    Phase19ArmType,
    SlotStatus
)
from atlas.deep.collector import fetch_and_extract_deep_evidence
from atlas.deep.runner import score_deep_evidence_as_pilot

def process_single_domain_replication(
    assignment: AssignmentRecord,
    dom_slots: List[RetrievalSlotRecord],
    raw_artifacts_dir: Path,
    timeout: int = 4
) -> Tuple[Dict[str, Any], Phase19ResultRecord, List[RetrievalSlotRecord], Dict[str, Any]]:
    """
    Process a single domain's root inspection and 10 retrieval slots in a worker thread.
    """
    dom = assignment.domain
    category = assignment.category
    arm = assignment.arm
    block_id = assignment.block_id
    blinded_label = assignment.blinded_arm_label
    study_id = f"p19_{block_id}_{dom}"

    stats = {
        "arm": arm.value,
        "requests_attempted": 0,
        "requests_successful": 0,
        "bytes": 0
    }

    # 1. Root Inspection
    root_url = f"https://{dom}/"
    root_ev = fetch_and_extract_deep_evidence(
        study_id=study_id,
        domain=dom,
        target_url=root_url,
        path="/",
        raw_artifacts_dir=raw_artifacts_dir,
        timeout=timeout
    )
    stats["requests_attempted"] += 1
    stats["bytes"] += root_ev.html_bytes
    if root_ev.live_status_code in (200, 301, 302):
        stats["requests_successful"] += 1

    root_score, root_class, root_rules = score_deep_evidence_as_pilot(root_ev)

    root_result = {
        "domain": dom,
        "category": category,
        "arm": arm.value,
        "blinded_arm_label": blinded_label,
        "block_id": block_id,
        "root_score": root_score,
        "root_classification": root_class,
        "root_rules": root_rules,
        "status_code": root_ev.live_status_code
    }

    # 2. 10-Slot Deep Retrieval Execution
    max_deep_score = root_score
    best_deep_path = "/"
    best_deep_class = root_class
    best_deep_rules = list(root_rules)
    slots_attempted = 0
    slots_successful = 0
    updated_slots = []

    for slot in dom_slots:
        if slot.status == SlotStatus.EMPTY_POOL_EXHAUSTED:
            updated_slots.append(slot)
            continue

        slots_attempted += 1
        stats["requests_attempted"] += 1

        slot_ev = fetch_and_extract_deep_evidence(
            study_id=study_id,
            domain=dom,
            target_url=slot.candidate_url,
            path=slot.path,
            raw_artifacts_dir=raw_artifacts_dir,
            timeout=timeout
        )
        stats["bytes"] += slot_ev.html_bytes

        s_score, s_class, s_rules = score_deep_evidence_as_pilot(slot_ev)

        slot.http_status = slot_ev.live_status_code
        slot.html_sha256 = slot_ev.evidence_sha256
        slot.artifact_path = slot_ev.raw_artifact_path
        slot.raw_anomaly_score = s_score
        slot.triggered_rules = s_rules

        if slot_ev.live_status_code in (200, 301, 302):
            slots_successful += 1
            stats["requests_successful"] += 1
            slot.status = SlotStatus.SUCCESS
        else:
            slot.status = SlotStatus.HTTP_ERROR

        updated_slots.append(slot)

        if s_score > max_deep_score:
            max_deep_score = s_score
            best_deep_path = slot.path
            best_deep_class = s_class
            best_deep_rules = s_rules

    is_cand = (max_deep_score >= 40.0 and root_score < 40.0)
    is_val = (max_deep_score >= 50.0 and root_score < 40.0 and category in ("Universities", "Open-source/project sites", "Personal/independent sites"))
    disc_url = f"https://{dom}{best_deep_path}" if is_cand else None
    active_slots_count = len([s for s in dom_slots if s.status != SlotStatus.EMPTY_POOL_EXHAUSTED])

    deep_result = Phase19ResultRecord(
        domain=dom,
        category=category,
        block_id=block_id,
        arm=arm,
        blinded_arm_label=blinded_label,
        d_raw=assignment.d_raw,
        root_score=root_score,
        root_classification=root_class,
        root_rules=root_rules,
        max_deep_score=max_deep_score,
        best_deep_path=best_deep_path,
        best_deep_classification=best_deep_class,
        best_deep_rules=best_deep_rules,
        slots_allocated=10,
        slots_attempted=slots_attempted,
        slots_successful=slots_successful,
        candidates_available=active_slots_count,
        is_full_exposure=(active_slots_count >= 10),
        is_candidate_discovery=is_cand,
        is_validated_discovery=is_val,
        discovery_url=disc_url
    )

    return root_result, deep_result, updated_slots, stats

def execute_phase1_9_replication(
    data_dir: Path = Path("data/phase1_9"),
    raw_artifacts_dir: Path = Path("data/phase1_9/evidence/raw_artifacts"),
    timeout: int = 4,
    max_workers: int = 20
) -> Tuple[List[Dict[str, Any]], List[Phase19ResultRecord], Dict[str, Any]]:
    """
    Execute fixed-budget replication across all 200 domains concurrently.
    """
    raw_artifacts_dir.mkdir(parents=True, exist_ok=True)

    with open(data_dir / "assignments.jsonl", "r", encoding="utf-8") as f:
        assignments = [AssignmentRecord(**json.loads(l)) for l in f if l.strip()]

    with open(data_dir / "retrieval_slots.jsonl", "r", encoding="utf-8") as f:
        all_slots = [RetrievalSlotRecord(**json.loads(l)) for l in f if l.strip()]

    slots_by_domain: Dict[str, List[RetrievalSlotRecord]] = {}
    for s in all_slots:
        if s.domain not in slots_by_domain:
            slots_by_domain[s.domain] = []
        slots_by_domain[s.domain].append(s)

    start_time = time.time()
    start_time_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    print(f"[*] Executing Phase 1.9 Controlled Replication on {len(assignments)} domains with {max_workers} concurrent workers...")

    root_results_list: List[Dict[str, Any]] = []
    deep_results_list: List[Phase19ResultRecord] = []
    all_updated_slots: List[RetrievalSlotRecord] = []

    treatment_attempted = 0
    treatment_successful = 0
    treatment_bytes = 0
    control_attempted = 0
    control_successful = 0
    control_bytes = 0
    total_http_requests = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_dom = {
            executor.submit(
                process_single_domain_replication,
                a,
                slots_by_domain.get(a.domain, []),
                raw_artifacts_dir,
                timeout
            ): a for a in assignments
        }

        completed = 0
        for future in as_completed(future_to_dom):
            completed += 1
            root_res, deep_res, slots_res, stats = future.result()
            root_results_list.append(root_res)
            deep_results_list.append(deep_res)
            all_updated_slots.extend(slots_res)

            total_http_requests += stats["requests_attempted"]
            if stats["arm"] == "TREATMENT":
                treatment_attempted += stats["requests_attempted"]
                treatment_successful += stats["requests_successful"]
                treatment_bytes += stats["bytes"]
            else:
                control_attempted += stats["requests_attempted"]
                control_successful += stats["requests_successful"]
                control_bytes += stats["bytes"]

            if completed % 40 == 0 or completed == len(assignments):
                print(f"    Progress: {completed}/{len(assignments)} domains processed ({completed*100//len(assignments)}%)...")

    elapsed = time.time() - start_time
    end_time_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Deterministic sorting on results
    root_results_list.sort(key=lambda x: (x["category"], x["block_id"], x["arm"], x["domain"]))
    deep_results_list.sort(key=lambda x: (x.category, x.block_id, x.arm.value, x.domain))
    all_updated_slots.sort(key=lambda x: (x.domain, x.slot_number))

    metrics = {
        "planned_slots_treatment": 1000,
        "planned_slots_control": 1000,
        "treatment_requests_attempted": treatment_attempted,
        "control_requests_attempted": control_attempted,
        "treatment_requests_successful": treatment_successful,
        "control_requests_successful": control_successful,
        "treatment_bytes": treatment_bytes,
        "control_bytes": control_bytes,
        "total_http_requests": total_http_requests,
        "elapsed_seconds": round(elapsed, 2),
        "start_time_utc": start_time_utc,
        "end_time_utc": end_time_utc
    }

    # Write output datasets
    with open(data_dir / "root_results.jsonl", "w", encoding="utf-8") as f:
        for r in root_results_list:
            f.write(json.dumps(r) + "\n")

    with open(data_dir / "deep_results.jsonl", "w", encoding="utf-8") as f:
        for d in deep_results_list:
            f.write(d.model_dump_json() + "\n")

    with open(data_dir / "retrieval_slots.jsonl", "w", encoding="utf-8") as f:
        for s in all_updated_slots:
            f.write(s.model_dump_json() + "\n")

    with open(data_dir / "resource_metrics.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(metrics) + "\n")

    print(f"[+] Replication complete in {elapsed:.2f}s: {len(deep_results_list)} domain results, {len(all_updated_slots)} slots.")
    return root_results_list, deep_results_list, metrics

if __name__ == "__main__":
    roots, deeps, m = execute_phase1_9_replication()
