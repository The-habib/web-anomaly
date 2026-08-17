"""Batch execution orchestrator, checkpointing, and resumability manager for Phase 1."""

import os
import csv
import json
import time
import shutil
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional

from atlas.phase1.config import (
    CORPUS_CSV_PATH, PHASE1_DIR,
    PHASE1_CHECKPOINTS_DIR, PHASE1_RAW_EVIDENCE_DIR,
    PHASE1_SCAN_LOG, PHASE1_ERRORS_LOG,
    BATCH_SIZE, MAX_WORKERS, STORAGE_SAFETY_MARGIN_MB
)
from atlas.phase1.preflight import run_preflight_check
from atlas.phase1.collector import collect_domain_evidence
from atlas.core.logger import logger

def check_disk_safety() -> bool:
    """Ensure available disk space in Codespace exceeds safety threshold."""
    total, used, free = shutil.disk_usage(PHASE1_DIR)
    free_mb = free // (1024 * 1024)
    if free_mb < STORAGE_SAFETY_MARGIN_MB:
        logger.error(f"STORAGE SAFETY LIMIT REACHED: Only {free_mb}MB free (safety limit {STORAGE_SAFETY_MARGIN_MB}MB). Stopping.")
        return False
    return True

def load_corpus() -> List[Dict[str, str]]:
    """Load sampled domains from seed_corpus.csv."""
    if not CORPUS_CSV_PATH.exists():
        raise FileNotFoundError(f"Corpus file {CORPUS_CSV_PATH} not found. Run 'atlas phase1 corpus' first.")
    
    records = []
    with open(CORPUS_CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records

def get_completed_domains() -> set:
    """Scan existing checkpoints to find already completed domains."""
    completed = set()
    if not PHASE1_CHECKPOINTS_DIR.exists():
        return completed

    for ckpt_file in PHASE1_CHECKPOINTS_DIR.glob("batch-*.json"):
        try:
            with open(ckpt_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for d in data.get("completed_domains", []):
                    completed.add(d)
        except Exception:
            continue
    return completed

def process_single_domain(domain_record: Dict[str, str]) -> Dict[str, Any]:
    """Execute preflight and blind evidence collection for one domain."""
    domain = domain_record["domain"]
    try:
        preflight = run_preflight_check(domain)
        evidence = collect_domain_evidence(domain_record, preflight)
        return {
            "status": "SUCCESS",
            "domain": domain,
            "category": domain_record.get("category", "Unknown"),
            "preflight_status": preflight.get("status"),
            "evidence": evidence
        }
    except Exception as e:
        logger.error(f"Error processing domain {domain}: {e}")
        return {
            "status": "ERROR",
            "domain": domain,
            "category": domain_record.get("category", "Unknown"),
            "error": str(e)
        }

def run_phase1_scan(resume: bool = False, max_domains: Optional[int] = None) -> Dict[str, Any]:
    """
    Run or resume the Phase 1 blind evidence collection across the seed corpus.
    """
    corpus = load_corpus()
    if max_domains:
        corpus = corpus[:max_domains]

    completed_domains = get_completed_domains() if resume else set()
    pending_records = [r for r in corpus if r["domain"] not in completed_domains]

    total_corpus = len(corpus)
    logger.info(f"Starting Phase 1 Scan: {len(pending_records)} pending of {total_corpus} total domains (Resuming: {resume}).")

    if not check_disk_safety():
        return {"status": "ABORTED_STORAGE_LIMIT"}

    # Chunk pending into batches
    batches = [pending_records[i:i + BATCH_SIZE] for i in range(0, len(pending_records), BATCH_SIZE)]
    
    start_batch_idx = len(list(PHASE1_CHECKPOINTS_DIR.glob("batch-*.json"))) if resume else 0
    total_processed = len(completed_domains)

    for b_idx, batch in enumerate(batches, start=start_batch_idx + 1):
        if not check_disk_safety():
            break

        batch_name = f"batch-{b_idx:03d}"
        logger.info(f"Processing {batch_name} ({len(batch)} domains)... [Progress: {total_processed}/{total_corpus}]")
        batch_start = time.time()
        batch_results = []
        batch_completed = []

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_rec = {executor.submit(process_single_domain, rec): rec for rec in batch}
            for future in as_completed(future_to_rec):
                rec = future_to_rec[future]
                res = future.result()
                batch_results.append(res)
                batch_completed.append(rec["domain"])

                # Append to structured log
                with open(PHASE1_SCAN_LOG, "a", encoding="utf-8") as lf:
                    lf.write(json.dumps({
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "batch": batch_name,
                        "domain": res["domain"],
                        "status": res["status"],
                        "category": res.get("category"),
                        "preflight": res.get("preflight_status")
                    }) + "\n")

                if res["status"] == "ERROR":
                    with open(PHASE1_ERRORS_LOG, "a", encoding="utf-8") as ef:
                        ef.write(json.dumps(res) + "\n")

        total_processed += len(batch_completed)
        batch_duration = time.time() - batch_start

        # Save Checkpoint
        ckpt_file = PHASE1_CHECKPOINTS_DIR / f"{batch_name}.json"
        with open(ckpt_file, "w", encoding="utf-8") as f:
            json.dump({
                "batch_id": batch_name,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "duration_seconds": round(batch_duration, 2),
                "domains_count": len(batch_completed),
                "completed_domains": batch_completed
            }, f, indent=2)

        logger.info(f"Completed {batch_name} in {batch_duration:.1f}s. Checkpoint saved.")

    logger.info(f"Phase 1 scan stage completed. Total domains processed: {total_processed}/{total_corpus}.")
    return {
        "status": "COMPLETED",
        "total_processed": total_processed,
        "total_corpus": total_corpus
    }
