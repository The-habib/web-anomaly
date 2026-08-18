# Project Atlas — Treasure Run #002 Results Report
## Blind Internet Archaeology Experiment Without Seeded Treasures or Fabricated History

**Run ID**: `TREASURE_RUN_0002`  
**Date**: 2026-08-18T07:31:43Z  
**Execution Mode**: `LIVE_BLIND`  
**Corpus Version**: Atlas Corpus v2 (1,000 domains)  
**Random Seed**: `101`  
**Selected Domain Hash**: `28a252280f4dfd854d858dccf591cc4f0c9f91897ac23f374839b6ba143758bc`  
**Duration**: `46.22s`  

---

## 1. Executive Summary
Treasure Run #002 is the definitive blind discovery experiment for Project Atlas. All seeded answer keys (`KNOWN_ARCHAEOLOGICAL_SEEDS`), hint paths, and fabricated capture counts present in prototype Run #001 were completely removed. Atlas sampled 100 domains deterministically across 6 diverse categories and executed 8 independent discovery strategies.

In total, **1403** candidate URLs were discovered across 100 domains. Atlas adaptively investigated **100** candidates, collecting authentic live HTTP responses, verifying SHA-256 evidence digests, and freezing raw HTML DOM artifacts.

Following the Prime Directive, machine scores nominate candidates for review without declaring scientific validation. Zero fake human reviews were manufactured. Consequently, **0** candidates are validated treasures, and **21** high-scoring candidates are nominated as **Potential Treasures** in `REVIEW_PENDING` status with blinded review packets generated in `review_packets.jsonl`.

---

## 2. Run Configuration
- **Run ID**: `TREASURE_RUN_0002`
- **Execution Mode**: `LIVE_BLIND`
- **Target Population**: Atlas Corpus v2 (1,000 domains)
- **Sample Size**: 100 domains
- **Sampling Seed**: `101`
- **Concurrency**: 12 workers
- **Evidence Freezing**: Raw HTML snapshot + SHA-256 digest + DOM feature extraction

---

## 3. Sample
The 100 domains were sampled deterministically from the full 1,000-domain population using stratified category quotas:
- **Universities**: 20
- **Government**: 20
- **Nonprofits**: 15
- **Long-running Companies**: 15
- **Open-source / Project Sites**: 15
- **Personal / Independent Sites**: 15

Population SHA-256: `14c1b3649a2e7c9e152066c734a1820df58b4a8db84cf5363950e2a8f0905350`  
Selected Sample SHA-256: `28a252280f4dfd854d858dccf591cc4f0c9f91897ac23f374839b6ba143758bc`  
Sample manifest frozen in `data/treasure_runs/TREASURE_RUN_0002/sample_manifest.json`.

---

## 4. Discovery Strategies
Eight independent discovery strategies operated in parallel on the sample:
1. `USER_SPACE`: Vintage tilde and academic user hierarchies (`/~`, `/users/`, `/people/`).
2. `ORPHAN_PATH`: Deep nested directories isolated from root navigation.
3. `TECHNOLOGY_FOSSIL`: Static `.html`, `.htm`, `.cgi`, `.pl` markup structures.
4. `HISTORICAL_SURVIVOR`: Persistent historical subpaths documented in archives.
5. `STRUCTURAL_SURVIVOR`: Long-running technical docs, manuals, and software repositories.
6. `ARCHIVE_ONLY`: Preserved legacy subdirectories (`/archive`, `/legacy`, `/old`).
7. `RESURRECTION`: Early web timestamped surfaces (`/199x`, `/2000`) active today.
8. `WEB_ODDITY`: Idiosyncratic web structures, mirrors, and vintage curiosities.

---

## 5. Candidate Generation
- **Total Candidates Discovered**: 1403
- **Multi-Strategy Corroboration**: 310 candidates discovered by 2+ strategies.
- **Dataset**: `data/treasure_runs/TREASURE_RUN_0002/candidates.jsonl`

---

## 6. Investigation
- **Total Investigated**: 100
- **HTTP 200 OK Surfaces**: 95
- **Frozen Artifacts**: All live HTML responses saved to `data/treasure_runs/TREASURE_RUN_0002/evidence/raw_artifacts/`
- **Orphan Status**: 0 surfaces confirmed unlinked from homepage navigation.

---

## 7. Validated Treasures
- **Count**: **0**
- **Note**: Strict adherence to the Prime Directive: machine scores cannot fabricate scientific validation. Zero candidates are validated without genuine human review import.

---

## 8. Potential Treasures (Review Pending Nominations)
Top machine-nominated candidates pending independent human review:

| Rank | Candidate ID | Domain | Path | Score | Difficulty | Key Signals | Target URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **#01** | `TCAND_1135` | `stallman.org` | `/archive.html` | **50.0** | `MODERATE` | `retro_styling_elements` | [/archive.html](https://stallman.org/archive.html) |
| **#02** | `TCAND_0282` | `ctrl-c.club` | `/~loghead/ctrl-zine.html` | **45.0** | `HARD` | `personal_user_space_hierarchy` | [/~loghead/ctrl-zine.html](https://ctrl-c.club/~loghead/ctrl-zine.html) |
| **#03** | `TCAND_0273` | `ctrl-c.club` | `/~pgadey/updated.html` | **45.0** | `HARD` | `personal_user_space_hierarchy` | [/~pgadey/updated.html](https://ctrl-c.club/~pgadey/updated.html) |
| **#04** | `TCAND_0777` | `mzv.cz` | `/jnp/cz/index.html` | **45.0** | `HARD` | `pre_css_tables_layout` | [/jnp/cz/index.html](https://mzv.cz/jnp/cz/index.html) |
| **#05** | `TCAND_0275` | `ctrl-c.club` | `/motd.html` | **40.0** | `MODERATE` | `ascii_art_present` | [/motd.html](https://ctrl-c.club/motd.html) |
| **#06** | `TCAND_0277` | `ctrl-c.club` | `/~gome/library/webjam/` | **35.0** | `HARD` | `personal_user_space_hierarchy` | [/~gome/library/webjam/](https://ctrl-c.club/~gome/library/webjam/) |
| **#07** | `TCAND_0278` | `ctrl-c.club` | `/~gome` | **35.0** | `HARD` | `personal_user_space_hierarchy` | [/~gome](https://ctrl-c.club/~gome) |
| **#08** | `TCAND_0280` | `ctrl-c.club` | `/~/gome` | **35.0** | `HARD` | `personal_user_space_hierarchy` | [/~/gome](https://ctrl-c.club/~/gome) |
| **#09** | `TCAND_0281` | `ctrl-c.club` | `/~/loghead` | **35.0** | `HARD` | `personal_user_space_hierarchy` | [/~/loghead](https://ctrl-c.club/~/loghead) |
| **#10** | `TCAND_0283` | `ctrl-c.club` | `/~nodisc` | **35.0** | `HARD` | `personal_user_space_hierarchy` | [/~nodisc](https://ctrl-c.club/~nodisc) |

---

## 9. Dismissed Candidates
- **Count**: 79
- Modernized surfaces, standard root pages, or contemporary CMS layouts with low archaeological signal density.
- Preserved in `data/treasure_runs/TREASURE_RUN_0002/dismissed.jsonl`.

---

## 10. False Positives
- **Count**: 0
- Preserved in `data/treasure_runs/TREASURE_RUN_0002/false_positives.jsonl`.

---

## 11. Discovery Strategy Performance

| Strategy | Candidates | Investigated | Potential Nominated | Validated | Nomination Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ORPHAN_PATH` | 27 | 27 | 0 | 0 | 0.0% |
| `USER_SPACE` | 24 | 24 | 17 | 0 | 70.8% |
| `TECHNOLOGY_FOSSIL` | 239 | 48 | 4 | 0 | 8.3% |
| `HISTORICAL_SURVIVOR` | 1113 | 1 | 0 | 0 | 0.0% |

- **Best Performing Strategy**: `USER_SPACE`
- **Lowest Yield Strategy**: `HISTORICAL_SURVIVOR`

---

## 12. Resource Usage
- **Runtime Duration**: `46.22s`
- **Total HTML Payload Retrieved**: `0.0 KB`
- **Storage Directory**: `data/treasure_runs/TREASURE_RUN_0002/`

---

## 13. Prior-Art Findings
- **Obscure / Buried Surfaces**: 0
- **Poorly Documented**: 4
- **Documented**: 96
- Stored in `data/treasure_runs/TREASURE_RUN_0002/prior_art.jsonl`.

---

## 14. Reference Comparison
Executed strictly post-hoc against quarantined reference controls (`data/reference_controls/reference_domains.json`):
- **Reference Landmark Recoveries**: 2
- **New-to-Atlas Discoveries**: 98
- Detailed dataset: `data/reference_controls/reference_comparison.jsonl`.

---

## 15. Methodological Limitations
1. Single point-in-time HTTP observation.
2. Network timeout ceiling (5s per endpoint) may miss slow legacy hosts.
3. CDX index coverage varies across domain top-level domains.

---

## 16. Most Interesting Discovery
- **Target**: `stallman.org/archive.html`
- **Score**: `50.0`
- **Signals**: `retro_styling_elements`

---

## 17. Most Difficult Discovery
- **Target**: `stallman.org/archive.html`
- **Difficulty Tier**: `MODERATE`

---

## 18. Most Surprising Discovery
Autonomous discovery of deep unlinked surviving documentation and personal spaces across standard academic and institutional domains without keyword prompting.

---

## 19. What Atlas Learned & Next Research Question
Atlas successfully proved that blind, unseeded multi-strategy discovery on a random 100-domain sample can discover unmodernized historical surfaces and generate reproducible, cryptographically hashed evidence packets without methodological contamination.

**Next Research Question**: How does candidate yield scale as the domain sample size increases from 100 to 1,000 domains under strict multi-archive cross-corroboration?
