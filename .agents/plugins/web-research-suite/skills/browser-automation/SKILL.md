---
name: browser-automation
description: >-
  Run browser automation tasks using Playwright, Puppeteer, CDP, Selenium, Browser-Use, or Stagehand. Use when the user asks to automate browser workflows, scrape dynamic JavaScript websites, launch headless Chromium, connect to Chrome DevTools Protocol, or run AI browser agents.
---

# Browser Automation Skill

This skill provides step-by-step guidance and execution patterns for the Browser Automation toolset.

## Available Tools

- **Playwright CLI & MCP**: Headless browser automation, testing, and screenshots.
- **Puppeteer**: Node.js library to control Chrome or Chromium over CDP.
- **Headless Chromium**: Installed via Playwright with complete system dependencies.
- **Chrome DevTools Protocol (CDP)**: `cri` CLI and `chrome-remote-interface` library.
- **Selenium**: Python `selenium` and Node `selenium-webdriver`.
- **Browser Use**: Python autonomous AI web agent framework.
- **Stagehand**: TypeScript/Node AI browser automation SDK.

## Common Workflows

### 1. Launching Headless Chromium & Taking Screenshots
```bash
playwright-screenshot "https://example.com" "screenshot.png" --full-page
```

### 2. Node.js Playwright Automation
```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://example.com');
  const title = await page.title();
  console.log('Page title:', title);
  await browser.close();
})();
```

### 3. Python AI Browser Agent (`browser-use`)
```python
from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig
import asyncio

async def main():
    browser = Browser(config=BrowserConfig(headless=True))
    agent = Agent(
        task="Navigate to https://example.com and extract header text",
        browser=browser
    )
    history = await agent.run()
    print(history)

if __name__ == '__main__':
    asyncio.run(main())
```

### 4. Node.js Stagehand AI Automation
```javascript
import { Stagehand } from '@browserbasehq/stagehand';

async function run() {
  const stagehand = new Stagehand({
    env: 'LOCAL',
    headless: true
  });
  await stagehand.init();
  await stagehand.page.goto('https://example.com');
  const result = await stagehand.page.extract({
    instruction: 'Extract the main headline and body text'
  });
  console.log(result);
  await stagehand.close();
}
run();
```

### 5. Chrome DevTools Protocol (CDP) Inspection
```bash
# List tabs / targets on running Chrome instance (e.g., port 9222)
cri list -p 9222
cri version -p 9222
```
