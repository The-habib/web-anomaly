# Project Atlas — Historical Review Systems Audit (Phases 0.5 – 1.9.1)

## 1. Longitudinal Review Architecture Audit

| Phase | Subsystem File | Review Method | Classification | Description & Provenance |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0.5** | `tests/test_synthetic_fixtures.py` | Unit test assertions | **`SAFE_TEST_FIXTURE`** | Controlled synthetic test fixtures for timeline scoring algorithms. |
| **Phase 1.0** | `atlas/phase1/review.py` | Heuristic score verification | **`MACHINE_REVIEW`** | Algorithmic ranking and candidate threshold filtering. |
| **Phase 1.1** | `atlas/audit/` | Deterministic replay audit | **`SAFE_AUDIT`** | Deterministic replay and audit verification. |
| **Phase 1.2** | `atlas/provenance/builder.py` | Provenance seed tags | **`BENCHMARK_ONLY`** | Corpus v2 provenance tracking on known reference sites. |
| **Phase 1.3** | `atlas/pilot/review.py` | Heuristic structural simulation | **`SIMULATION`** | Pilot study evaluating structural heuristics (`has_frameset`, etc.) as simulated expert. |
| **Phase 1.4** | `atlas/research/release_gate.py`| Automated release check | **`BENCHMARK_ONLY`** | Mathematical verification of benchmark metrics. |
| **Phase 1.5** | `atlas/deep/review.py` | Model-dependent verdict simulation | **`SIMULATION`** | Programmatically assigned verdicts by inspecting `is_new_validated_discovery`. |
| **Phase 1.6** | `atlas/deep/evaluator.py` | Incremental candidate audit | **`SAFE_AUDIT`** | Reconciled root vs deep candidate discoveries. |
| **Phase 1.7** | `atlas/density/review.py` | Score-thresholded verdict assigner | **`SIMULATION`** | Assigned `CLEAR_ANOMALY` if `score >= 50.0 and is_incremental_candidate`. |
| **Phase 1.8** | `atlas/research/audit_phase1_8.py`| Experimental design audit | **`SAFE_AUDIT`** | Identified Arm D selection bias and budget disparities. |
| **Phase 1.9** | `atlas/replication/review.py` | Hardcoded domain conditional checks | **`EMPIRICAL_CONTAMINATION`** | Programmatically evaluated `gwern.net` and `uspto.gov` to assign `CLEAR_ANOMALY`. |
| **Phase 1.9.1**| `atlas/replication/review.py` | Decoupled blind packet export | **`REAL_HUMAN_REVIEW_PROTOCOL`** | Strips all scores, arms, and ranks; exports packets; marks status as `HUMAN_REVIEW_PENDING`. |

---

## 2. Key Historical Takeaway
Across Phases 1.3 through 1.9, the codebase frequently labeled automated heuristic classifiers as "human reviews" in output filenames (`human_reviews.jsonl`). While useful as exploratory heuristic classifiers, they did not involve real human operators.

In Phase 1.9.1, Project Atlas establishes an immutable boundary: **machine code may generate review packets and record imported human decisions, but may never synthesize or simulate human judgment.**
