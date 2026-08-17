---
name: recon-discovery
description: >-
  Perform advanced web reconnaissance, subdomain enumeration, DNS resolution, secret scanning, URL intelligence, and binary/malware analysis using HTTPX, Subfinder, Assetfinder, DNSX, MassDNS, URLScan, TruffleHog, YARA, Binwalk, and Hashdeep.
---

# Recon & Discovery Skill

This skill guides the use of modern security reconnaissance, DNS mapping, endpoint extraction, and binary inspection tools in Project Atlas.

## Tool Overview & Command Patterns

### 1. HTTP Probing & Tech Stack Detection
- **`httpx`**:
  ```bash
  # Probe domain list with status codes, titles, tech stack, and response times
  httpx -l domains.txt -status-code -title -tech-detect -follow-redirects -json -o httpx_results.jsonl
  ```

### 2. Subdomain & Asset Enumeration
- **`subfinder`**:
  ```bash
  # Passive subdomain enumeration
  subfinder -d example.com -silent -o subdomains.txt
  ```
- **`assetfinder`**:
  ```bash
  # Fast asset enumeration from public sources
  assetfinder --subs-only example.com >> subdomains.txt
  ```

### 3. Fast DNS Resolution
- **`dnsx`**:
  ```bash
  # Validate active resolving subdomains and extract A/CNAME records
  cat subdomains.txt | dnsx -a -cname -resp -silent
  ```
- **`massdns`**:
  ```bash
  # Ultra-high speed bulk DNS resolver
  massdns -r /etc/resolv.conf -t A -o S subdomains.txt -w resolved.txt
  ```

### 4. URL & Threat Intelligence
- **`urlscan`**:
  ```bash
  # Search urlscan.io historical scans for domain
  urlscan search "page.domain:example.com"
  ```
- **`trufflehog`**:
  ```bash
  # Scan filesystem or git repository for leaked credentials & high-entropy strings
  trufflehog filesystem /workspaces/web-anomaly/data/
  ```

### 5. Signature & Binary Analysis
- **`yara`**:
  ```bash
  # Match custom signature rules against raw web HTML or payloads
  yara rules.yar data/phase1_3_live/evidence/raw_artifacts/
  ```
- **`binwalk`**:
  ```bash
  # Inspect and extract embedded files and headers from compressed payloads
  binwalk -e payload.bin
  ```
- **`hashdeep`**:
  ```bash
  # Recursive multi-hash verification (MD5, SHA1, SHA256)
  hashdeep -r -c sha256 data/benchmark_v2/evidence/
  ```
