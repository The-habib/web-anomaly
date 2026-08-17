# Project Atlas — Corpus Policy & Provenance Standards (Corpus v2)

## 1. Zero Synthetic Data Policy
Production research corpora in Project Atlas must satisfy:
$$\text{synthetic\_domains} = 0$$

Under no circumstance may synthetic domain names, procedural pattern expansions (`univ-001.edu`, `corp-001.com`, etc.), placeholder entries (`example.com`), or unverified fabricated hostnames be included in any discovery or benchmark corpus. If an authentic public source cannot establish the real-world existence of an entity, that candidate is rejected.

---

## 2. Real Domain Definition
A domain qualifies as **REAL** when:
1. At least one authoritative, trustworthy public source establishes that the domain represents an active or historical organization, institution, open-source project, public service, or documented independent website.
2. The domain is registered with an ICANN-accredited TLD or authorized public top-level registry.
3. The domain has documented provenance verifiable via institutional directories, government registries, open-source repositories, or scholarly archives.

---

## 3. Subdomain and Host Entity Policy
1. **Root Domains vs Subdomains**:
   - Institutional and organizational root domains (`harvard.edu`, `nasa.gov`, `debian.org`) represent the primary research unit for that organization.
   - Distinct, independently operated sub-projects with dedicated web infrastructures (e.g. `httpd.apache.org`, `ccny.cuny.edu`, `subversion.apache.org`) are treated as distinct research units provided they possess separate governance or independent architectural history.
   - Generic organizational aliases (e.g. `www.domain.com`) are normalized to their canonical hostname (`domain.com`).
2. **User Directory Pages**:
   - Individual user path pages (e.g. `cmu.edu/~username` or `tilde.town/~user`) remain within the parent host entity and are not separate domain records in the seed corpus.

---

## 4. Rejection Taxonomy
When a candidate fails validation, it must be recorded in `replacement_log.jsonl` with an explicit standardized rejection code:
- `SYNTHETIC_PATTERN`: Identified procedural pattern or placeholder name.
- `INVALID_DOMAIN`: Malformed hostname or missing valid TLD.
- `DNS_FAILURE`: Inability to resolve or non-existent domain record.
- `SOURCE_UNVERIFIED`: Lacks reputable third-party public citation.
- `CATEGORY_UNCERTAIN`: Ambiguous classification across research categories.
- `DUPLICATE`: Domain already present in candidate pool.
- `REDIRECT_ONLY`: Trivial alias redirecting to an existing entity.
- `PARKED_DOMAIN`: Domain monetization or commercial parked page.
- `DOMAIN_FOR_SALE`: Expired domain listing.
- `PRIVATE_SERVICE`: Non-public intranet or private authenticated portal.
- `TEST_DOMAIN`: Test fixture or temporary development endpoint.
- `INSUFFICIENT_PROVENANCE`: Missing required provenance metadata fields.
- `DISALLOWED_TARGET`: Excluded by ethical or safety policies.

---

## 5. Category Definitions
1. **Universities**: Accredited higher education institutions and academic degree-granting universities.
2. **Government**: National, federal, state/provincial, and municipal governmental bodies, ministries, and statutory public agencies.
3. **Nonprofits**: Registered non-governmental organizations (NGOs), philanthropic foundations, public libraries, museums, scientific societies, and internet standards organizations.
4. **Long-Running Companies**: Commercial corporate enterprises with established operational or industrial history.
5. **Open-Source / Project Sites**: Public open-source software projects, operating systems, toolchains, and collaborative developer platforms.
6. **Personal / Independent Sites**: Genuinely public independent personal sites, tilde communities, early-web archives, and non-commercial handcrafted digital spaces.

---

## 6. Deterministic Sampling Protocol
- Sampling occurs strictly **AFTER** candidate verification, duplicate removal, and provenance validation.
- All sampling operations use `random.Random(42)` on sorted candidate lists to ensure cross-platform reproducibility.
- If a validated category pool has fewer entries than its target quota, the corpus retains all verified items and reports the exact count without synthetic padding.
