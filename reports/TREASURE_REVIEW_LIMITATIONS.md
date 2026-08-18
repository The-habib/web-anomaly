# Project Atlas — Treasure Review Limitations
## Known Constraints, Scope Boundaries, and Methodological Notes

```
=====================================================================================
                          TREASURE REVIEW LIMITATIONS
=====================================================================================
```

### 1. Scope & Execution Boundaries

1. **Point-in-Time Observations**: Live evidence reflects the public web state observed at the time of Run #003 investigation (2026-08-18). Some ephemeral dynamic endpoints may evolve over time.
2. **Reviewer Subjectivity**: Human evaluators may have divergent definitions of "historical interest." Atlas records the reviewer identity, confidence score, and qualitative notes for every judgment rather than claiming an objective absolute truth.
3. **Quarantine of Cross-Run Memory**: Prior art findings and human reviews from Run #002 and Run #003 are strictly quarantined in `data/memory/` and `data/review_results/` and do not modify blind exploration seeds.
4. **Offline Packet Limitations**: Offline exported sessions include preserved raw HTML paths and SHA-256 digests. Rendering dynamic external client-side scripts is outside the review console scope.

---

### 2. Methodological Guarantees

- **No Synthetic Consensus**: Single-reviewer evaluations are transparently labeled `reviewer_count = 1` and never reported as multi-rater consensus.
- **Zero Automatic Validation**: No automated process or release gate has the authority to transition machine candidates into validated museum treasures.
