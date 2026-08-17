# Project Atlas — Execution Reconstruction & Timeline Audit Report

**Document**: `reports/PHASE_1_4_EXECUTION_RECONSTRUCTION.md`  
**Audit Objective**: Determine the exact mechanical cause of the contradiction between `BENCHMARK_V2_RESULTS.md` and `evaluation.json`  
**Date**: 2026-08-17T21:35:00Z  

---

## 1. Timeline of Execution Events

Through Git commit history and background task log inspection, the exact sequence of events was established:

1. **Event 1 (20:50:15 UTC)**: `python3 -m atlas.cli benchmark run --mode LIVE` executed in background task `task-887`.
   - Result: Active HTTP and Wayback CDX queries processed all 30 benchmark domains.
   - Output: `evaluation.json` was written with `TP=2/3, TN=17, FP=3, FN=8/7` (Accuracy: 63.33% - 66.67%).
   - Report: `reports/BENCHMARK_V2_RESULTS.md` was drafted based on these empirical results.
2. **Event 2 (21:25:14 UTC)**: `pytest -v tests/test_live_mode_integrity.py tests/test_pilot_and_benchmark.py` executed in background task `task-957`.
   - Inside `tests/test_pilot_and_benchmark.py`, `test_benchmark_v1_evaluation()` called `run_benchmark_v1_evaluation()`, which executed `run_benchmark_v2_evaluation(mode="SIMULATION")`.
   - Because `run_benchmark_v2_evaluation` defaulted to writing output to `data/benchmark_v2/evaluation.json` and `data/benchmark_v2/predictions.jsonl`, the simulation fallback generated default synthetic profiles (all scores = `0.0`, all predicted = `ORDINARY`).
   - The test run **silently overwrote the live dataset files with simulation all-zero outputs** (`TP=0, TN=20, FP=0, FN=10`).
3. **Event 3 (21:26:00 UTC)**: Git commit and push of branch `phase1_3` occurred, capturing the overwritten `evaluation.json` while `BENCHMARK_V2_RESULTS.md` retained the live metrics.

---

## 2. Root Cause Classification

$$\mathbf{ROOT\text{ }CAUSE: \text{ TEST SUITE DATASET POLLUTION / SIDE-EFFECT}}$$

### Contributing Factors:
1. **Lack of Test Directory Sandboxing**: Unit tests executed against production dataset paths rather than isolated `tmp_path` fixture folders.
2. **Shared Evaluator Endpoint**: The legacy `run_benchmark_v1_evaluation()` alias pointed to the Benchmark v2 evaluator without redirecting output paths.

---

## 3. Remediation & Permanent Safeguards

1. **Test Sandboxing**: `tests/test_pilot_and_benchmark.py` now explicitly passes `benchmark_dir = tmp_path / "test_benchmark"`, guaranteeing that unit tests can never mutate `data/benchmark_v2/`.
2. **Release Gate**: `atlas research release-check` validates that `predictions.jsonl`, `evaluation.json`, and `BENCHMARK_V2_RESULTS.md` match before granting scientific release approval.
