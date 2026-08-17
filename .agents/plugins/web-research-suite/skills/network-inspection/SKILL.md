---
name: network-inspection
description: >-
  Inspect, intercept, debug, and diagnose HTTP/HTTPS, WebSockets, and network packets using HTTPie, mitmproxy, tcpdump, websocat, curlie, or httpstat. Use when the user asks to analyze network latency, capture packets, intercept proxy traffic, debug WebSocket connections, or inspect API headers.
---

# Network & HTTP Inspection Skill

This skill provides step-by-step guidance for testing HTTP APIs, measuring connection latency, intercepting proxy flows, and debugging network streams.

## Available Tools

- **HTTPie (`http`, `https`)**: Human-friendly HTTP CLI client with formatted JSON output.
- **mitmproxy (`mitmproxy`, `mitmdump`, `mitmweb`)**: Interactive TLS-capable intercepting HTTP proxy.
- **tcpdump**: Command-line packet analyzer.
- **websocat**: CLI tool to connect to, send, and receive WebSocket frames.
- **curlie**: The ease of use of HTTPie combined with the speed and power of curl.
- **httpstat**: Visualizes curl statistics into a terminal waterfall (DNS, TCP, TLS, TTFB, transfer).

## Common Workflows

### 1. Visualizing Request Latency with `httpstat`
```bash
httpstat "https://example.com"
```

### 2. Formatted API Testing with `http` / `https`
```bash
# JSON POST request with headers and auth
http POST "https://httpbin.org/post" \
  Authorization:"Bearer mytoken" \
  name="Alice" \
  role="Engineer"

# Downloading files with resumed transfer
http --download "https://example.com/largefile.zip"
```

### 3. Intercepting & Modifying Traffic with `mitmproxy`
```bash
# Run headless mitmdump saving flows to a file
mitmdump -p 8080 -w flows.mitm

# Start mitmweb UI on port 8081 with proxy on port 8080
mitmweb --web-port 8081 -p 8080
```

### 4. Interactive WebSocket Debugging with `websocat`
```bash
# Connect to a WebSocket server and pipe stdin/stdout
websocat "wss://echo.websocket.events"

# Listen on a local WebSocket port and echo incoming messages
websocat -s 9001
```

### 5. Fast Network Packet Inspection with `tcpdump`
```bash
# Capture 10 packets on port 80 or 443
sudo tcpdump -i any -c 10 "port 80 or port 443" -n
```
