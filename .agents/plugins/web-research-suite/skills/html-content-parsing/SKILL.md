---
name: html-content-parsing
description: >-
  Parse HTML, XML, YAML, and JSON content and extract main text or structured data using htmlq, pup, jq, yq, BeautifulSoup, lxml, Readability, or Trafilatura. Use when the user asks to extract specific elements from HTML, extract readable article text, parse complex XML/YAML documents, or process scraping pipelines.
---

# HTML & Content Parsing Skill

This skill provides patterns for extracting and transforming HTML, XML, JSON, and web content.

## Available Tools

- **htmlq**: Fast CLI CSS selector tool for HTML (like `jq` for HTML).
- **pup**: CLI HTML parser using CSS selectors and attribute formatting.
- **jq**: Command-line JSON processor.
- **yq**: Command-line YAML, JSON, and XML processor.
- **BeautifulSoup4**: Python HTML/XML parser.
- **lxml**: Fast, high-performance Python XML and HTML processing library.
- **Readability**: Content cleanup and readability parsing (`readabilipy`, `readability-lxml`).
- **Trafilatura**: State-of-the-art Python web text extractor and metadata scraper.

## Common Workflows

### 1. Extracting Elements with `htmlq`
```bash
# Extract text of all headings
curl -s "https://example.com" | htmlq 'h1, h2, h3' --text

# Extract attributes (e.g., all image sources)
curl -s "https://example.com" | htmlq 'img' --attribute src
```

### 2. Extracting Attributes with `pup`
```bash
# Extract hrefs as JSON
curl -s "https://example.com" | pup 'a json{}'

# Extract text of specific container
curl -s "https://example.com" | pup 'div.content text{}'
```

### 3. Extracting Clean Article Content with `trafilatura`
```bash
# CLI direct URL extraction
trafilatura -u "https://example.com"

# Python usage with metadata
python3 -c "
import trafilatura
downloaded = trafilatura.fetch_url('https://example.com')
result = trafilatura.extract(downloaded, include_links=True, include_images=True, output_format='json')
print(result)
"
```

### 4. Readability Simplification in Python
```python
from readability import Document
import urllib.request

html = urllib.request.urlopen("https://example.com").read()
doc = Document(html)
print("Title:", doc.title())
print("Summary HTML:", doc.summary())
```

### 5. YAML/JSON Processing with `yq` and `jq`
```bash
# Convert YAML to JSON
yq -p yaml -o json config.yaml

# Extract specific nested fields
yq '.database.connection.host' config.yaml
```
