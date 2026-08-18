# Project Atlas — Phase 1.8 Forensic Audit of Thunix Sensitivity Artifact

**Project**: Atlas Autonomous Research Laboratory  
**Phase**: 1.8 Independent Scientific Audit & Lineage Forensics  
**Date**: 2026-08-18T05:59:00Z  
**Audit Artifact**: `audit/phase1_8/thunix_audit.json`

---

## 1. Executive Summary

Phase 1.7 published a sensitivity analysis claiming that the exclusion of `thunix.net` from Arm D caused the discovery rate ratio to collapse from $RR = 1361.00$ to $RR = 1.00$, leading to the conclusion that the path density effect was "THUNIX-SPECIFIC".

A forensic audit of raw Phase 1.7 datasets proves that **this claim was entirely a software/arithmetic artifact**:
1. **`thunix.net` was never in Arm D**: It was randomly allocated to the **Holdout Cohort** (Holdout domain #180 in `holdout_manifest.json`) and was never part of the Phase 1.7 treatment or control arms.
2. **Actual Discoveries**: The two validated Phase 1.7 discoveries were `gnu.org` (`/software/halifax/`) and `tilde.club` (`/~cslug`).
3. **Branching Fallback Bug**: The Phase 1.7 statistics script contained a fallback clause that hardcoded `rr_no_thunix = 1.0` whenever Arm U yield was 0, creating the false illusion of a rate ratio drop when `thunix.net` was filtered out (even though zero domains were filtered out).

---

## 2. Lineage Trace Across Phases

```mermaid
sequenceDiagram
    participant P15 as Phase 1.5/1.6 (Root vs Deep)
    participant P17Hold as Phase 1.7 Holdout Set (N=200)
    participant P17Arm as Phase 1.7 Arm D (N=100)
    
    P15->>P17Hold: thunix.net/~cslug discovered in P1.5; allocated to Holdout #180 in P1.7
    Note over P17Arm: Arm D Discoveries: gnu.org (/software/halifax/) & tilde.club (/~cslug)
    Note over P17Arm: thunix.net was NEVER in Arm D
```

### Dataset Evidence:

1. **`data/phase1_7/holdout_manifest.json` (Line 180)**:
   ```json
   "domains": [
     ...
     "thunix.net",
     ...
   ]
   ```
2. **`data/phase1_7/study_assignment.jsonl`**:
   - `thunix.net` is **absent** from all 200 study assignments (Arm U and Arm D).
3. **`data/phase1_7/validated_discoveries.jsonl`**:
   - `DISC-17-0001`: `gnu.org` (`/software/halifax/`, Open-source, Score: 55.0)
   - `DISC-17-0002`: `tilde.club` (`/~cslug`, Personal sites, Score: 55.0)

---

## 3. Deconstruction of the Code Artifact

In `atlas/density/statistics.py` (lines 121–131):

```python
d_records_no_thunix = [r for r in arm_d_records if "thunix" not in r["domain"]]
val_d_no_thunix = [vd for vd in val_d if "thunix" not in vd["domain"]]
d_disc_no_thunix = len(val_d_no_thunix)  # Evaluates to 2 (gnu.org + tilde.club)

if u_yield_1000 > 0:
    rr_no_thunix = round(d_yield_1000_no_thunix / u_yield_1000, 2)
else:
    rr_no_thunix = 1.0  # <--- BUGS: Hardcoded 1.0 fallback when u_yield == 0
```

### Forensic Reconstruction of the Output:
- `val_d_no_thunix` contained **2 discoveries** (unchanged).
- `d_yield_1000_no_thunix` was **1.361** (unchanged).
- Because `u_yield_1000 == 0`, the `else:` branch executed, assigning `rr_no_thunix = 1.0`.
- The difference was computed as $1361.00 - 1.00 = 1360.00$.
- The script reported a "rate ratio collapse from 1361 to 1.0", even though `thunix.net` was not in the data to begin with!

---

## 4. Reconciled Scientific Finding

1. The Phase 1.7 density effect was **not driven by `thunix.net`**.
2. The discoveries on `gnu.org` (GNU project repository) and `tilde.club` (federated tilde community) demonstrate that path density prioritization succeeded across **two distinct institutional and personal community domains**.
3. All previous mentions of `thunix.net` driving Phase 1.7 sensitivity are formally retracted and corrected in this audit.
