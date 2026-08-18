# Project Atlas — Phase 1 Seed Corpus Audit

**Date**: 2026-08-18  
**Experiment ID**: `0002`  
**Sampling Seed**: `42`  
**Total Corpus Size**: `20` domains  

---

## 1. Executive Summary

This audit evaluates the composition, distribution, and structural characteristics of the Phase 1 seed corpus. The corpus was generated using deterministic pseudo-random sampling (`seed=42`) to guarantee perfect scientific reproducibility across independent runs.

---

## 2. Category Distribution

| Category | Domain Count | Share (%) |
| :--- | :---: | :---: |
| **Universities** | 10 | 50.0% |
| **Government** | 10 | 50.0% |
| **Total** | **`20`** | **100.0%** |

---

## 3. Top-Level Domain (TLD) Representation

| TLD Suffix | Domain Count | Share (%) |
| :--- | :---: | :---: |
| `.edu` | 7 | 35.0% |
| `.gov` | 6 | 30.0% |
| `.fr` | 2 | 10.0% |
| `.it` | 1 | 5.0% |
| `.at` | 1 | 5.0% |
| `.de` | 1 | 5.0% |
| `.gov.za` | 1 | 5.0% |
| `.gov.pl` | 1 | 5.0% |

---

## 4. Domain Name Length Distribution

| Length Tier | Domain Count | Share (%) |
| :--- | :---: | :---: |
| <= 10 chars | 12 | 60.0% |
| 11-15 chars | 7 | 35.0% |
| 16-20 chars | 0 | 0.0% |
| > 20 chars | 1 | 5.0% |

---

## 5. Potential Selection Biases & Constraints

1. **Category Quota Stratification**: The corpus deliberately forces equal or near-equal quotas across 6 distinct institutional and independent categories to ensure adequate representation of non-commercial and academic surfaces. This is not representative of raw internet traffic distributions.
2. **Historical Domain Survivorship**: Curated base candidates skew towards long-lived, high-reputation domains (e.g. established universities and early Internet RFC organizations).
3. **Observational Scope**: This corpus represents a controlled observational benchmark for Project Atlas, not a statistical census of the entire World Wide Web.
