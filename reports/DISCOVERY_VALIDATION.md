# Project Atlas — Phase 1.8 Discovery Validation & Reference Contamination Audit

**Project**: Atlas Autonomous Research Laboratory  
**Phase**: 1.8 Discovery Lineage & Cryptographic Validation  
**Date**: 2026-08-18T05:59:00Z  
**Audit Artifact**: `audit/phase1_8/discovery_validation.json`

---

## 1. Executive Summary

Phase 1.8 independently audited the two validated deep discoveries generated in Phase 1.7:
1. `gnu.org` (`/software/halifax/`) — Discovery ID `DISC-17-0001`
2. `tilde.club` (`/~cslug`) — Discovery ID `DISC-17-0002`

Both artifacts were cryptographically audited, their raw HTML payloads verified, anomaly score breakdowns inspected, and reference contamination checked against all historical fixtures and negative controls.

---

## 2. Discovery Dossiers & Cryptographic Verification

### Discovery 1: GNU Halifax
- **Domain**: `gnu.org`
- **Category**: Open-source / project sites
- **Path**: `/software/halifax/`
- **Arm**: `DENSITY_PRIORITIZED` (Density Tier: `HIGH`, $d_{\text{raw}} = 104$)
- **Root Score**: $0.0$ (Root page modernized)
- **Deep Anomaly Score**: **$55.0$** (Confidence: $0.85$)
- **Human Review Verdict**: `CLEAR_ANOMALY`
- **Raw Evidence Artifact**: `data/phase1_7/evidence/raw_artifacts/gnu.org_software_halifax.html`
- **SHA-256 Digest**: `017c6643e9faea90eb0ef148dae3c36c6a6ee0eb91703673f4e3c9fe3dc5cefa`
- **Artifact Size**: $3,321$ bytes
- **Archaeological Description**: Unmodernized 1990s GNU project distribution page for Halifax (fax utility), preserved with HTML 2.0 markup, legacy `<pre>` formatting, and archaic FTP/email mirrors.

### Discovery 2: Tilde.club Cslug
- **Domain**: `tilde.club`
- **Category**: Personal / independent sites
- **Path**: `https://tilde.club/~cslug` (Internal file: `tilde.club_tilde_cslug.html`)
- **Arm**: `DENSITY_PRIORITIZED` (Density Tier: `EXTREME`, $d_{\text{raw}} = 1024$)
- **Root Score**: $35.0$
- **Deep Anomaly Score**: **$55.0$** (Confidence: $0.85$)
- **Human Review Verdict**: `CLEAR_ANOMALY`
- **Raw Evidence Artifact**: `data/phase1_7/evidence/raw_artifacts/tilde.club_tilde_cslug.html`
- **SHA-256 Digest**: `8d52c788649ec30ad562479e0bfddbaee2643a6d912440339d73d573eb10787a`
- **Artifact Size**: $2,840$ bytes
- **Archaeological Description**: Authentic handcrafted user homepage on the tilde community shell server, featuring minimalist semantic HTML, retro personal bio, and vintage web badges.
- **Evidence Path Note**: In Phase 1.7 `validated_discoveries.jsonl`, the filename was recorded with a literal `~` (`tilde.club_~cslug.html`), whereas the crawler normalized `~` to `tilde_` (`tilde.club_tilde_cslug.html`). The payload hash and existence are verified.

---

## 3. Novelty & Reference Contamination Audit

To prevent false claims of global discovery, we audit discoveries across two categories:

| Discovery | Domain | Prior In Benchmarks? | In Reference Controls? | Novelty Classification | World Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DISC-17-0001` | `gnu.org` | No | No | **OBSCURE / NEW_TO_ATLAS** | Public open-source archive |
| `DISC-17-0002` | `tilde.club` | No | No | **OBSCURE / NEW_TO_ATLAS** | Public tilde server page |

### Contamination Finding:
- **Zero Reference Contamination**: Neither discovery appeared in `benchmark_v1`, `benchmark_v2`, or `reference_controls.jsonl`.
- **Classification**: Both discoveries are authentic **`NEW_TO_ATLAS`** autonomous crawl discoveries. Atlas makes no claim of "NEW_TO_WORLD" as both are public web pages.
