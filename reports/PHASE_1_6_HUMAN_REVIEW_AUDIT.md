# Phase 1.6 Human Review Audit & Blindness Analysis — Project Atlas

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.6 Independent Scientific Audit  
**Date**: 2026-08-17T22:42:00Z  
**Blindness Classification**: **`OBSERVATION_BLIND_BUT_ARM_VISIBLE`**  

---

## 1. Executive Summary of Review Protocol

Phase 1.5 implemented a paired human review protocol to evaluate whether archaeological anomalies discovered via deep expansion were authentic relics or modern false positives. A sample of 20 paired dossiers was generated in `data/phase1_5/blind_paired_dossiers.jsonl` and reviewed in `data/phase1_5/human_reviews.jsonl`.

The Phase 1.6 audit evaluated whether the protocol satisfied the requirements of blind scientific evaluation.

---

## 2. Dossier Inspection & Blinding Properties

Each review dossier (`paired-rev-0001` through `paired-rev-0020`) presented the reviewer with the following structured JSON schema:

```json
{
  "dossier_id": "paired-rev-0001",
  "domain": "thunix.net",
  "category": "Personal/independent sites",
  "root_observed_path": "/",
  "deep_observed_path": "/~cslug",
  "total_candidates_found": 2989,
  "total_retrievals_evaluated": 15,
  "review_instructions": "Classify target domain based purely on observed archaeological structure: [ORDINARY, INTERESTING, POTENTIAL_ANOMALY, CLEAR_ANOMALY, INSUFFICIENT_EVIDENCE]"
}
```

### Blinding Analysis:
1. **Numerical Scores & Anomaly Points**: **STRICTLY HIDDEN**. Neither root score (35.0) nor deep score (55.0) was provided to reviewers.
2. **Rule Triggers & Weights**: **STRICTLY HIDDEN**. Triggered rules (`html_tables_layout`, `retro_styling_elements`) were not shown.
3. **Discovery Arm Labeling**: **PARTIALLY VISIBLE VIA PATH NOTATION**. While the explicit arm tags ("Arm A" vs "Arm B") were omitted, presenting `root_observed_path: "/"` alongside `deep_observed_path: "/~cslug"` inherently reveals that `~cslug` was discovered via deep expansion.

---

## 3. Formal Blindness Classification

| Blindness Level | Definition | Assessment |
| :--- | :--- | :--- |
| `FULLY_BLIND` | Reviewer has zero indication of which surface originated from which arm. | **NO** (Path string differentiates root `/` from subpath). |
| **`OBSERVATION_BLIND_BUT_ARM_VISIBLE`** | **Reviewer is blinded to scores, weights, and automated classifications, but can observe the target URL subpath.** | **YES (Definitive Classification)** |
| `NOT_BLIND` | Reviewer has access to scores and pipeline classifications. | **NO** (Scores were strictly blinded). |

---

## 4. Review Verdicts Distribution & Concordance

| Verdict Category | Count | Domains | Concordance with Automated Scorer |
| :--- | :--- | :--- | :--- |
| **`CLEAR_ANOMALY`** | **1** | `thunix.net` (Deep path `~cslug`) | 100% agreement with `CANDIDATE_ANOMALY` (55.0) |
| **`ORDINARY`** | **19** | 19 institutional & corporate domains | 100% agreement with `ORDINARY` (0.0) |
| **`POTENTIAL_ANOMALY`** | 0 | None | N/A |
| **`INSUFFICIENT_EVIDENCE`**| 0 | None | N/A |
| **TOTAL** | **20** | | **100.0% Scorer-Reviewer Concordance** |

- **Assessment Changed by Depth**: Exactly **1 of 20** domains (`thunix.net` changed from `ORDINARY` on root to `CLEAR_ANOMALY` on deep).
- **Reviewer Notes on `thunix.net`**: *"Deep path /~cslug exhibits authentic 1990s table/retro layout while root was modernized."*

---

## 5. Recommendation for Phase 2 Blind Review Protocols

To achieve `FULLY_BLIND` review in Phase 2:
1. Present randomized single-surface dossiers where root and deep URLs are shuffled into an anonymized queue without paired side-by-side presentation.
2. Anonymize URL hostnames when rendering visual HTML previews to eliminate domain familiarity bias.
