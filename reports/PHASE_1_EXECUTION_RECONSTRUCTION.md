# Project Atlas — Phase 1 Execution Reconstruction Report

**Audit Phase**: `Phase 1.1 Independent Scientific Audit`  
**Baseline Git SHA**: `6db5827`  
**Audit Branch**: `audit/phase1_1`  
**Methodology**: Direct source-code execution trace and artifact state verification.

---

## 1. Executive Summary

This report documents the exact chronological and algorithmic execution path of Project Atlas Phase 1 reconstructed directly from implementation code (`atlas/phase1/`), configuration files, and persistent disk records. It explicitly describes what the system actually executed rather than high-level narrative summaries.

---

## 2. Full Architectural Execution Path

The Phase 1 pipeline executed sequentially across 9 distinct stages:

```
[1] Deterministic Corpus Generation (atlas.phase1.corpus)
      ↓ data/seed_corpus.csv (N=1,000)
[2] Batch Preflight Verification (atlas.phase1.preflight)
      ↓ DNS resolution + HTTP/HTTPS redirects + live availability
[3] Blind Evidence Collection (atlas.phase1.collector)
      ↓ Live HTML + Trafilatura text + CDX timeline → experiments/0002/evidence/raw/
[4] Checkpoint Management (atlas.phase1.scanner)
      ↓ experiments/0002/checkpoints/batch-001..022.json
[5] Cryptographic Evidence Freezing (atlas.phase1.freezer)
      ↓ experiments/0002/evidence/frozen/frozen_manifest.json (SHA-256 digests)
[6] Versioned Offline Scoring (atlas.phase1.scoring_runner)
      ↓ data/scan_results.jsonl, data/findings.jsonl, data/near_misses.jsonl
[7] Multi-Dimensional Candidate Ranking (atlas.phase1.ranking)
      ↓ reports/TOP_100_CANDIDATES.md, TOP_50_HIGH_CONFIDENCE.md, etc.
[8] Stratified Human Review Protocol (atlas.phase1.review)
      ↓ data/human_reviews.jsonl, reports/PHASE_1_FALSE_*.md
[9] Experimental Metrics & Publication Reports (atlas.phase1.metrics, report)
      ↓ data/phase1_metrics.json, data/phase1_manifest.json, reports/PHASE_1_RESULTS.md
```

---

## 3. Stage-by-Stage Implementation Specification

### Stage 1: Deterministic Corpus Generation
- **Source File**: `atlas/phase1/corpus.py` (`generate_seed_corpus`)
- **Input**: `CATEGORY_DISTRIBUTION` quotas, `CANDIDATE_POOLS`, `SEED = 42`.
- **Output**: `data/seed_corpus.csv` (1,000 domain rows), `reports/PHASE_1_CORPUS_AUDIT.md`.
- **Actual Behavior**:
  - The curated base lists for 5 of the 6 categories were smaller than their quotas (e.g. Government: 184 vs 200 quota; Nonprofits: 128 vs 150 quota; Companies: 132 vs 150 quota; Open-Source: 133 vs 150 quota; Personal: 124 vs 150 quota).
  - To reach exact quotas, the algorithm procedurally generated synthetic domain patterns (`univ-001.edu`, `dept-001.gov`, `foundation-001.org`, `corp-001.com`, `project-001.org`, `tilde-user-001.org`, `personal-site-001.net`).
  - Rows were sampled using `random.Random(42).sample()` and written to CSV.
- **Side Effects**: Injected synthetic placeholder domains into the seed dataset.

### Stage 2: Batch Preflight Verification
- **Source File**: `atlas/phase1/preflight.py` (`run_preflight_check`)
- **Input**: Domain string from `data/seed_corpus.csv`.
- **Output**: Preflight result dictionary (`status`: `SUCCESS`, `DNS_FAILURE`, `HTTP_FAILURE`, `TIMEOUT`, `CONNECTION_ERROR`).
- **Actual Behavior**:
  - Performed lightweight DNS resolution via `socket.getaddrinfo()`.
  - Executed streaming HTTP/HTTPS GET request with `DEFAULT_USER_AGENT` to detect landing URL, HTTP status code, response headers, and `/robots.txt` and `/sitemap.xml` presence.
- **Observed Result**: 671 / 1,000 domains succeeded; 329 domains failed preflight (principally synthetic and offline legacy domains).

### Stage 3: Blind Evidence Collection
- **Source File**: `atlas/phase1/collector.py` (`collect_domain_evidence`)
- **Input**: Domain record and preflight dictionary.
- **Output**: Raw evidence directory `experiments/0002/evidence/raw/<domain_slug>/`.
- **Artifacts Saved per Domain**:
  1. `rendered.html` (Raw response bytes decoded to UTF-8)
  2. `extracted_text.txt` (Clean text extracted via thread-safe Trafilatura/BeautifulSoup parser)
  3. `timeline.json` (Combined CDX timeline from Wayback Machine and Common Crawl)
  4. `raw_bundle.json` (Complete evidence dossier including preflight metadata)
- **Failure Handling**: Timeouts bounded at 5s per CDX query with polite fallback to empty list.

### Stage 4: Checkpointing & Resumability Orchestration
- **Source File**: `atlas/phase1/scanner.py` (`run_phase1_scan`, `get_completed_domains`)
- **Input**: Corpus records, `BATCH_SIZE = 50`, `MAX_WORKERS = 4`.
- **Output**: `experiments/0002/checkpoints/batch-001.json` through `batch-022.json`.
- **Actual Behavior**: Processed domains in chunks of 50 using `ThreadPoolExecutor`. Recorded completed domains into batch JSONs. When thread concurrency caused an early abort at batch-009, `atlas phase1 resume` successfully resumed from batch-009 without re-scanning batches 1–8.

### Stage 5: Cryptographic Evidence Freezing
- **Source File**: `atlas/phase1/freezer.py` (`freeze_collected_evidence`)
- **Input**: Directory `experiments/0002/evidence/raw/`.
- **Output**: `experiments/0002/evidence/frozen/frozen_manifest.json`.
- **Actual Behavior**: Iterated through all 1,000 domain subdirectories, computed SHA-256 digests of all 3,332 artifact files (121.99 MB total), and locked experiment state to `FROZEN`.

### Stage 6: Versioned Offline Scoring
- **Source File**: `atlas/phase1/scoring_runner.py` (`run_phase1_scoring`)
- **Input**: Frozen dossiers in `experiments/0002/evidence/raw/`, `atlas/config/scoring_rules.json`.
- **Output**: `data/scan_results.jsonl` (1,000 entries), `data/findings.jsonl` (3 entries), `data/near_misses.jsonl` (2 entries).
- **Actual Behavior**:
  - Computed SHA-256 hash of scoring rules (`a5b062c651...`).
  - Passed frozen artifacts to `AnomalyScorer.evaluate()`.
  - Discovered 3 candidate findings (Score $\ge 2$): `tilde.town` (Score 4), `tilde.club` (Score 4), `cmu.edu` (Score 2).

### Stage 7: Candidate Ranking Generation
- **Source File**: `atlas/phase1/ranking.py` (`generate_candidate_rankings`)
- **Input**: Scored JSONL datasets.
- **Output**: `reports/TOP_100_CANDIDATES.md`, `reports/TOP_50_HIGH_CONFIDENCE.md`, `reports/TOP_NEAR_MISSES.md`, `reports/ZERO_SCORE_SUMMARY.md`.

### Stage 8: Stratified Human Review Protocol
- **Source File**: `atlas/phase1/review.py` (`conduct_stratified_human_review`)
- **Input**: `data/scan_results.jsonl`, `SEED = 42 + 100`.
- **Output**: `data/human_reviews.jsonl` (23 entries), `reports/PHASE_1_FALSE_POSITIVES.md`, `reports/PHASE_1_FALSE_NEGATIVES.md`.
- **Root Cause of Sample Size (23 vs 50)**:
  - High score ($\ge 4$): 2 domains (`tilde.town`, `tilde.club`)
  - Med score ($2-3$): 1 domain (`cmu.edu`)
  - Near miss ($1$): 0 domains
  - Zero score ($0$): 10 domains sampled
  - Random remaining: 10 domains sampled
  - Total sampled: $2 + 1 + 0 + 10 + 10 = 23$ domains.
  - The function default signature `sample_size=50` and the report narrative contained hardcoded text mentioning 50 domains, causing a documented reporting discrepancy.

### Stage 9: Experimental Metrics & Publication Reports
- **Source File**: `atlas/phase1/metrics.py`, `atlas/phase1/report.py`
- **Output**: `data/phase1_metrics.json`, `data/phase1_manifest.json`, `reports/PHASE_1_RESULTS.md`, `reports/PHASE_1_LIMITATIONS.md`.

---

## 4. Key Takeaways from Execution Trace

1. **Blindness Maintained**: Live collection and CDX queries executed strictly before any anomaly scoring logic ran.
2. **Immutability Maintained**: Evidence was sealed with SHA-256 manifests prior to offline scoring.
3. **Identified Discrepancies**:
   - Synthetic placeholder domains were generated to meet arbitrary quotas.
   - The human review cohort evaluated 23 domains rather than 50 due to small candidate subpopulation sizes.
