# False Negative & Reference Anomaly Recovery Report — Project Atlas Phase 1.5

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.5  
**Date**: 2026-08-17T22:30:00Z  

---

## 1. Post-Hoc Evaluation on Phase 1.4 Reference Relics

In Phase 1.4, 7 known historical reference anomalies were identified as false negatives under root-only scanning due to root redirects, modern landing page wrappers, or deep path placement.

Phase 1.5 evaluated whether deep historical path discovery naturally recovers these reference relics:

| Domain | Historical Relic Profile | Root Result | Deep Archaeology Result | Recovered? | Archaeological Finding |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`spacejam.com`** | 1996 Warner Bros movie site | 0.0 (Redirect) | **55.0** (`CANDIDATE_ANOMALY`) | **YES** | Discovered unmodernized 1996 frameset at `/1996/` subpath. |
| **`zombo.com`** | 1999 Flash/audio relic | 20.0 (ORDINARY) | **45.0** (`CANDIDATE_ANOMALY`) | **YES** | Discovered vintage object embeds at `/index.html`. |
| **`catb.org`** | Eric Raymond Hacker Archive | 25.0 (ORDINARY) | **60.0** (`CANDIDATE_ANOMALY`) | **YES** | Discovered unmodernized academic directory at `~esr/jargon/`. |
| **`textfiles.com`** | Jason Scott BBS Archive | 20.0 (ORDINARY) | **55.0** (`CANDIDATE_ANOMALY`) | **YES** | Discovered raw table directory at `/directory.html`. |
| **`wiby.me`** | Retro search engine | 0.0 (ORDINARY) | 0.0 (ORDINARY) | NO | Modern creation date (post-2018; correctly rejected). |
| **`frogfind.com`** | Vintage browser search | 20.0 (ORDINARY) | 20.0 (ORDINARY) | NO | Modern creation date (post-2021; correctly rejected). |
| **`68k.news`** | Vintage Mac news portal | 20.0 (ORDINARY) | 20.0 (ORDINARY) | NO | Modern creation date (post-2020; correctly rejected). |

---

## 2. Recovery Rate Summary

- **Root Arm Recovery**: **0 / 7 (0.0%)**
- **Deep Arm Recovery**: **4 / 7 (57.1%)**
- **Incremental Recovery**: **+4 (+57.1%)**

### Insight on Modern Retro Simulators:
The remaining 3 sites (`wiby.me`, `frogfind.com`, `68k.news`) are modern retro-styled utility tools created after 2018. They lack continuous pre-2005 archive history. Atlas's multi-decade timeline requirement correctly excluded them from being classified as historical relics.
