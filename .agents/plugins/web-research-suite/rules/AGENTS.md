# Web Research & Automation Suite Guidelines

This workspace is equipped with 40 Browser, Web Crawling, Parsing, Visual Diffing, Network Inspection, and MCP tools.

## Tool Selection Quick Reference

1. **Browser & UI Automation**:
   - Use `playwright` or `playwright-screenshot` for fast headless browser interactions and full-page screenshots.
   - Use `browser_use` (Python) or `@browserbasehq/stagehand` (Node) for LLM-driven autonomous web navigation.
   - Use `cri` (Chrome DevTools Protocol CLI) to inspect and debug running Chrome targets over CDP.
   - Use `puppeteer` or `selenium` for standard automated regression scripts.

2. **Web Crawling & Archiving**:
   - Use `katana` for fast multi-threaded crawler endpoint discovery (`katana -u <url> -d 2`).
   - Use `gospider` for deep web spidering and asset extraction.
   - Use `httrack` to mirror entire websites offline.
   - Use `cdx-toolkit` to query Common Crawl CDX indices.
   - Use `waybackpy` / `wayback` to query Internet Archive snapshots.
   - Use `warcio` to read, parse, and write WARC archive files.

3. **HTML & Content Extraction**:
   - Use `htmlq` or `pup` for command-line CSS selector queries on HTML streams.
   - Use `trafilatura` for clean main article body text and metadata extraction from web pages.
   - Use `readability` (`readabilipy`, `readability-lxml`) for clean document simplification.
   - Use `jq` / `yq` for JSON, YAML, and XML filtering.

4. **Visual Testing & Diffing**:
   - Use `playwright-screenshot <url> <out.png> [--full-page]` or `pageres <url> <res>` or `capture-website <url> <out.png>`.
   - Use `pixelmatch <img1.png> <img2.png> <diff.png>` for exact pixel diffing.
   - Use `resemblejs <img1.png> <img2.png> <diff.png>` for perceptual image analysis.
   - Use `blink-diff --image-a <img1.png> --image-b <img2.png> --image-output <diff.png>`.

5. **Network Inspection & Diagnostics**:
   - Use `httpstat <url>` for visual latency breakdowns (DNS, TCP, TLS, TTFB, transfer).
   - Use `http` / `https` (HTTPie) or `curlie` for interactive and formatted HTTP requests.
   - Use `mitmproxy` / `mitmdump` for intercepting, inspecting, and modifying HTTP/HTTPS traffic.
   - Use `websocat` to interact with WebSocket endpoints.
   - Use `tcpdump` for packet capture.

6. **MCP Servers**:
   - MCP servers are declared in `mcp_config.json` (`playwright`, `brave-search`, `context7`, `filesystem`, `fetch`).
