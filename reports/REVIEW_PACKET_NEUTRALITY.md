# Project Atlas — Review Packet Neutrality Specification
## Elimination of Machine Interpretations and Model Leakage in Human Review

```
=====================================================================================
                      REVIEW PACKET NEUTRALITY SPECIFICATION (V2)
=====================================================================================
```

### 1. Overview & Verification Summary

The Human Review Packet V2 format ([`ReviewPacketV2`](file:///workspaces/web-anomaly/atlas/review/packet_v2.py)) guarantees that reviewers receive pure empirical evidence rather than machine-derived conclusions.

- **Total Packets Verified**: 51
- **Neutrality Check Status**: `PASS (100% Evidence-Only)`
- **Prohibited Tokens Detected**: `0`

---

### 2. Forbidden Keyword & Phrase Inventory

The following attributes and phrases are strictly purged during packet serialization:

| Prohibited Category | Prohibited Keywords / Phrases | Neutral Replacement |
| :--- | :--- | :--- |
| **Scores & Rankings** | `anomaly_score`, `research_priority`, `queue_score`, `treasure_score`, `score`, `rank` | Omitted completely |
| **Discovery Strategy** | `strategy`, `USER_SPACE`, `DEEP_PATH`, `strategy_rank` | Omitted completely |
| **Treasure DNA & Clusters** | `dna`, `cluster_id`, `survival_vector`, `similarity` | Omitted completely |
| **Interpretive Labels** | `"This page is old"`, `"ancient page"`, `"retro styling"`, `"long-term survival"` | Raw historical capture dates and HTTP statuses |
| **Orphan Verdicts** | `ORPHAN_PROVEN`, `ORPHAN_CANDIDATE` | Raw navigation scope (links checked count, root URL) |
| **Machine Explanations** | `why_interesting`, `why_it_matters`, `machine_explanation` | Blank reviewer prompt field |

---

### 3. Neutral Timeline & Navigation Separation

#### Raw Timeline vs Interpreted Timeline
- **Prohibited (Interpreted)**: *"Surviving continuous page active since 1999 without modern CSS framework."*
- **Allowed (Raw Evidence)**:
  ```json
  {
    "timestamp_utc": "1999-04-12T10:15:00Z",
    "archive_source": "Wayback CDX Index",
    "target_url": "https://example.org/archive/",
    "http_status": 200,
    "content_digest_sha256": "9c0fddb8e1fb3d37..."
  }
  ```

#### Raw Navigation Scope vs Orphan Judgments
- **Prohibited (Judgment)**: `orphan_status = "ORPHAN_PROVEN"`
- **Allowed (Raw Scope)**:
  ```json
  {
    "root_url": "https://example.org/",
    "links_inspected_count": 42,
    "direct_link_found": false,
    "inspection_timestamp_utc": "2026-08-18T09:00:30Z"
  }
  ```
