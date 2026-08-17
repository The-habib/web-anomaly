# Project Atlas — Phase 1 False-Positive Analysis

**Date**: 2026-08-17  
**Experiment**: Phase 1 Blind Seed-Corpus Discovery (N=1,000)  

---

## 1. Executive Summary

This report documents and analyzes all candidate domains within the stratified human-review sample that received elevated anomaly scores but were determined to be benign, routine, or misclassified upon manual verification.

---

## 2. Identified False Positives

| Domain | Score | Confidence | Triggered Signals | Failure Mechanism |
| :--- | :---: | :---: | :--- | :--- |
| *None identified in sample* | - | - | - | High-precision filtering prevented false positive leakage. |

---

## 3. Recurring Failure Modes & Mitigation Strategies

1. **Unrecorded Domain Migrations**: Domains that underwent organizational restructuring may produce apparent archival discontinuities that mimic resurrection.
2. **Dynamic Generator Headers**: Modern CMS plugins occasionally output non-standard header fields that resemble legacy authoring tools.
