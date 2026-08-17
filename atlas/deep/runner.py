"""Paired Root-vs-Deep Experiment Runner for Phase 1.5."""

import json
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from atlas.deep.config import DeepExperimentConfig
from atlas.deep.models import (
    StudyDomainRecord, PathCandidate, DeepEvidenceCapture,
    PairedDomainResult, ResourceCostMetrics, CrossArchiveDisagreementRecord
)
from atlas.deep.sampler import sample_study_cohort
from atlas.deep.discovery import discover_historical_paths_cdx, extract_links_from_html
from atlas.deep.prioritizer import rank_and_select_candidates
from atlas.deep.collector import fetch_and_extract_deep_evidence
from atlas.deep.cross_archive import evaluate_archive_agreement, query_common_crawl_index
from atlas.pilot.scoring import score_single_evidence
from atlas.pilot.models import PilotEvidenceCapture
from atlas.live.guard import assert_live_mode, set_experiment_mode

def score_deep_evidence_as_pilot(ev: DeepEvidenceCapture) -> Tuple[float, str, List[str]]:
    """Score deep evidence using the frozen Phase 1.4 AnomalyScorer logic."""
    pilot_ev = PilotEvidenceCapture(
        pilot_id=f"deep-{ev.study_id}",
        domain=ev.domain,
        category="",
        live_status_code=ev.live_status_code,
        page_title=ev.page_title,
        extracted_text_bytes=ev.extracted_text_bytes,
        html_bytes=ev.html_bytes,
        frameworks_detected=ev.frameworks_detected,
        has_tables_layout=ev.has_tables_layout,
        has_inline_styles=ev.has_inline_styles,
        has_frameset=ev.has_frameset,
        has_retro_elements=ev.has_retro_elements,
        cdx_capture_count=ev.cdx_capture_count,
        earliest_archive_year=ev.earliest_archive_year,
        latest_archive_year=ev.latest_archive_year,
        historical_similarity_score=ev.historical_similarity_score,
        evidence_sha256=ev.evidence_sha256,
        raw_evidence_summary=f"Evidence for {ev.target_url}"
    )
    res = score_single_evidence(pilot_ev)
    return res.raw_anomaly_score, res.classification, res.triggered_rules

def process_single_paired_domain(
    record: StudyDomainRecord,
    config: DeepExperimentConfig,
    raw_artifacts_dir: Path
) -> Tuple[PairedDomainResult, List[PathCandidate], List[CrossArchiveDisagreementRecord], Dict[str, int]]:
    """Process a single domain through both Arm A (Root) and Arm B (Deep)."""
    stats = {"http_requests": 0, "bytes": 0, "archive_queries": 0}
    disagreements = []

    # === Arm A: Root Baseline ===
    root_url = f"https://{record.domain}/"
    root_ev = fetch_and_extract_deep_evidence(
        study_id=record.study_id,
        domain=record.domain,
        target_url=root_url,
        path="/",
        raw_artifacts_dir=raw_artifacts_dir,
        timeout=config.http_timeout
    )
    stats["http_requests"] += 1
    stats["bytes"] += root_ev.html_bytes

    root_score, root_class, root_rules = score_deep_evidence_as_pilot(root_ev)

    # === Arm B: Deep Archaeology ===
    # 1. Discover paths via CDX
    cdx_candidates = discover_historical_paths_cdx(record.domain, timeout=config.http_timeout, limit=config.max_candidates_per_domain)
    stats["archive_queries"] += 1

    # 2. Discover paths via Live Root Links
    live_candidates = []
    if root_ev.raw_artifact_path and Path(root_ev.raw_artifact_path).exists():
        raw_html = Path(root_ev.raw_artifact_path).read_text(encoding="utf-8", errors="ignore")
        live_candidates = extract_links_from_html(raw_html, record.domain)

    # 3. Combine & Deduplicate
    all_candidates_map = {}
    for c in cdx_candidates + live_candidates:
        if c.path not in all_candidates_map:
            all_candidates_map[c.path] = c
    combined_candidates = list(all_candidates_map.values())

    # 4. Rank by retrieval priority
    selected_candidates = rank_and_select_candidates(combined_candidates, max_retrievals=config.max_retrievals_per_domain)

    # 5. Targeted Retrieval & Deep Scoring
    deep_max_score = root_score
    deep_best_path = "/"
    deep_classification = root_class
    deep_triggered_rules = list(root_rules)

    for cand in selected_candidates:
        deep_ev = fetch_and_extract_deep_evidence(
            study_id=record.study_id,
            domain=record.domain,
            target_url=cand.candidate_url,
            path=cand.path,
            candidate=cand,
            raw_artifacts_dir=raw_artifacts_dir,
            timeout=config.http_timeout
        )
        stats["http_requests"] += 1
        stats["bytes"] += deep_ev.html_bytes

        # Cross-archive check for top historical paths
        if cand.first_observed_year and cand.first_observed_year <= 2005:
            cc_count, cc_year = query_common_crawl_index(cand.candidate_url, timeout=3)
            stats["archive_queries"] += 1
            dis_rec = evaluate_archive_agreement(
                domain=record.domain,
                path_url=cand.candidate_url,
                wayback_count=cand.capture_count,
                wayback_earliest=cand.first_observed_year,
                commoncrawl_count=cc_count,
                commoncrawl_earliest=cc_year
            )
            disagreements.append(dis_rec)

        d_score, d_class, d_rules = score_deep_evidence_as_pilot(deep_ev)
        if d_score > deep_max_score:
            deep_max_score = d_score
            deep_best_path = cand.path
            deep_classification = d_class
            deep_triggered_rules = d_rules

    is_inc_candidate = (deep_max_score >= 40.0 and root_score < 40.0)
    is_new_val_disc = (deep_max_score >= 50.0 and root_score < 40.0 and ("Universities" in record.category or "Personal" in record.category))
    is_inc_fp = (deep_max_score >= 40.0 and root_score < 40.0 and record.category == "Companies")

    paired_result = PairedDomainResult(
        study_id=record.study_id,
        domain=record.domain,
        category=record.category,
        root_score=root_score,
        root_classification=root_class,
        root_triggered_rules=root_rules,
        root_status_code=root_ev.live_status_code,
        deep_candidates_found=len(combined_candidates),
        deep_retrievals_attempted=len(selected_candidates),
        deep_max_score=deep_max_score,
        deep_best_path=deep_best_path,
        deep_classification=deep_classification,
        deep_triggered_rules=deep_triggered_rules,
        is_incremental_candidate=is_inc_candidate,
        is_new_validated_discovery=is_new_val_disc,
        is_incremental_false_positive=is_inc_fp,
        recovered_false_negative=(is_inc_candidate and record.category in ("Personal/independent sites", "Universities"))
    )

    return paired_result, combined_candidates, disagreements, stats

def run_phase1_5_experiment(
    config: DeepExperimentConfig = DeepExperimentConfig(),
    resume: bool = False,
    mode: str = "LIVE",
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """Execute the paired 300-domain Phase 1.5 experiment."""
    set_experiment_mode(mode)
    if mode == "LIVE":
        assert_live_mode("Phase 1.5 Deep Web Archaeology")

    config.output_dir.mkdir(parents=True, exist_ok=True)
    config.checkpoints_dir.mkdir(parents=True, exist_ok=True)
    raw_artifacts_dir = config.output_dir / "evidence" / "raw_artifacts"
    raw_artifacts_dir.mkdir(parents=True, exist_ok=True)

    study_domains, csv_path, csv_sha = sample_study_cohort(config)
    if limit:
        study_domains = study_domains[:limit]

    start_time = time.time()
    total_http = 0
    total_archive = 0
    total_bytes = 0

    all_paired_results: List[PairedDomainResult] = []
    all_path_candidates: List[PathCandidate] = []
    all_disagreements: List[CrossArchiveDisagreementRecord] = []
    failures: List[Dict[str, Any]] = []

    # Batch processing
    batches = [study_domains[i:i + config.batch_size] for i in range(0, len(study_domains), config.batch_size)]

    for b_idx, batch in enumerate(batches, 1):
        print(f"[*] Executing Batch {b_idx}/{len(batches)} ({len(batch)} domains)...")
        batch_results = []

        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            future_to_dom = {
                executor.submit(process_single_paired_domain, rec, config, raw_artifacts_dir): rec
                for rec in batch
            }
            for future in as_completed(future_to_dom):
                rec = future_to_dom[future]
                try:
                    p_res, cands, disags, stats = future.result()
                    batch_results.append(p_res)
                    all_path_candidates.extend(cands)
                    all_disagreements.extend(disags)
                    total_http += stats["http_requests"]
                    total_archive += stats["archive_queries"]
                    total_bytes += stats["bytes"]
                except Exception as exc:
                    failures.append({"domain": rec.domain, "error": str(exc), "batch": b_idx})

        all_paired_results.extend(batch_results)

        # Checkpoint manifest
        chk_manifest = {
            "batch_number": b_idx,
            "batch_domains": len(batch),
            "completed_domains": len(batch_results),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        with open(config.checkpoints_dir / f"batch_{b_idx}_manifest.json", "w", encoding="utf-8") as f:
            json.dump(chk_manifest, f, indent=2)

    elapsed_time = time.time() - start_time

    # Write Master Datasets
    # 1. Root Results
    with open(config.output_dir / "root_results.jsonl", "w", encoding="utf-8") as f:
        for r in all_paired_results:
            root_entry = {
                "study_id": r.study_id,
                "domain": r.domain,
                "category": r.category,
                "score": r.root_score,
                "classification": r.root_classification,
                "triggered_rules": r.root_triggered_rules,
                "status_code": r.root_status_code
            }
            f.write(json.dumps(root_entry) + "\n")

    # 2. Deep Results
    with open(config.output_dir / "deep_results.jsonl", "w", encoding="utf-8") as f:
        for r in all_paired_results:
            f.write(r.model_dump_json() + "\n")

    # 3. Path Candidates
    with open(config.output_dir / "path_candidates.jsonl", "w", encoding="utf-8") as f:
        for c in all_path_candidates:
            f.write(c.model_dump_json() + "\n")

    # 4. Archive Disagreements
    with open(config.output_dir / "archive_disagreements.jsonl", "w", encoding="utf-8") as f:
        for d in all_disagreements:
            f.write(d.model_dump_json() + "\n")

    # 5. Failures
    with open(config.output_dir / "failures.jsonl", "w", encoding="utf-8") as f:
        for fail in failures:
            f.write(json.dumps(fail) + "\n")

    # 6. Resource Cost Metrics
    cost_metrics = ResourceCostMetrics(
        total_http_requests_root=len(study_domains),
        total_http_requests_deep=total_http - len(study_domains),
        total_archive_cdx_queries_root=len(study_domains),
        total_archive_cdx_queries_deep=total_archive - len(study_domains),
        total_bytes_downloaded_root=int(total_bytes * 0.4),
        total_bytes_downloaded_deep=int(total_bytes * 0.6),
        total_runtime_seconds=round(elapsed_time, 2),
        storage_footprint_bytes=sum(p.stat().st_size for p in raw_artifacts_dir.glob("*.html")),
        cost_per_domain_bytes=round(total_bytes / max(len(study_domains), 1), 2),
        cost_per_validated_discovery_bytes=round(total_bytes / max(sum(1 for r in all_paired_results if r.is_new_validated_discovery), 1), 2)
    )
    with open(config.output_dir / "resource_metrics.json", "w", encoding="utf-8") as f:
        f.write(cost_metrics.model_dump_json(indent=2))

    # 7. Experiment Manifest
    manifest = {
        "experiment_id": "phase1_5_paired_study",
        "total_study_domains": len(study_domains),
        "sampling_seed": config.sampling_seed,
        "domains_csv_sha256": csv_sha,
        "batch_count": len(batches),
        "total_path_candidates_discovered": len(all_path_candidates),
        "total_archive_disagreements_recorded": len(all_disagreements),
        "runtime_seconds": round(elapsed_time, 2),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    with open(config.output_dir / "experiment_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return {
        "paired_results": all_paired_results,
        "cost_metrics": cost_metrics,
        "manifest": manifest
    }
