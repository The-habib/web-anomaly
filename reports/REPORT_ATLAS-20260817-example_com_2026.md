# Research Finding Report: ATLAS-20260817-example_com_2026

**Project Atlas — Autonomous Web Anomaly Laboratory**  
*Mission Finding Classification & Evidence Dossier*

---

## 1. Executive Summary

| Parameter | Value |
| :--- | :--- |
| **Finding ID** | `ATLAS-20260817-example_com_2026` |
| **Target URL** | [https://example.com](https://example.com) |
| **Canonical Domain** | `example.com` |
| **Investigation Timestamp** | `2026-08-17T18:52:22.611840Z` |
| **Anomaly Score** | **`7`** |
| **Classification** | **Tier-2 Significant Historical Anomaly** |

### Human Analysis
Target https://example.com analyzed with Anomaly Score 7 (Tier-2 Significant Historical Anomaly). Observed 2 anomaly signals across a 24-year historical timeline.

---

## 2. Detected Anomaly Signals

| Signal | Category | Weight | Evidence Description |
| :--- | :--- | :--- | :--- |
| **15+ Year Web Persistence** | `temporal` | +2 | First recorded in 2002 (24 years continuous lifespan). |
| **Domain / URL Resurrection** | `temporal` | +5 | Disappeared and subsequently returned: Gap between 2004 (status 200) and 2018 (status 200). |

---

## 3. Visual Evidence

![Target Screenshot](../evidence/screenshots/example_com_20260817_185136_screenshot.png)

---

## 4. Temporal Analysis & Timeline


- **First Recorded Snapshot**: `20020120142510` (`2002-01-20T14:25:10Z`)
- **Latest Recorded Snapshot**: `20260817185222` (`2026-08-17T18:52:22.611840Z`)
- **Calculated Lifespan**: `24 years`
- **Total Historical Observations**: `757`


---

## 5. Technical Metadata


- **Document Title**: Example Domain
- **HTML Generator / CMS**: ``
- **Outbound Links Count**: 1
- **External Scripts Count**: 0
- **Images Count**: 0


---

## 6. Permanent Evidence Artifacts

| Type | File Name | SHA-256 Digest | Size |
| :--- | :--- | :--- | :--- |
| `screenshot` | `example_com_20260817_185136_screenshot.png` | `04b93c1a2c020127...` | 19,288 bytes |
| `html` | `example_com_20260817_185136_rendered.html` | `ff67a9d764d6a236...` | 559 bytes |
| `metadata` | `example_com_20260817_185136_metadata.json` | `ef0482a20a455871...` | 541 bytes |
| `timeline` | `example_com_20260817_185136_timeline.json` | `e6164d19402efac9...` | 355,513 bytes |
| `json` | `example_com_20260817_185136_evidence.json` | `7b983aa7841dfd31...` | 4,414 bytes |

---

## 7. Machine Summary (JSON)

```json
{
  "finding_id": "ATLAS-20260817-example_com_2026",
  "target_url": "https://example.com",
  "canonical_domain": "example.com",
  "timestamp": "2026-08-17T18:52:22.611840Z",
  "anomaly_score": 7,
  "classification": "Tier-2 Significant Historical Anomaly",
  "signals": [
    {
      "signal_id": "persistence_15yr",
      "name": "15+ Year Web Persistence",
      "category": "temporal",
      "weight": 2,
      "score_awarded": 2,
      "description": "First recorded in 2002 (24 years continuous lifespan).",
      "evidence_keys": [
        "timeline_first_seen",
        "timeline_span_years"
      ],
      "confidence": 1.0
    },
    {
      "signal_id": "resurrection",
      "name": "Domain / URL Resurrection",
      "category": "temporal",
      "weight": 5,
      "score_awarded": 5,
      "description": "Disappeared and subsequently returned: Gap between 2004 (status 200) and 2018 (status 200).",
      "evidence_keys": [
        "timeline_gaps",
        "resurrection_interval"
      ],
      "confidence": 1.0
    }
  ],
  "timeline_analysis": {
    "total_events": 757,
    "first_seen": "20020120142510",
    "last_seen": "20260817185222",
    "earliest_iso": "2002-01-20T14:25:10Z",
    "latest_iso": "2026-08-17T18:52:22.611840Z",
    "span_years": 24,
    "gaps_detected": []
  },
  "metadata": {
    "title": "Example Domain",
    "generator": "",
    "description": "",
    "links_count": 1,
    "scripts_count": 0,
    "images_count": 0,
    "doctype": "",
    "headers": {
      "Date": "Mon, 17 Aug 2026 18:51:37 GMT",
      "Content-Type": "text/html",
      "Transfer-Encoding": "chunked",
      "Connection": "keep-alive",
      "Server": "cloudflare",
      "last-modified": "Wed, 12 Aug 2026 20:15:57 GMT",
      "allow": "GET, HEAD",
      "Age": "5551",
      "cf-cache-status": "HIT",
      "Content-Encoding": "br",
      "CF-RAY": "a2cadf077beea6ad-BOM"
    }
  },
  "artifacts": [
    {
      "artifact_id": "art_ss_example_com_20260817_185136",
      "artifact_type": "screenshot",
      "relative_path": "evidence/screenshots/example_com_20260817_185136_screenshot.png",
      "file_name": "example_com_20260817_185136_screenshot.png",
      "sha256": "04b93c1a2c020127fd125f3ce179b53259c160b7b24917d3e88e8991c2f5f09f",
      "size_bytes": 19288,
      "created_at": "2026-08-17T18:51:37.401251+00:00",
      "metadata": {
        "url": "https://example.com",
        "viewport": {
          "width": 1280,
          "height": 800
        }
      }
    },
    {
      "artifact_id": "art_html_example_com_20260817_185136",
      "artifact_type": "html",
      "relative_path": "evidence/html/example_com_20260817_185136_rendered.html",
      "file_name": "example_com_20260817_185136_rendered.html",
      "sha256": "ff67a9d764d6a2367a187734e697f6a53217db9a21c101d410a113ca871a299d",
      "size_bytes": 559,
      "created_at": "2026-08-17T18:51:37.470999+00:00",
      "metadata": {
        "status_code": 200,
        "final_url": "https://example.com/"
      }
    },
    {
      "artifact_id": "art_meta_example_com_20260817_185136",
      "artifact_type": "metadata",
      "relative_path": "evidence/metadata/example_com_20260817_185136_metadata.json",
      "file_name": "example_com_20260817_185136_metadata.json",
      "sha256": "ef0482a20a455871986b631dd3f07c6a4d1c1e09a4678a7b0238c10435741360",
      "size_bytes": 541,
      "created_at": "2026-08-17T18:51:37.600063+00:00",
      "metadata": {
        "fields_extracted": [
          "title",
          "generator",
          "description",
          "links_count",
          "scripts_count",
          "images_count",
          "doctype",
          "headers"
        ]
      }
    },
    {
      "artifact_id": "art_tl_example_com_20260817_185136",
      "artifact_type": "timeline",
      "relative_path": "evidence/timeline/example_com_20260817_185136_timeline.json",
      "file_name": "example_com_20260817_185136_timeline.json",
      "sha256": "e6164d19402efac95bc09a652d10ec5632839b470528e24cb68397d6692deeee",
      "size_bytes": 355513,
      "created_at": "2026-08-17T18:52:22.622944+00:00",
      "metadata": {
        "total_events": 757,
        "first_seen": "20020120142510",
        "last_seen": "20260817185222",
        "earliest_iso": "2002-01-20T14:25:10Z",
        "latest_iso": "2026-08-17T18:52:22.611840Z",
        "span_years": 24,
        "gaps_detected": []
      }
    }
  ]
}
```

---

## 8. Reproducibility

To re-run this exact investigation and reproduce the evidence chain:
```bash
python3 scripts/run_pipeline.py https://example.com
```
