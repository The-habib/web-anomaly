---
name: mcp-research-tools
description: >-
  Use Model Context Protocol (MCP) servers for live web search, library documentation lookup, filesystem access, page fetching, browser automation, GitHub repository interaction, structured knowledge graphs, sequential thinking, and stealth web exploration.
---

# MCP Research & Discovery Skill

This skill explains how the Model Context Protocol (MCP) servers configured in this suite operate and how to use them.

## Configured MCP Servers

The suite configures MCP servers in `.agents/plugins/web-research-suite/mcp_config.json`:

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
6. **`github`** (`@modelcontextprotocol/server-github`):
   - Search repositories, inspect pull requests, read issues, and manage commits over MCP.
7. **`memory`** (`@modelcontextprotocol/server-memory`):
   - Persistent graph-based memory and relation tracker across research steps.
8. **`sequential-thinking`** (`@modelcontextprotocol/server-sequential-thinking`):
   - Dynamic step-by-step reasoning and hypothesis revision engine.
9. **`wigolo` & `cloak-browser`**:
   - Stealth scraping runtime and headless browser environment.

## Configuration Manifest

Configured in `.agents/plugins/web-research-suite/mcp_config.json`:

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
      "env": { "BRAVE_API_KEY": "" }
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
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "" }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```
