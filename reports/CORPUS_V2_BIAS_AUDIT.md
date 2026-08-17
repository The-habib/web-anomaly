# Project Atlas — Corpus v2 Representation & Bias Audit

**Document**: `reports/CORPUS_V2_BIAS_AUDIT.md`  
**Dataset Analyzed**: `data/corpus_v2/seed_corpus_v2.csv` (N=1,000)  
**Audit Objective**: Identify geographical, structural, and institutional skews in Corpus v2  

---

## 1. Top-Level Domain (TLD) Distribution

Corpus v2 spans 28 distinct TLDs across generic, sponsored, and country-code spaces:

| Top-Level Domain | Domain Count | Percentage | Representative Entities |
| :--- | :--- | :--- | :--- |
| `.org` | 338 | 33.8% | `eff.org`, `kernel.org`, `wikipedia.org`, `w3.org`, `apache.org` |
| `.com` | 244 | 24.4% | `ibm.com`, `apple.com`, `danluu.com`, `spacejam.com` |
| `.edu` | 148 | 14.8% | `harvard.edu`, `mit.edu`, `stanford.edu`, `berkeley.edu` |
| `.gov` | 122 | 12.2% | `nasa.gov`, `loc.gov`, `nih.gov`, `ca.gov`, `texas.gov` |
| `.ac.uk` | 52 | 5.2% | `ox.ac.uk`, `cam.ac.uk`, `ucl.ac.uk`, `imperial.ac.uk` |
| `.uk` / `.gov.uk` | 24 | 2.4% | `gov.uk`, `parliament.uk`, `nhs.uk`, `bbc.co.uk` |
| `.de` / `.fr` / `.it` / `.es` | 28 | 2.8% | `bund.de`, `service-public.fr`, `governo.it`, `lamoncloa.gob.es` |
| `.io` / `.net` / `.int` / `.ch` / others | 44 | 4.4% | `redis.io`, `ietf.org`, `who.int`, `cern.ch`, `admin.ch` |

---

## 2. Institutional vs Independent Balance

An essential design goal was preventing Corpus v2 from being dominated entirely by modern venture-backed startups or monolithic tech platforms:

- **Institutional Portals (Universities + Government)**: 40.0% (400 domains)
- **Civil Society & Open Source (Nonprofits + FOSS)**: 30.0% (300 domains)
- **Commercial Lineages (Long-running enterprise)**: 15.0% (150 domains)
- **Handcrafted & Independent Web (Blogs, Tildes, BBS, Retro)**: 15.0% (150 domains)

This balance guarantees that Atlas encounters both heavy, multi-layered enterprise CDNs (e.g. `microsoft.com`, `nasa.gov`) and minimal, hand-edited static HTML documents (e.g. `stallman.org`, `toastytech.com`, `textfiles.com`).

---

## 3. Geographic Distribution & Inherent Skews

### Strengths
- **Diverse Federal Systems**: Incorporates federal and regional portals from the US, UK, Canada, Australia, Germany, France, Italy, Spain, Netherlands, Sweden, Norway, Denmark, Finland, Switzerland, Austria, Poland, Czech Republic, Greece, Brazil, Mexico, Chile, South Africa, India, Japan, and Singapore.
- **International Standards**: Contains core non-governmental international bodies headquartered across Geneva, Paris, London, and Tokyo.

### Documented Skews (To be addressed in future expansions)
1. **Anglophone Predominance**: Approximately 74% of the candidate pools are primarily English-language domains, driven by the historical concentration of early web infrastructure (.edu, .gov, .org).
2. **CCTLD Long-Tail**: Asian and African ccTLDs represent ~6% of the government and university cohorts, though Latin American and European representation is strong.
3. **Pre-2005 Sourcing Bias**: Because the experiment studies temporal persistence and technological fossilization, candidate curation deliberately prioritized entities with continuous existence prior to 2005.

---

## 4. Bias Mitigation Recommendations

For future Phase 2 operations:
- Incorporate automated Common Crawl CDX sampling stratified by ccTLD to expand non-Latin script coverage (.jp, .in, .br, .pl).
- Establish explicit secondary language cohorts (e.g. French, German, Spanish, Japanese, Hindi) with verified native-language seed registries.
