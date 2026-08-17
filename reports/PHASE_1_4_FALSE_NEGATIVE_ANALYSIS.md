# Project Atlas — Benchmark v2 False-Negative Analysis

**Document**: `reports/PHASE_1_4_FALSE_NEGATIVE_ANALYSIS.md`  
**Scope**: In-Depth Investigation of Benchmark v2 False Negatives  
**Date**: 2026-08-17T21:35:00Z  

---

## 1. False Negative Inventory

7 reference anomaly domains scored below the 40.0 candidate anomaly threshold:

| Domain | Observed Score | Classification | Primary Cause | Failure Category |
| :--- | :--- | :--- | :--- | :--- |
| **`spacejam.com`** | 0.0 | `ORDINARY` | Root domain redirects to modern Warner Bros marketing CMS portal | `F2_REDIRECT_WRAPPER` / `F7` |
| **`zombo.com`** | 0.0 | `ORDINARY` | Replaced legacy Flash embed with HTML5 `<audio>` tag; lacks table layout | `F6_DYNAMIC_CONTENT` |
| **`catb.org`** | 20.0 | `ORDINARY` | Preformatted ASCII text archive; lacks `<table>` tags (+20 retro only) | `F3_ASCII_LAYOUT` |
| **`textfiles.com`** | 0.0 | `ORDINARY` | Upstream connection timeout during live scan window | `F4_ARCHIVE_COVERAGE` |
| **`wiby.me`** | 0.0 | `ORDINARY` | Minimalist modern search engine format; modern creation date (2018) | `F4_ARCHIVE_COVERAGE` |
| **`frogfind.com`** | 20.0 | `ORDINARY` | Retro styling (+20) scored below 40.0 threshold; modern creation date (2021) | `F4_ARCHIVE_COVERAGE` |
| **`68k.news`** | 20.0 | `ORDINARY` | Retro styling (+20) scored below 40.0 threshold; modern creation date (2020) | `F4_ARCHIVE_COVERAGE` |

---

## 2. Failure Analysis by Archetype

1. **Redirect Wrappers (`spacejam.com`)**: Living relics preserved by parent corporations are often placed behind modern HTTPS portals or redirects. A root-only scanner evaluates the modern landing page.
2. **Plain ASCII Text Archives (`catb.org`)**: The detector's current ruleset rewards table layouts (+20) and framesets (+30), but assigns 0 points to unadorned `<pre>` ASCII documentation.
3. **Modern Retro Engines (`frogfind.com`, `68k.news`, `wiby.me`)**: These sites intentionally render retro web interfaces, but their domain history begins post-2018, preventing them from accumulating historical archive points (+15 to +35).
