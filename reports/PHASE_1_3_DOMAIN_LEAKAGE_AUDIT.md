# Project Atlas — Domain Leakage & Special-Casing Audit Report

**Document**: `reports/PHASE_1_3_DOMAIN_LEAKAGE_AUDIT.md`  
**Audit Objective**: Identify hardcoded domain names, domain reputations, or domain-specific scoring logic in the codebase  
**Date**: 2026-08-17T20:42:00Z  

---

## 1. Domain Leakage Audit Findings

A complete scan of `atlas/` identified two locations where domain names were explicitly inspected:

### Case 1: Generator Branching in `atlas/pilot/runner.py`
```python
# Lines 31-48:
if domain in ("spacejam.com", "toastytech.com", "zombo.com", "stallman.org", "catb.org", "sdf.org", "textfiles.com"):
    has_tables = True
    has_inline = True
    has_retro = True
    ...
```
- **Analysis**: Hardcoded domain names determined HTML features.
- **Remediation**: Relocated to `atlas/simulation/profiles.py` for test fixtures only; deleted from empirical path.

### Case 2: Review Verifier in `atlas/pilot/review.py`
```python
# Line 107:
known_fossils = {"spacejam.com", "toastytech.com", "zombo.com", "stallman.org", "catb.org", "sdf.org", "textfiles.com"}
if domain in known_fossils:
    blind_verdict = "REAL_ANOMALY"
```
- **Analysis**: Human review simulation evaluated domains by checking a known list rather than inspecting observed evidence.
- **Remediation**: Removed from empirical human review engine.

---

## 2. Core Rule Scorer Audit (`atlas/scoring/scorer.py`)

A rigorous inspection of `atlas/scoring/scorer.py` confirmed:
- **Zero Domain Leakage**: `AnomalyScorer` consumes only `timeline`, `metadata`, `html_content`, and `timeline_metrics`.
- **Domain Blindness**: `scorer.py` contains **no** `if domain == ...` statements, **no** domain whitelists/blacklists, and **no** reputation scoring.

The core scoring engine is cleanly decoupled and domain-blind.
