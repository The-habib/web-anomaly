# Project Atlas — Plain-Text & ASCII Blind Spot Analysis

**Document**: `reports/PHASE_1_4_ASCII_BLIND_SPOT.md`  
**Classification**: Empirical Research Blind Spot Investigation  
**Date**: 2026-08-17T21:35:00Z  

---

## 1. The ASCII Blind Spot Problem

A fundamental design premise in early HTML anomaly detection was that vintage 1990s websites relied heavily on multi-column table layouts (`<table cellpadding="0" cellspacing="0">`) and framesets (`<frameset>`).

However, an entire class of influential early web culture and hacker documentation consists of **unadorned plain ASCII text** formatted inside `<pre>` tags without any layout tables:
- `catb.org` (Eric S. Raymond's Jargon File and open-source essays)
- `rfc-editor.org` / `ietf.org` plain text RFC repositories
- `rawtext.club` / `tilde.town` plain text gopher/web roots
- `kernel.org/pub/` directory index text trees

---

## 2. Empirical Scoring Impact

Under the Phase 1.3/1.4 scoring rules:
- Table layout: +20.0
- Frameset layout: +30.0
- Retro tags (`<font>`, `<center>`, `bgcolor`): +20.0
- **Plain ASCII text layout (`<pre>` dominates >80% DOM)**: **+0.0 (Unscored)**

Because `catb.org` only triggered retro styling elements (+20.0), its score stalled at `20.0 / 40.0`, resulting in a false negative.

---

## 3. Empirical Justification for Future Research

This finding provides a clear, data-grounded empirical justification for adding an **ASCII/Plain-Text Layout Rule** in future research phases:
- Rule: Award +20 points when `<pre>` text content constitutes >70% of rendered body bytes and lacks modern CSS/JS frameworks.
