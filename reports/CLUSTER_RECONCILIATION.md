# Project Atlas — Cluster Reconciliation Report
## Archaeological Site Hierarchy & Exhibit Collapsing Specification

```
=====================================================================================
                      CLUSTER RECONCILIATION & SITE COLLAPSING
=====================================================================================
```

### 1. The Domain Cluster Proliferation Problem

In blind discovery runs, single highly-structured historical domains (such as `cosmic.voyage` or `theoldnet.com`) may generate dozens of candidate subpages (e.g., `/Accipiter/...`, `/0dev Outpost/...`, `/docs/...`).

Treating every individual candidate URL on the same domain as a distinct museum treasure creates artificial exhibit inflation and distorts portfolio diversity.

---

### 2. The SiteCluster Hierarchical Architecture

Project Atlas resolves this through a 3-tier hierarchical structure:

```
DOMAIN (e.g., cosmic.voyage)
  └── ARCHAEOLOGICAL_CLUSTER (e.g., VINTAGE_WEB_COMMUNITIES)
        └── SITE_CLUSTER (SITE-cosmic-voyage)
              ├── Candidate URL 1 (/0dev Outpost/akerresponse.html)
              ├── Candidate URL 2 (/Accipiter/000_distress_relay.html)
              └── Candidate URL 3 (/Accipiter/001_decompression.html)
```

---

### 3. Collapsing Policy & Multi-Candidate Sites in Run #003

| Site Domain | Candidate URLs | Cluster Archetype | Collapsing Policy |
| :--- | :--- | :--- | :--- |
| `cosmic.voyage` | 13 | Vintage Web Communities & Fiction Archives | `COLLAPSE_TO_SINGLE_EXHIBIT_UNLESS_INDEPENDENT` |
| `daringfireball.net` | 5 | Independent Open-Source Software Sites | `COLLAPSE_TO_SINGLE_EXHIBIT_UNLESS_INDEPENDENT` |
| `theoldnet.com` | 5 | Vintage Web Communities & Fiction Archives | `COLLAPSE_TO_SINGLE_EXHIBIT_UNLESS_INDEPENDENT` |
| `tn.gov` | 18 | Historical Government Archive Repositories | `COLLAPSE_TO_SINGLE_EXHIBIT_UNLESS_INDEPENDENT` |
| `oklahoma.gov` | 14 | Historical Government Archive Repositories | `COLLAPSE_TO_SINGLE_EXHIBIT_UNLESS_INDEPENDENT` |

---

### 4. Promotion Rule

- **Default Behavior**: When human reviewers validate multiple subpages within a single `SiteCluster`, the museum curator automatically compiles them into **ONE unified platform exhibit** with deep links to the subpage artifacts.
- **Exception**: An independent sub-exhibit is permitted only if the subpage represents a distinct author space (e.g., individual Unix user directories on tilde servers: `~userA` vs `~userB`).
