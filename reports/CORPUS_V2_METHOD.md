# Project Atlas — Corpus v2 Construction Methodology

**Document**: `reports/CORPUS_V2_METHOD.md`  
**Dataset Version**: Corpus v2.0  
**Method Classification**: Deterministic Curated Sampling with Zero-Synthetic Guardrails  
**Seed**: `42`  

---

## 1. Scientific Requirements & Policy

The primary objective of Corpus v2 is to construct a representative, reproducible 1,000-domain public web corpus with verifiable real-world provenance for every single record.

### Core Invariants
1. **Zero Synthetic Domains (`synthetic_domains = 0`)**: No procedural generation (`univ-001.edu`, `corp-123.com`), placeholder domains (`example.com`), fabricated entity names, or unverified guesses.
2. **Deterministic Sampling**: Using a fixed PRNG seed (`seed=42`) with pre-sorted candidate pools to guarantee bit-for-bit identical outputs across environments.
3. **Category Quotas**:
   - Universities: 200 (from 326 curated candidates)
   - Government: 200 (from 203 curated candidates)
   - Nonprofits: 150 (from 160 curated candidates)
   - Long-running companies: 150 (from 157 curated candidates)
   - Open-source / project sites: 150 (from 152 curated candidates)
   - Personal / independent sites: 150 (from 151 curated candidates)
   - **Total Corpus Size: 1,000 Domains**
4. **Transparent Rejection Taxonomy**: Any malformed, duplicate, or synthetic entry is immediately logged to `data/corpus_v2/replacement_log.jsonl` with an explicit `RejectionCode`.

---

## 2. Candidate Pool Sourcing Strategy

Each category draws from established, publicly verifiable entity registries:

### 1. Universities (`Universities`, Quota: 200, Pool: 326)
- **Source**: US Department of Education IPEDS database and UK Higher Education Statistics Agency (HESA).
- **Domains**: Major US research universities (`harvard.edu`, `mit.edu`, `stanford.edu`), state university systems (`berkeley.edu`, `umich.edu`, `utexas.edu`), liberal arts colleges (`williams.edu`, `amherst.edu`, `swarthmore.edu`), and UK institutions (`ox.ac.uk`, `cam.ac.uk`, `ucl.ac.uk`, `ed.ac.uk`).

### 2. Government (`Government`, Quota: 200, Pool: 203)
- **Source**: US Federal Executive/Legislative registries (`usa.gov`, `loc.gov`, `nasa.gov`, `nih.gov`), all 50 US State portals (`ca.gov`, `texas.gov`, `ny.gov`), and international government portals (UK `gov.uk`, Canada `canada.ca`, Australia `australia.gov.au`, Germany `bund.de`, France `service-public.fr`, Switzerland `admin.ch`, Japan `japan.go.jp`, Brazil `gov.br`, etc.).

### 3. Nonprofits & Standards Bodies (`Nonprofits`, Quota: 150, Pool: 160)
- **Source**: Global standards organizations (`w3.org`, `ietf.org`, `icann.org`, `iso.org`), international institutions (`un.org`, `who.int`, `unesco.org`, `cern.ch`), major philanthropic foundations (`gatesfoundation.org`, `fordfoundation.org`, `rockefellerfoundation.org`), national libraries and museums (`bl.uk`, `bnf.fr`, `metmuseum.org`, `smithsonian.org`), and open knowledge platforms (`archive.org`, `gutenberg.org`, `arxiv.org`).

### 4. Long-Running Companies (`Long-running companies`, Quota: 150, Pool: 157)
- **Source**: Major global enterprise records with established corporate lineages (e.g. IBM, Microsoft, Apple, Xerox, Siemens, Philips, Ericsson, Nokia, Nintendo, Toyota, Boeing, John Deere, BP, Shell, General Electric), historical dialup ISPs and tech pioneers (Panix, Halcyon, Eskimo North, Silicon Graphics, DEC, Amiga, Atari, Cray).

### 5. Open-Source Projects (`Open-source/project sites`, Quota: 150, Pool: 152)
- **Source**: Core operating systems (`kernel.org`, `gnu.org`, `debian.org`, `freebsd.org`, `openbsd.org`, `archlinux.org`), programming language communities (`python.org`, `ruby-lang.org`, `perl.org`, `rust-lang.org`, `golang.org`, `lua.org`, `crystal-lang.org`, `ziglang.org`), web infrastructure (`apache.org`, `nginx.org`, `postgresql.org`, `sqlite.org`, `redis.io`, `curl.se`, `openssl.org`), and modern CNCF/open-source tools (`kubernetes.io`, `prometheus.io`, `grafana.com`, `godotengine.org`, `blender.org`).

### 6. Personal & Independent Sites (`Personal/independent sites`, Quota: 150, Pool: 151)
- **Source**: Weblog pioneers and digital essayists (`scripting.com`, `kottke.org`, `waxy.org`, `tbray.org`, `jwz.org`, `paulgraham.com`, `joelonsoftware.com`, `danluu.com`, `idlewords.com`, `gwern.net`, `ciechanow.ski`, `jvns.ca`), historical web art and culture archives (`spacejam.com`, `toastytech.com`, `zombo.com`, `stallman.org`, `catb.org`, `textfiles.com`), public Unix communities (`sdf.org`, `tilde.town`, `tilde.club`, `rawtext.club`), and independent search / IndieWeb nodes (`wiby.me`, `frogfind.com`, `68k.news`, `theoldnet.com`, `neocities.org`, `marginalia.nu`).

---

## 3. Sampling and Normalization Algorithm

```python
def sample_corpus_v2(validated_pools, seed=42):
    rng = random.Random(seed)
    final_corpus = []
    for category, quota in CATEGORY_QUOTAS.items():
        pool = validated_pools[category]
        # Sort deterministically by domain name prior to sampling
        sorted_pool = sorted(pool, key=lambda x: x.domain)
        if len(sorted_pool) <= quota:
            sampled = list(sorted_pool)
        else:
            sampled = rng.sample(sorted_pool, quota)
        final_corpus.extend(sampled)
    final_corpus.sort(key=lambda x: x.domain)
    return final_corpus
```

---

## 4. Verification and Rejection Logging

During the candidate ingest pipeline, all candidate records undergo:
1. `normalize_domain()`: Strip protocol, port, path, trailing dots, and convert IDN to ASCII.
2. `SYNTHETIC_PATTERNS` regex matching: Rejects pattern matches (`r"^(univ|corp|...)-\d+"`).
3. Deduplication check: Rejects already seen domain names.
4. Schema validation: Validates source type, category mapping, and source URL reference.

Any rejected candidate is appended to `data/corpus_v2/replacement_log.jsonl` with an explicit reason, ensuring complete reproducibility of candidate filtering.
