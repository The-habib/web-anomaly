# TREASURE_005 — Unmodernized Governmental Patent Manual Repository (uspto.gov)

## What Atlas Found
Atlas discovered an unmodernized archaeological surface at '/web/offices/pac/mpep/index.html' on uspto.gov. The page preserves 1990s table-based HTML layout and pre-CSS formatting. 

## Why It Is Interesting
This page survives in active service (200 OK) while the surrounding domain modernized. It exhibits 2 structural archaeological signals without contemporary frontend frameworks.

## How Atlas Found It
- **Discovery Strategy**: `ORPHAN_PATH`
- **Candidate Path**: `/web/offices/pac/mpep/index.html`
- **Target URL**: [https://uspto.gov/web/offices/pac/mpep/index.html](https://uspto.gov/web/offices/pac/mpep/index.html)
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
- **Artifact File**: [`data/treasures/evidence/raw_artifacts/uspto.gov_web_offices_pac_mpep_index.html.html`](file:///workspaces/web-anomaly/data/treasures/evidence/raw_artifacts/uspto.gov_web_offices_pac_mpep_index.html.html)

## Why Ordinary Search Might Miss It
Ordinary search behavior and modern web crawlers miss this surface because it is 5 directories deep, lacks incoming links from the current root homepage, and does not match high-ranking commercial SEO keywords.

## Prior Art
- **Classification**: `DOCUMENTED`
- **Assessment**: Atlas did not identify substantial commercial search visibility for this deep subpath during investigation.

## Confidence / Evidence Quality
- **Evidence Verification**: Cryptographically verified via live HTTP retrieval and SHA-256 digest.
- **Scope Limitation**: Preserved strictly as observed on public network endpoints without unauthorized probing.

## Cryptographic Evidence
```
SHA-256: 3cd67c36255c9faf285a5a571bc3ed8746382cef28d9022e1cce665ad87c9c2a
Validated At: 2026-08-18T07:09:22Z
```

## Reproduction
1. Run `curl -s https://uspto.gov/web/offices/pac/mpep/index.html | sha256sum`
2. Confirm SHA-256 matches `3cd67c36255c9faf285a5a571bc3ed8746382cef28d9022e1cce665ad87c9c2a`
3. Inspect HTML structure for table/retro layout elements.
