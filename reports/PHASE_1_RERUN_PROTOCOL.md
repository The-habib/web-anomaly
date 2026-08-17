# Project Atlas — Phase 1 Future Rerun Protocol Specification

**Status**: `PROPOSED / ARCHIVED PROTOCOL`  
**Purpose**: Define the precise experimental requirements for any future execution of the 1,000-domain blind discovery experiment.

---

## 1. Required Modifications from Phase 1 Baseline

1. **Elimination of Synthetic Procedural Padding**:
   - Curated candidate pools must contain $\ge 500$ verified real-world public domains per category prior to sampling.
   - The sampling engine must raise an explicit `CorpusDeficitError` rather than synthesizing placeholder hostnames if pools are insufficient.
2. **Dynamic Review Cohort Binding**:
   - The review sampler must dynamically sample up to a fixed target $N$ by expanding control and random strata if candidate strata have small counts.
   - Report generator code must bind directly to `len(load_jsonl('data/human_reviews.jsonl'))` with zero fallback constants.
3. **Scoring Engine Refinement (`phase1-score-v2`)**:
   - Single-point 404 snapshots on continuous academic/institutional domains must not trigger resurrection signals unless multi-year continuous downtime is verified.
4. **Calibrated Confidence Labeling**:
   - Explicitly label confidence values as `Heuristic Confidence Score` in all reporting outputs.
