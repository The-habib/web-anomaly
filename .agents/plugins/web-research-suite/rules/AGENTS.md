# Web Research, Automation & Archival Suite Guidelines

This workspace is equipped with 52 Browser, Web Crawling, Recon, Parsing, Visual Diffing, Data Analytics, Archival, and Model Context Protocol (MCP) tools.

## Tool Selection & Category Reference

### 1. Browser & UI Automation
- **`playwright` / `playwright-screenshot`**: Headless browser automation, script execution, full-page screenshots.
- **`browser_use` (Python) / `@browserbasehq/stagehand` (Node)**: Autonomous LLM browser workflows.
- **`cri` (Chrome Remote Interface)**: Direct Chrome DevTools Protocol debugging.
- **`puppeteer` / `selenium`**: Regression tests and DOM capture.
- **`gowitness`**: Bulk automated web screenshot capturing.
- **`capture-website` / `pageres`**: Fast responsive page screenshot CLI.
- **`pixelmatch` / `resemblejs` / `blink-diff`**: Exact and perceptual visual regression diffing.

### 2. Web Crawling & Archival
- **`katana`**: Fast multi-threaded crawler endpoint discovery (`katana -u <url> -d 2`).
- **`gospider`**: Deep web spidering, JS parsing, and asset extraction.
- **`waybackurls` / `gau`**: Fetch all historical URLs known to Wayback, AlienVault OTX, and URLScan.
- **`httrack`**: Mirror entire websites offline.
- **`archivebox`**: Self-hosted preservation of HTML, PDFs, screenshots, and assets.
- **`crawl4ai`**: Async LLM-friendly crawler for clean Markdown/JSON extraction.
- **`warcio`**: Read, write, and validate standard WARC/WACZ archive files.
- **`cdx-toolkit` / `waybackpy` / `wayback`**: Query Internet Archive & Common Crawl CDX indices.

### 3. Reconnaissance, DNS & Security Discovery
- **`httpx`**: Fast multi-purpose HTTP prober (status, title, technology stack, CDN).
- **`subfinder` / `assetfinder`**: Passive and active subdomain discovery.
- **`dnsx` / `massdns`**: High-performance multi-threaded DNS resolver.
- **`urlscan`**: URLScan.io intelligence search and submission.
- **`trufflehog`**: Secret, API key, and credential leakage scanning across files and repos.
- **`yara`**: Signature-based pattern matching and rule evaluation.
- **`binwalk` / `hashdeep`**: Firmware/payload extraction and multi-algorithm hash auditing.

### 4. Data Analysis, Storage & Workflow Engines
- **`duckdb` (CLI + Python)**: Ultra-fast columnar SQL queries on CSV, JSONL, Parquet, and SQLite files.
- **`sqlite-utils` / `datasette`**: Turn raw JSONL into structured SQLite databases and browse via UI.
- **`tika` / `ocrmypdf`**: Document text/metadata parsing and OCR searchable PDF generation.
- **`mlr` (Miller)**: High-speed streaming transformations on JSONL and CSV data.
- **`zstd` / `parquet-tools`**: Modern compression and columnar Parquet analysis.
- **`parallel` / `just`**: Repeatable job execution and research recipe runners.

### 5. Model Context Protocol (MCP) Servers
- Declared in `.agents/plugins/web-research-suite/mcp_config.json`:
  - `playwright`: Real-time browser manipulation over MCP.
  - `brave-search`: Live web search.
  - `context7`: Library documentation and SDK reference.
  - `filesystem`: Workspace filesystem operations.
  - `fetch`: Web page to clean Markdown fetcher.
  - `github`: Repository, pull request, and issue management.
  - `memory`: Knowledge graph and persistent entity relationship storage.
  - `sequential-thinking`: Dynamic step-by-step hypothesis formulation.
  - `wigolo` & `cloak-browser`: Stealth scraping and anti-bot browser runtime.
