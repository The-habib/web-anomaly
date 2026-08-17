---
name: data-analysis-archiving
description: >-
  Query large datasets with DuckDB, manage SQLite databases with sqlite-utils/Datasette, preserve deep snapshots with ArchiveBox, run LLM-friendly crawls with Crawl4AI, extract text with Tika/OCRmyPDF, manipulate structured data with Miller, and execute repeatable workflows with just and GNU Parallel.
---

# Data Analysis & Archival Engineering Skill

This skill explains how to analyze large web datasets, manage local archives, and run high-performance columnar queries in Project Atlas.

## Core Engines & Usage

### 1. Columnar Web Analytics with DuckDB
- **CLI Querying**:
  ```bash
  # Query CSV, JSONL, or Parquet datasets directly without database loading
  duckdb -c "SELECT classification, count(*), avg(raw_anomaly_score) FROM 'data/phase1_3_live/pilot_scores.jsonl' GROUP BY classification;"
  ```
- **Python Integration**:
  ```python
  import duckdb
  df = duckdb.query("SELECT * FROM 'data/benchmark_v2/predictions.jsonl' WHERE raw_anomaly_score > 40").df()
  ```

### 2. Relational Evidence Management (sqlite-utils & Datasette)
- **`sqlite-utils`**:
  ```bash
  # Ingest JSONL evidence into an SQLite database
  sqlite-utils insert evidence.db evidence data/phase1_3_live/pilot_evidence.jsonl --nl
  sqlite-utils tables evidence.db --counts
  ```
- **`datasette`**:
  ```bash
  # Browse evidence database interactively
  datasette evidence.db -p 8001
  ```

### 3. Local Web Archival with ArchiveBox
- **Deep URL Preservation**:
  ```bash
  # Save HTML, screenshots, PDFs, and media into structured archive
  archivebox add "https://toastytech.com"
  archivebox list
  ```

### 4. LLM Crawling & Extraction with Crawl4AI
- **Python Async Extraction**:
  ```python
  import asyncio
  from crawl4ai import AsyncWebCrawler

  async def crawl():
      async with AsyncWebCrawler() as crawler:
          result = await crawler.arun(url="https://stallman.org")
          print(result.markdown[:500])

  asyncio.run(crawl())
  ```

### 5. Document & Metadata Extraction (Tika & OCRmyPDF)
- **`tika`**: Extract text and metadata from PDF, DOCX, audio/video streams.
- **`ocrmypdf`**:
  ```bash
  ocrmypdf input_scanned.pdf output_searchable.pdf
  ```

### 6. Streaming Data Wrangling with Miller (`mlr`)
- **Fast Column Operations on JSONL/CSV**:
  ```bash
  mlr --jsonl filter '$raw_anomaly_score >= 40' then count-by classification data/benchmark_v2/predictions.jsonl
  ```

### 7. Workflow Automation (`just` & GNU Parallel)
- **Repeatable Workflows via `justfile`**:
  ```bash
  just audit
  just release-check
  ```
- **GNU Parallel**:
  ```bash
  cat domains.txt | parallel -j 10 "katana -u https://{} -silent -d 1"
  ```
