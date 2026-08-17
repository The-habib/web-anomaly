# Project Atlas — Phase 1 Sampling & Randomization Audit

**Audit Phase**: `Phase 1.1 Independent Scientific Audit`  
**Sampling Seed**: `42`  
**RNG Engine**: Python `random.Random(seed=42)`  

---

## 1. Executive Summary

This audit evaluates the randomization, determinism, and procedural candidate selection mechanisms employed in Phase 1 corpus generation (`atlas/phase1/corpus.py`).

### Key Findings:
1. **Deterministic Reproducibility**: 100% verified. Replaying the sampling procedure from `seed=42` produces an identical sequence of 1,000 domains (`Exact Domain Identity Match: True`).
2. **Category Independence**: Categories were sampled independently in sequential loops using the shared deterministic RNG stream.
3. **Candidate Pool Composition**:
   - Initial curated pool: 901 unique public domains.
   - Procedurally generated padding: 99 synthetic pattern domains added to meet exact target quotas.
4. **Ordering Influence**: Selected domains within each category were lexicographically sorted (`sorted(selected)`) before persistence, eliminating arbitrary selection order artifacts.
5. **Timestamp Variability**: The CSV column `selection_timestamp` embeds the execution timestamp, which alters full-file SHA-256 digests across runs while leaving domain sequences identical.

---

## 2. Plain-Language Algorithm Description

```
For each (category, quota) in TargetDistribution:
    1. Retrieve category candidate pool.
    2. Normalize all domain strings (strip protocol, path, port).
    3. If pool size < quota:
         Calculate deficit = quota - len(pool).
         Procedurally append deficit synthetic placeholder domains (e.g. corp-NNN.com).
    4. Deterministically sample 'quota' domains using random.Random(42).sample().
    5. Sort selected domains lexicographically.
    6. Emit CSV record with domain, canonical_url, category, and metadata.
```

---

## 3. Evaluation & Recommendations

- **Strengths**: The sampling is fully deterministic and independently verifiable.
- **Flaws Identified**: Procedural pool expansion created synthetic entries rather than drawing from expanded public registries.
- **Phase 1.1 Remediation**: Candidate pools must be pre-populated with $>1,000$ verified real-world public domains per category so procedural synthesis is never invoked.
