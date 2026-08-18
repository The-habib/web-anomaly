# Project Atlas — Phase 1.8 Arm Design & Sampling Mechanics Audit

**Project**: Atlas Autonomous Research Laboratory  
**Phase**: 1.8 Independent Scientific Audit & Experimental Design Validation  
**Date**: 2026-08-18T05:59:00Z  
**Classification**: **`TAIL_SELECTION_VS_REMAINDER_CONTROL`**  
**Audit Artifacts**: `audit/phase1_8/arm_design_audit.json`, `audit/phase1_8/zero_trust_reconstruction.json`

---

## 1. Executive Summary

Phase 1.7 intended to execute a controlled randomized trial comparing a **Uniform Random Selection Control (Arm U)** against a **Path Density Prioritized Treatment (Arm D)** on Corpus v2 ($N=1,000$ domains).

An independent algorithmic inspection of `atlas/density/sampler.py` revealed that **Arm U was not drawn as an unconstrained uniform random sample from the general population**. Instead, Arm D was selected first by extracting the top density percentiles per category, and Arm U was sampled second from the remaining truncated pool. Consequently, Arm U represents a **Remainder Control** that was systematically censored from containing high-density domains.

---

## 2. Sampling Algorithm Forensics

In `atlas/density/sampler.py` (lines 147–158):

```python
for cat, records in eligible_by_cat.items():
    quota = arm_quota_per_cat.get(cat, 15)
    # Step 1: Arm D (Tail Selection)
    sorted_by_density = sorted(records, key=lambda x: x.d_raw, reverse=True)
    selected_d = sorted_by_density[:quota]
    arm_d_records.extend(selected_d)

    # Step 2: Arm U (Remainder Draw)
    remaining = [r for r in records if r not in selected_d]
    rng.shuffle(remaining)
    selected_u = remaining[:quota]
    arm_u_records.extend(selected_u)
```

### Key Mechanical Findings:
1. **Sampling Order**: Arm D was extracted **first**; Arm U was extracted **second**.
2. **Population Censoring**: The top 100 highest-density eligible domains were assigned to Arm D. Arm U was restricted to the bottom 700 eligible domains.
3. **Density Truncation**: No domain in Arm U has a $d_{\text{raw}}$ value exceeding the category cutoff of Arm D.

---

## 3. Balance Audit & Density Disparity

Standardized balance table across both arms ($N=100$ domains each):

| Dimension / Metric | Arm U (Remainder Control) | Arm D (Tail Selection) | Disparity / Contrast |
| :--- | :--- | :--- | :--- |
| **Total Domains** | 100 | 100 | Equal ($1:1$) |
| **Category Representation** | Matched (6 categories) | Matched (6 categories) | $100\%$ Identical |
| **Mean $d_{\text{raw}}$ (Path Volume)** | $12.4$ paths/domain | $248.6$ paths/domain | **$20.0\times$ higher in Arm D** |
| **Median $d_{\text{raw}}$** | $4.0$ paths/domain | $142.0$ paths/domain | **$35.5\times$ higher in Arm D** |
| **Mean $d_{\text{user}}$ (User Spaces)** | $0.2$ paths/domain | $41.8$ paths/domain | **$209.0\times$ higher in Arm D** |
| **Mean Total Captures** | $28.5$ captures | $412.3$ captures | **$14.5\times$ higher in Arm D** |
| **Archive Coverage Span** | $1.2$ years | $1.8$ years | $+50.0\%$ in Arm D |

---

## 4. Formal Experimental Classification

We formally classify the Phase 1.7 experimental design as:

$$\mathbf{Class = \text{TAIL\_SELECTION\_VS\_REMAINDER\_CONTROL}}$$

### Scientific Implications:
- The experiment did not contrast a random sample against a prioritized sample. It contrasted the **extreme upper tail of path density** against the **lower/middle remainder**.
- This design maximizes contrast and statistical power to detect whether density matters at all, but it slightly overestimates the effect size relative to a true unconstrained natural uniform draw.
- Future phases (Phase 2) must implement a **pure randomized block trial** where domains are randomly assigned to arms before density prioritization is applied within arms.

---

## 5. Reproduction Command

```bash
PYTHONPATH=. python3 atlas/research/audit_phase1_8.py
```
