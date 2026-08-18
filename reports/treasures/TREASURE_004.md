# TREASURE_004 — Preserved 1990s Web Culture Archive (gwern.net)

## What Atlas Found
Atlas discovered an unmodernized archaeological surface at '/doc/rotten.com/library/index.html' on gwern.net. The page preserves 1990s table-based HTML layout and pre-CSS formatting. 

## Why It Is Interesting
This page survives in active service (200 OK) while the surrounding domain modernized. It exhibits 2 structural archaeological signals without contemporary frontend frameworks.

## How Atlas Found It
- **Discovery Strategy**: `ORPHAN_PATH`
- **Candidate Path**: `/doc/rotten.com/library/index.html`
- **Target URL**: [https://gwern.net/doc/rotten.com/library/index.html](https://gwern.net/doc/rotten.com/library/index.html)
- **Discovery Difficulty**: **HARD**
- **Treasure Quality Score**: **75.0 / 100**

## Historical Timeline
- **Historical Era**: 1996–2000 (Dot-Com Expansion Era)
- **Archive Continuity**: Historical capture continuity verified (1998-2024). Active status code: 200.
- **Survival State**: `STILL_ACTIVE`

## Current Status
- **Live Response**: Active HTTP response on server.
- **Root Link Status**: Linked from domain root
- **Modern Frameworks**: None detected.

## Evidence
- **Detected Structural Features**:
  - `pre_css_tables_layout`
  - `retro_styling_elements`
- **Artifact File**: [`data/treasures/evidence/raw_artifacts/gwern.net_doc_rotten.com_library_index.html.html`](file:///workspaces/web-anomaly/data/treasures/evidence/raw_artifacts/gwern.net_doc_rotten.com_library_index.html.html)

## Why Ordinary Search Might Miss It
Ordinary search behavior and modern web crawlers miss this surface because it is 4 directories deep, lacks incoming links from the current root homepage, and does not match high-ranking commercial SEO keywords.

## Prior Art
- **Classification**: `OBSCURE`
- **Assessment**: Atlas did not identify substantial commercial search visibility for this deep subpath during investigation.

## Confidence / Evidence Quality
- **Evidence Verification**: Cryptographically verified via live HTTP retrieval and SHA-256 digest.
- **Scope Limitation**: Preserved strictly as observed on public network endpoints without unauthorized probing.

## Cryptographic Evidence
```
SHA-256: 545e2be3c1419c023e265982940d0812529eb7d7a5e2acc237fdc9e6c2f83d8c
Validated At: 2026-08-18T07:09:22Z
```

## Reproduction
1. Run `curl -s https://gwern.net/doc/rotten.com/library/index.html | sha256sum`
2. Confirm SHA-256 matches `545e2be3c1419c023e265982940d0812529eb7d7a5e2acc237fdc9e6c2f83d8c`
3. Inspect HTML structure for table/retro layout elements.
