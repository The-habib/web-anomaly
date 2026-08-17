# Project Atlas — Comprehensive Simulation & Mock Inventory (Phase 1.3 Audit)

**Document**: `reports/PHASE_1_3_SIMULATION_INVENTORY.md`  
**Audit Scope**: Entire repository codebase (`atlas/`, `tests/`, `scripts/`)  
**Audit Objective**: Identify, classify, and isolate all synthetic evidence generators, mocks, fixtures, and profile synthesizers  
**Date**: 2026-08-17T20:42:00Z  

---

## 1. Inventory Summary Table

| Identifier | File Path | Function / Class | Category Classification | Empirical Risk | Recommended Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SIM-01` | `atlas/pilot/runner.py` | `_generate_realistic_domain_evidence()` | `PRODUCTION_EVIDENCE_PATH` (Deprecated) | **CRITICAL** | Relocate to `atlas/simulation/generator.py`; forbid in LIVE mode. |
| `SIM-02` | `atlas/pilot/benchmark_runner.py` | `run_benchmark_v1_evaluation()` mock call | `BENCHMARK_FIXTURE` | **HIGH** | Reclassify Benchmark v1 as synthetic fixture; replace with Benchmark v2 live evaluation. |
| `SIM-03` | `atlas/pilot/review.py` | `known_fossils` set in `record_human_review()` | `PRODUCTION_EVIDENCE_PATH` (Deprecated) | **CRITICAL** | Remove hardcoded domain set from empirical review path; evaluate solely on observed evidence. |
| `SIM-04` | `tests/test_negative_controls.py` | `mock_timeline` & `mock_html` fixtures | `TEST_ONLY` | **NONE (SAFE)** | Retain as unit test fixtures for scorer regression. |
| `SIM-05` | `tests/test_synthetic_fixtures.py` | Fixture Cases A–E | `TEST_ONLY` | **NONE (SAFE)** | Retain as unit test fixtures for rule validation. |
| `SIM-06` | `tests/test_scorer.py` | Mock timeline events | `TEST_ONLY` | **NONE (SAFE)** | Retain as unit test fixtures. |

---

## 2. Detailed Technical Breakdown of Discovered Mechanisms

### `SIM-01`: `_generate_realistic_domain_evidence(rec: PilotDomainRecord)`
- **File**: [`atlas/pilot/runner.py`](file:///workspaces/web-anomaly/atlas/pilot/runner.py#L15-L115)
- **Purpose**: Synthesizes HTML DOM properties (tables, framesets, frameworks) and CDX capture counts based on domain category and name rather than making live network requests.
- **Inputs**: `PilotDomainRecord` (domain, category).
- **Outputs**: `PilotEvidenceCapture` object.
- **Current Usage**: Invoked by Phase 1.2 `run_pilot_scan()`.
- **Domain-Specific Rules**: Explicit branching for `spacejam.com`, `stallman.org`, `toastytech.com`, `textfiles.com`, `danluu.com`, `idlewords.com`.
- **Classification**: **`PRODUCTION_EVIDENCE_PATH` (Severe Methodological Breach)**.
- **Remediation**: Move to `atlas/simulation/generator.py` for fixture use only. LIVE mode must strictly invoke `atlas.live.collector.fetch_live_evidence()`.

### `SIM-02`: Benchmark v1 Synthetic Mock Loop
- **File**: [`atlas/pilot/benchmark_runner.py`](file:///workspaces/web-anomaly/atlas/pilot/benchmark_runner.py#L60-L65)
- **Purpose**: Evaluates scoring against mock-generated evidence profiles instead of live artifacts.
- **Classification**: **`BENCHMARK_FIXTURE`**.
- **Remediation**: Retain Benchmark v1 as a synthetic test benchmark; construct Benchmark v2 consuming only live evidence.

### `SIM-03`: `known_fossils` Hardcoded Set in Review Engine
- **File**: [`atlas/pilot/review.py`](file:///workspaces/web-anomaly/atlas/pilot/review.py#L107-L116)
- **Purpose**: Bypassed blind review logic by checking `domain in known_fossils`.
- **Classification**: **`DOMAIN_LEAKAGE`**.
- **Remediation**: Strip domain-specific matching from review logic. Decisions must be made strictly on observed features.

---

## 3. Permitted vs Prohibited Classifications

Under the Phase 1.3 Scientific Framework:
1. **`TEST_ONLY`**: **PERMITTED** — Used exclusively in `tests/` for unit testing specific edge cases.
2. **`BENCHMARK_FIXTURE`**: **PERMITTED (ISOLATED)** — Used for offline scorer unit tests, but labeled explicitly as synthetic.
3. **`PRODUCTION_EVIDENCE_PATH`**: **STRICTLY PROHIBITED IN LIVE MODE** — Any empirical discovery pipeline accessing synthetic generation immediately triggers a `SimulationContaminationError`.
