---
name: web-crawling
description: >-
  Crawl, spider, archive, and query historical web archives using Katana, GoSpider, HTTrack, WARC, Common Crawl, or Wayback Machine. Use when the user asks to crawl a website, extract endpoints, mirror a site, query historical snapshots, or inspect WARC records.
---

# Web Crawling Skill

This skill provides step-by-step guidance and commands for web crawling, spidering, and archive retrieval.

## Available Tools

- **Katana**: ProjectDiscovery fast web crawler for endpoint discovery.
- **GoSpider**: Fast Go-based web spider for deep site asset discovery.
- **HTTrack**: Offline website mirror and crawler.
- **Wayback / Waybackpy**: Internet Archive Wayback Machine Python library and CLI.
- **Warcio**: WARC (Web ARChive) file reader, writer, and indexer.
- **Common Crawl Toolkit (`cdx-toolkit`)**: Query Common Crawl CDX indices.
- **wget / curl**: Standard download and scraping tools.

## Common Workflows

### 1. Fast Crawl and Endpoint Discovery with Katana
```bash
# Crawl up to depth 2 silently
katana -u "https://example.com" -d 2 -silent -o endpoints.txt

# Crawl with headless browser mode for JS-rendered apps
katana -u "https://example.com" -headless -d 2
```

### 2. Deep Spidering with GoSpider
```bash
gospider -s "https://example.com" -o crawl_output -c 10 -d 1 --other-source
```

### 3. Mirroring Websites with HTTrack
```bash
# Mirror a website offline into ./mirror directory
httrack "https://example.com" -O "./mirror" "+*.example.com/*" -v
```

### 4. Querying Wayback Machine
```bash
# Fetch newest snapshot URL via waybackpy CLI
waybackpy --url "https://example.com" --newest

# Using Python wayback library
python3 -c "
import wayback
client = wayback.WaybackClient()
for record in client.search('https://example.com'):
    print(record.timestamp, record.view_url)
    break
"
```

### 5. Common Crawl Index Querying
```bash
# Query recent captures for a domain
cdx-toolkit iter --cc --crawl 2026-04 --limit 10 "example.com/*"
```

### 6. WARC File Operations
```bash
# Index a WARC archive file
warcio index sample.warc.gz

# Extract records with Python
python3 -c "
from warcio.archiveiterator import ArchiveIterator
with open('sample.warc.gz', 'rb') as stream:
    for record in ArchiveIterator(stream):
        if record.rec_type == 'response':
            print(record.rec_headers.get_header('WARC-Target-URI'))
"
```
