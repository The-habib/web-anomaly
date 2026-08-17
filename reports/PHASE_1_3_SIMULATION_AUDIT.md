# Project Atlas — Simulation Containment & Architecture Audit Report

**Document**: `reports/PHASE_1_3_SIMULATION_AUDIT.md`  
**Audit Objective**: Verify architectural separation of simulation fixtures from live empirical workflows  
**Date**: 2026-08-17T21:25:00Z  

---

## 1. Structural Isolation Verification

All simulation, mock, and fixture files have been strictly quarantined into `atlas/simulation/`:

```
atlas/simulation/
├── __init__.py       -> Exports test profiles for unit tests only
├── generator.py      -> Contains generate_synthetic_evidence_profile() with assert_no_simulation()
├── profiles.py       -> Contains KNOWN_TEST_PROFILES
└── fixtures.py       -> Synthetic timeline test cases
```

---

## 2. Automated Simulation Guard Testing

The runtime guard `assert_no_simulation()` was verified in `tests/test_live_mode_integrity.py`:
- When `mode == "LIVE"`, invoking `generate_synthetic_evidence_profile()` immediately raises `SimulationContaminationError: SECURITY GUARD VIOLATION in generate_synthetic_evidence_profile: Attempted to invoke simulation/synthetic fixture while experiment mode is set to LIVE!`.
- The CLI commands `atlas pilot run --mode LIVE` and `atlas benchmark run --mode LIVE` set global mode to `LIVE`, guaranteeing that any latent simulation call will abort execution.

---

## 3. Decontamination of Review & Scoring Modules

1. **`atlas/pilot/review.py`**: The hardcoded set `known_fossils = {"spacejam.com", ...}` was permanently deleted. Human reviewers evaluate dossiers based solely on extracted structural tags (`frameset_layout_detected`, `retro_styling_elements_present`, etc.) and archive span continuity.
2. **`atlas/scoring/scorer.py`**: Confirmed 100% domain-blind. Operates exclusively on extracted features and timeline event distributions.
