# Project Atlas — Phase 1 False-Negative Analysis

**Date**: 2026-08-17  
**Experiment**: Phase 1 Blind Seed-Corpus Discovery (N=1,000)  

---

## 1. Executive Summary

This report documents web phenomena discovered within the stratified control cohorts (Score 0–1) that possess genuine historical, structural, or retro-computing interest but were missed or underweighted by the automated scoring ruleset.

---

## 2. Identified False-Negative Candidates

| Domain | Automated Score | Phenomenon Description | Reason Scorer Underweighted |
| :--- | :---: | :--- | :--- |
| `tilde-user-010.org` | 0 | Genuine retro/indie web phenomenon with low automated score due to lack of traditional CMS generator tags. | Lack of traditional metadata fossils; clean plain text layout. |

---

## 3. Recommended New Anomaly Detectors for Future Phases

1. **Text-Mode / Minimalist HTML Detector**: Detect ultra-lightweight, non-CSS, plain-text pages that deliberately reject modern styling conventions.
2. **Static Directory Tilde User Graph**: Detect surviving user home directories (`/~user/`) on shared multi-user Unix servers.
