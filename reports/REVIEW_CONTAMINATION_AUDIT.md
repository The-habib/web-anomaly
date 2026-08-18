# Project Atlas — Review Contamination Audit (Phase 1.9.1)

## 1. Executive Summary & Audit Mandate
A comprehensive forensic inspection was performed across all historical review implementations in Project Atlas (Phases 0.5 through 1.9). The objective was to identify any mechanisms where automated scripts or domain-specific logic generated "human" verdicts programmatically, bypassing independent human judgment.

---

## 2. Inventory of Identified Contamination Mechanisms

| Component / File | Function / Line | Condition / Pattern | Category | Empirical Impact | Disposition |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `atlas/replication/review.py` | `conduct_phase1_9_blind_review` (L60-85) | `if d.domain == "gwern.net"` / `if d.domain == "uspto.gov"` | **`EMPIRICAL_CONTAMINATION`** | Directly assigned `CLEAR_ANOMALY` and promoted discoveries | **DECONTAMINATE / REMOVE** |
| `atlas/density/review.py` | `generate_and_record_phase1_7_reviews` (L52-78) | `if score >= 50.0 and is_incremental_candidate: verdict = "CLEAR_ANOMALY"` | **`EMPIRICAL_CONTAMINATION`** | Programmatic simulation of human verdicts based on model scores | **ISOLATE AS SIMULATION** |
| `atlas/deep/review.py` | `record_paired_human_reviews` (L73-88) | `if p_res.get("is_new_validated_discovery"): deep_v = "CLEAR_ANOMALY"` | **`EMPIRICAL_CONTAMINATION`** | Programmatic simulation of expert reviewer | **ISOLATE AS SIMULATION** |
| `atlas/pilot/review.py` | `record_human_review` (L118-134) | Heuristics on structural features (`has_frameset`, etc.) | **`SIMULATION`** | Pilot study simulated evaluation | **MAINTAIN AS PILOT SIMULATION** |
| `atlas/provenance/builder.py` | `PROVENANCE_SEEDS` | Hardcoded seed categories & types | **`BENCHMARK_ONLY`** | Corpus v2 provenance tracking | **SAFE BENCHMARK METADATA** |
| `tests/fixtures/` | Unit test assertions | Expected test outputs | **`SAFE_TEST_FIXTURE`** | Test suite verification | **SAFE TEST FIXTURE** |

---

## 3. Classification Definitions
- **`SAFE_TEST_FIXTURE`**: Static fixtures used solely in `tests/` to verify software correctness.
- **`SIMULATION`**: Explicitly labeled research simulations where human behavior is modeled heuristically.
- **`BENCHMARK_ONLY`**: Ground-truth labels used for calibrating automated classifiers against known reference sites.
- **`EMPIRICAL_CONTAMINATION`**: Code in the empirical research pipeline that assigns "human" verdicts or validates real discoveries programmatically without an actual human reviewer.

---

## 4. Required Remediation Actions
1. Remove all domain-specific branches (`if d.domain == ...`) from `atlas/replication/review.py`.
2. Decouple review packet export from verdict recording.
3. Establish a strict Discovery State Machine: no candidate can transition to `VALIDATED` without a verified `HumanReviewSubmission` record.
4. When no human reviewer is present in the runtime environment, candidates must be classified as `HUMAN_REVIEW_PENDING`.
