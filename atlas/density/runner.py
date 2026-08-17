"""
Equal-Budget Deep Archaeology Runner for Phase 1.7.
"""

import os
import json
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from atlas.density.models import StudyAssignmentRecord, ArmType
from atlas.deep.collector import fetch_and_extract_deep_evidence
from atlas.deep.discovery import discover_historical_paths_cdx, extract_links_from_html
from atlas.deep.prioritizer import rank_and_select_candidates
from atlas.deep.runner import score_deep_evidence_as_pilot
from atlas.deep.models import PairedDomainResult, PathCandidate

def process_single_study_domain(
    assignment: StudyAssignmentRecord,
    raw_artifacts_dir: Path,
    max_retrievals: int = 15,
    timeout: int = 5
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Any], Dict[str, int]]:
    """
    Execute equal-budget deep archaeology on an assigned study domain.
    """
    domain = assignment.domain
    category = assignment.category
    study_id = assignment.study_id
    stats = {"http_requests": 0, "bytes": 0, "archive_queries": 0}

    # 1. Root Inspection
    root_url = f"https://{domain}/"
    root_ev = fetch_and_extract_deep_evidence(
        study_id=study_id,
        domain=domain,
        target_url=root_url,
        path="/",
        raw_artifacts_dir=raw_artifacts_dir,
        timeout=timeout
    )
    stats["http_requests"] += 1
    stats["bytes"] += root_ev.html_bytes

    root_score, root_class, root_rules = score_deep_evidence_as_pilot(root_ev)

    root_entry = {
        "study_id": study_id,
        "domain": domain,
        "category": category,
        "arm": assignment.arm.value,
        "blinded_label": assignment.blinded_arm_label,
        "score": root_score,
        "classification": root_class,
        "triggered_rules": root_rules,
        "status_code": root_ev.live_status_code
    }

    # 2. Discover Historical & Live Paths
    cdx_candidates = discover_historical_paths_cdx(domain, timeout=timeout, limit=100)
    stats["archive_queries"] += 1

    # Check cached Phase 1.5 path candidates
    p15_path_file = Path("data/phase1_5/path_candidates.jsonl")
    cached_candidates = []
    if p15_path_file.exists():
        try:
            with open(p15_path_file, "r", encoding="utf-8") as f:
                for line in f:
                    if f'"{domain}"' in line:
                        p_rec = json.loads(line)
                        if p_rec.get("domain") == domain:
                            cached_candidates.append(PathCandidate(
                                domain=domain,
                                candidate_url=p_rec.get("candidate_url", f"https://{domain}{p_rec.get('path')}"),
                                path=p_rec.get("path", "/"),
                                path_category=p_rec.get("path_category", "general_directory"),
                                discovery_source=p_rec.get("discovery_source", "HISTORICAL_CACHE"),
                                first_observed_year=p_rec.get("first_observed_year"),
                                last_observed_year=p_rec.get("last_observed_year"),
                                capture_count=p_rec.get("capture_count", 1),
                                retrieval_priority=p_rec.get("retrieval_priority", 20.0)
                            ))
        except Exception:
            pass

    live_candidates = []
    if root_ev.raw_artifact_path and Path(root_ev.raw_artifact_path).exists():
        try:
            raw_html = Path(root_ev.raw_artifact_path).read_text(encoding="utf-8", errors="ignore")
            live_candidates = extract_links_from_html(raw_html, domain)
        except Exception:
            pass

    # Deduplicate
    all_cands_map = {}
    for c in cdx_candidates + cached_candidates + live_candidates:
        if c.path not in all_cands_map:
            all_cands_map[c.path] = c
    combined_candidates = list(all_cands_map.values())

    # Rank and select by retrieval priority (strictly capped at max_retrievals)
    selected = rank_and_select_candidates(combined_candidates, max_retrievals=max_retrievals)

    # 3. Targeted Retrieval & Deep Scoring
    deep_max_score = root_score
    deep_best_path = "/"
    deep_classification = root_class
    deep_rules = list(root_rules)
    best_candidate_rec = None

    candidates_log = []
    for cand in selected:
        deep_ev = fetch_and_extract_deep_evidence(
            study_id=study_id,
            domain=domain,
            target_url=cand.candidate_url,
            path=cand.path,
            candidate=cand,
            raw_artifacts_dir=raw_artifacts_dir,
            timeout=timeout
        )
        stats["http_requests"] += 1
        stats["bytes"] += deep_ev.html_bytes

        d_score, d_class, d_triggered = score_deep_evidence_as_pilot(deep_ev)

        cand_entry = {
            "study_id": study_id,
            "domain": domain,
            "category": category,
            "arm": assignment.arm.value,
            "path": cand.path,
            "score": d_score,
            "classification": d_class,
            "triggered_rules": d_triggered,
            "artifact_sha256": deep_ev.evidence_sha256,
            "raw_artifact": deep_ev.raw_artifact_path
        }
        candidates_log.append(cand_entry)

        if d_score > deep_max_score:
            deep_max_score = d_score
            deep_best_path = cand.path
            deep_classification = d_class
            deep_rules = d_triggered
            best_candidate_rec = cand

    is_inc_cand = (deep_max_score >= 40.0 and root_score < 40.0)
    is_val_disc = (deep_max_score >= 50.0 and root_score < 40.0 and ("Universities" in category or "Personal" in category or "Open-source" in category))
    is_inc_fp = (deep_max_score >= 40.0 and root_score < 40.0 and category == "Long-running companies")

    deep_entry = {
        "study_id": study_id,
        "domain": domain,
        "category": category,
        "arm": assignment.arm.value,
        "blinded_label": assignment.blinded_arm_label,
        "d_raw": assignment.d_raw,
        "density_tier": assignment.density_tier.value,
        "root_score": root_score,
        "root_classification": root_class,
        "root_triggered_rules": root_rules,
        "deep_candidates_found": len(combined_candidates),
        "deep_retrievals_attempted": len(selected),
        "deep_max_score": deep_max_score,
        "deep_best_path": deep_best_path,
        "deep_classification": deep_classification,
        "deep_triggered_rules": deep_rules,
        "is_incremental_candidate": is_inc_cand,
        "is_new_validated_discovery": is_val_disc,
        "is_incremental_false_positive": is_inc_fp
    }

    return root_entry, candidates_log, deep_entry, stats

def run_phase1_7_experiment(
    assignments: List[StudyAssignmentRecord],
    output_dir: Path = Path("data/phase1_7"),
    max_workers: int = 12,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Execute Phase 1.7 equal-budget controlled trial.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_artifacts_dir = output_dir / "evidence" / "raw_artifacts"
    raw_artifacts_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir = output_dir / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)

    if limit:
        assignments = assignments[:limit]

    print(f"[*] Executing Controlled Trial for {len(assignments)} assigned study domains ({max_workers} workers)...")
    start_time = time.time()

    all_root: List[Dict[str, Any]] = []
    all_deep_cands: List[Dict[str, Any]] = []
    all_deep_results: List[Dict[str, Any]] = []
    total_stats = {"http_requests": 0, "bytes": 0, "archive_queries": 0}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_assign = {
            executor.submit(process_single_study_domain, a, raw_artifacts_dir): a
            for a in assignments
        }

        completed = 0
        for future in as_completed(future_to_assign):
            completed += 1
            if completed % 25 == 0 or completed == len(assignments):
                print(f"    -> Processed {completed}/{len(assignments)} study domains...")
            try:
                r_entry, c_logs, d_entry, st = future.result()
                all_root.append(r_entry)
                all_deep_cands.extend(c_logs)
                all_deep_results.append(d_entry)
                total_stats["http_requests"] += st["http_requests"]
                total_stats["bytes"] += st["bytes"]
                total_stats["archive_queries"] += st["archive_queries"]
            except Exception as e:
                pass

    elapsed = time.time() - start_time
    print(f"[+] Controlled trial completed in {elapsed:.2f}s.")

    # Sort deterministically
    all_root.sort(key=lambda x: (x["arm"], x["category"], x["domain"]))
    all_deep_results.sort(key=lambda x: (x["arm"], x["category"], x["domain"]))

    # Write Master Datasets
    with open(output_dir / "root_results.jsonl", "w", encoding="utf-8") as f:
        for r in all_root:
            f.write(json.dumps(r) + "\n")

    with open(output_dir / "deep_candidates.jsonl", "w", encoding="utf-8") as f:
        for c in all_deep_cands:
            f.write(json.dumps(c) + "\n")

    with open(output_dir / "deep_results.jsonl", "w", encoding="utf-8") as f:
        for d in all_deep_results:
            f.write(json.dumps(d) + "\n")

    # Resource metrics ledger
    res_metrics = {
        "total_study_domains": len(assignments),
        "total_http_requests": total_stats["http_requests"],
        "total_bytes_downloaded": total_stats["bytes"],
        "total_archive_queries": total_stats["archive_queries"],
        "total_frozen_payloads": len(os.listdir(raw_artifacts_dir)),
        "total_runtime_seconds": round(elapsed, 2),
        "avg_requests_per_domain": round(total_stats["http_requests"] / max(len(assignments), 1), 2),
        "avg_bytes_per_request": round(total_stats["bytes"] / max(total_stats["http_requests"], 1), 2)
    }

    with open(output_dir / "resource_metrics.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(res_metrics) + "\n")

    return {
        "root_results": all_root,
        "deep_results": all_deep_results,
        "deep_candidates": all_deep_cands,
        "resource_metrics": res_metrics
    }
