---
name: mcp-research-tools
description: >-
  Use Model Context Protocol (MCP) servers for live web search, library documentation lookup, filesystem access, page fetching, and browser automation. Use when the user requests Brave Search queries, Context7 documentation context, local filesystem inspection via MCP, or live page markdown fetching.
---

# MCP Research & Discovery Skill

This skill explains how the Model Context Protocol (MCP) servers configured in this suite operate and how to use them.

## Configured MCP Servers

The suite configures 5 MCP servers in `mcp_config.json`:

1. **`playwright`** (`@executeautomation/playwright-mcp-server`):
   - Real-time browser automation via MCP tools (`navigate`, `click`, `fill`, `screenshot`, etc.).
2. **`brave-search`** (`@modelcontextprotocol/server-brave-search`):
   - Web search with query parameters and optional `BRAVE_API_KEY`.
3. **`context7`** (`@upstash/context7-mcp`):
   - Documentation context and library lookup for modern SDKs and frameworks.
4. **`filesystem`** (`@modelcontextprotocol/server-filesystem`):
   - Safe workspace file reading, listing, and writing capabilities.
5. **`fetch`** (`mcp-server-fetch`):
   - Converts web pages directly into clean Markdown for AI consumption.

## Configuration Format

Configured in `~/.gemini/config/mcp_config.json` and `.agents/plugins/web-research-suite/mcp_config.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": ""
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspaces/web-anomaly"]
    },
    "fetch": {
      "command": "python3",
      "args": ["-m", "mcp_server_fetch"]
    }
  }
}
```
