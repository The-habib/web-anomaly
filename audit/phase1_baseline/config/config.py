"""Centralized configuration and parameters for Project Atlas Phase 1."""

import os
from pathlib import Path
from atlas.core.config import ROOT_DIR, DATA_DIR, EXPERIMENTS_DIR, LOGS_DIR, REPORTS_DIR

# Experiment Directory (Experiment 0002)
EXPERIMENT_ID = "0002"
PHASE1_DIR = EXPERIMENTS_DIR / EXPERIMENT_ID
PHASE1_DATA_DIR = DATA_DIR
PHASE1_REPORTS_DIR = REPORTS_DIR

PHASE1_EVIDENCE_DIR = PHASE1_DIR / "evidence"
PHASE1_RAW_EVIDENCE_DIR = PHASE1_EVIDENCE_DIR / "raw"
PHASE1_FROZEN_DIR = PHASE1_EVIDENCE_DIR / "frozen"
PHASE1_CHECKPOINTS_DIR = PHASE1_DIR / "checkpoints"

# Output Datasets
CORPUS_CSV_PATH = PHASE1_DATA_DIR / "seed_corpus.csv"
SCAN_RESULTS_JSONL = PHASE1_DATA_DIR / "scan_results.jsonl"
FINDINGS_JSONL = PHASE1_DATA_DIR / "findings.jsonl"
NEAR_MISSES_JSONL = PHASE1_DATA_DIR / "near_misses.jsonl"
HUMAN_REVIEWS_JSONL = PHASE1_DATA_DIR / "human_reviews.jsonl"
PHASE1_MANIFEST_PATH = PHASE1_DATA_DIR / "phase1_manifest.json"
PHASE1_METRICS_PATH = PHASE1_DATA_DIR / "phase1_metrics.json"

# Logging Paths
PHASE1_SCAN_LOG = LOGS_DIR / "phase1_scan.jsonl"
PHASE1_ERRORS_LOG = LOGS_DIR / "phase1_errors.jsonl"
PHASE1_REVIEWS_LOG = LOGS_DIR / "phase1_reviews.jsonl"

# Sampling Parameters
SEED = 42
TARGET_SAMPLE_SIZE = 1000
CATEGORY_DISTRIBUTION = {
    "Universities": 200,
    "Government": 200,
    "Nonprofits": 150,
    "Long-running companies": 150,
    "Open-source/project sites": 150,
    "Personal/independent sites": 150
}

# Network & Resource Budgets
BATCH_SIZE = 50
MAX_WORKERS = 4
PREFLIGHT_TIMEOUT = 5
FETCH_TIMEOUT = 8
ARCHIVE_TIMEOUT = 10
MAX_HISTORICAL_CAPTURES = 100
MAX_PAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
STORAGE_SAFETY_MARGIN_MB = 2048        # Stop if < 2GB available

# Scoring Version
SCORING_VERSION = "phase1-v1"

# Ensure directories exist
for d in [PHASE1_DIR, PHASE1_RAW_EVIDENCE_DIR, PHASE1_FROZEN_DIR, PHASE1_CHECKPOINTS_DIR, PHASE1_DATA_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)
