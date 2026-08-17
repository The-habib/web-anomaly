# Phase 1.5 Methodology Report — Experimental Design & Integrity Protocols

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.5  
**Date**: 2026-08-17T22:30:00Z  

---

## 1. Primary Research Objective

Phase 1.5 tests whether expanding Atlas from canonical root-only inspection to passive historical index exploration (`Wayback CDX` and `Common Crawl`) recovers genuine historical web anomalies that root landing pages obscure.

---

## 2. Experimental Principles & Controls

### Principle 1: Paired Control Cohort
All 300 domains are evaluated simultaneously across two observation tracks:
- **Arm A (Root Baseline)**: Evaluates root URL (`/`), root Wayback timeline, and frozen Phase 1.4 scoring.
- **Arm B (Deep Expansion)**: Starts with Arm A evidence, queries historical indexes for public path candidates (`/~user/`, `old/`, `archive/`, `doc/`, `pub/`, `history/`), scores retrieval priority, fetches top candidates, and evaluates deep evidence under the identical frozen scorer.

### Principle 2: Scorer Freeze
Scoring rules, signal definitions, and weights were held strictly constant (`scoring_version: 1.4_frozen`). No ad-hoc rules or domain-specific exceptions were introduced.

### Principle 3: Deterministic Study Sampling
The 300-domain study subset was sampled deterministically (`seed=42`) from Corpus v2:
- Universities: 60
- Government: 60
- Nonprofits: 45
- Long-running companies: 45
- Open-source / project sites: 45
- Personal / independent sites: 45

### Principle 4: Passive, Ethical Exploration
No aggressive directory fuzzing, credential guessing, or access control bypasses. Path candidates were derived exclusively from public historical indices and public root links with a strict ceiling of `max_candidates=50` and `max_retrievals=15`.

---

## 3. Data Integrity & Verification
- Evidence frozen in `data/phase1_5/evidence/raw_artifacts/` (2,760 payloads).
- Cryptographic SHA-256 manifest recorded in `data/phase1_5/evidence_manifest.json`.
- 1-to-1 record join across `study_domains.csv`, `root_results.jsonl`, and `deep_results.jsonl`.
