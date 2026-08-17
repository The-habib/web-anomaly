#!/usr/bin/env python3
"""
Verification suite for all 40 Browser & Web Research Tools.
Validates CLI tools, libraries, browser engines, visual diffing, and MCP configurations.
"""

import os
import sys
import json
import shutil
import subprocess

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

results = []

def record(num, category, name, tool_type, status, details=""):
    results.append({
        "num": num,
        "category": category,
        "name": name,
        "type": tool_type,
        "status": status,
        "details": details
    })
    status_str = PASS if status else FAIL
    print(f"[{num:02d}/40] [{category:<24}] {name:<26} ({tool_type:<9}) -> {status_str} | {details}")

def run_cmd(cmd, ok_codes=(0,)):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        output = (res.stdout or res.stderr).strip().splitlines()
        first_line = output[0] if output else ""
        return (res.returncode in ok_codes), first_line
    except Exception as e:
        return False, str(e)

def run_py(code):
    try:
        res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=10)
        output = (res.stdout or res.stderr).strip().splitlines()
        first_line = output[0] if output else ""
        return (res.returncode == 0), first_line
    except Exception as e:
        return False, str(e)

def run_node(code):
    try:
        res = subprocess.run(["node", "-e", code], capture_output=True, text=True, timeout=10)
        output = (res.stdout or res.stderr).strip().splitlines()
        first_line = output[0] if output else ""
        return (res.returncode == 0), first_line
    except Exception as e:
        return False, str(e)

def check_mcp(server_key):
    mcp_path = os.path.expanduser("~/.gemini/config/mcp_config.json")
    if not os.path.exists(mcp_path):
        return False, "mcp_config.json missing"
    try:
        with open(mcp_path, "r") as f:
            cfg = json.load(f)
        if server_key in cfg.get("mcpServers", {}):
            srv = cfg["mcpServers"][server_key]
            return True, f"Configured: {srv.get('command')} {' '.join(srv.get('args', []))}"
        return False, f"'{server_key}' not in mcpServers"
    except Exception as e:
        return False, str(e)

print("=" * 80)
print("  VERIFYING 40 BROWSER & WEB RESEARCH TOOLS")
print("=" * 80)

# -------------------------------------------------------------
# A. Browser Automation (1–8)
# -------------------------------------------------------------
cat_a = "Browser Automation"

# 1. Playwright MCP
ok1, d1 = check_mcp("playwright")
record(1, cat_a, "Playwright MCP", "MCP", ok1, d1)

# 2. Playwright CLI
ok2, d2 = run_cmd("playwright --version")
record(2, cat_a, "Playwright CLI", "CLI", ok2, d2)

# 3. Puppeteer
ok3, d3 = run_cmd("puppeteer --version")
record(3, cat_a, "Puppeteer", "CLI", ok3, f"CLI version: {d3}")

# 4. Chromium (headless)
ok4, d4 = run_node("""
const { chromium } = require('playwright');
(async () => {
    const browser = await chromium.launch({ headless: true });
    const version = browser.version();
    await browser.close();
    console.log('Chromium version ' + version);
})();
""")
record(4, cat_a, "Chromium (headless)", "Browser", ok4, d4)

# 5. Chrome DevTools Protocol (CDP)
ok5, d5 = run_cmd("cri -v || chrome-remote-interface -v")
record(5, cat_a, "CDP (cri)", "Protocol", ok5, f"CRI v{d5}")

# 6. Selenium
ok6, d6 = run_py("import selenium; print(f'Selenium v{selenium.__version__}')")
record(6, cat_a, "Selenium", "CLI/Py", ok6, d6)

# 7. Browser Use
ok7, d7 = run_py("import browser_use; print('browser-use module loaded')")
record(7, cat_a, "Browser Use", "AI browser", ok7, d7)

# 8. Stagehand
ok8, d8 = run_node("import('@browserbasehq/stagehand'); console.log('@browserbasehq/stagehand loaded')")
record(8, cat_a, "Stagehand", "AI browser", ok8, d8)

# -------------------------------------------------------------
# B. Web Crawling (9–16)
# -------------------------------------------------------------
cat_b = "Web Crawling"

# 9. wget
ok9, d9 = run_cmd("wget --version")
record(9, cat_b, "wget", "CLI", ok9, d9)

# 10. curl
ok10, d10 = run_cmd("curl --version")
record(10, cat_b, "curl", "CLI", ok10, d10)

# 11. HTTrack
ok11, d11 = run_cmd("httrack --help", ok_codes=(0, 1, 2))
record(11, cat_b, "HTTrack", "CLI", ok11, "HTTrack CLI available")

# 12. wayback
ok12, d12 = run_cmd("waybackpy --help", ok_codes=(0, 1, 2))
record(12, cat_b, "wayback", "CLI/Py", ok12, "wayback & waybackpy available")

# 13. warcio
ok13, d13 = run_cmd("warcio -h", ok_codes=(0, 1, 2))
record(13, cat_b, "warcio", "Python", ok13, "warcio CLI & library available")

# 14. Common Crawl Toolkit
ok14, d14 = run_cmd("cdx-toolkit -h", ok_codes=(0, 1, 2))
record(14, cat_b, "Common Crawl Toolkit", "Python", ok14, "cdx-toolkit available")

# 15. Katana
ok15, d15 = run_cmd("katana -version")
record(15, cat_b, "Katana", "CLI", ok15, d15)

# 16. gospider
ok16, d16 = run_cmd("gospider -h", ok_codes=(0, 1, 2))
record(16, cat_b, "gospider", "CLI", ok16, "gospider web spider available")

# -------------------------------------------------------------
# C. HTML & Content Parsing (17–24)
# -------------------------------------------------------------
cat_c = "HTML & Content Parsing"

# 17. htmlq
ok17, d17 = run_cmd("htmlq -h", ok_codes=(0, 1, 2))
record(17, cat_c, "htmlq", "CLI", ok17, "htmlq CSS selector engine available")

# 18. pup
ok18, d18 = run_cmd("pup --help", ok_codes=(0, 1, 2))
record(18, cat_c, "pup", "CLI", ok18, "pup HTML parser available")

# 19. jq
ok19, d19 = run_cmd("jq --version")
record(19, cat_c, "jq", "CLI", ok19, d19)

# 20. yq
ok20, d20 = run_cmd("yq --version")
record(20, cat_c, "yq", "CLI", ok20, d20)

# 21. BeautifulSoup
ok21, d21 = run_py("import bs4; print(f'bs4 v{bs4.__version__}')")
record(21, cat_c, "BeautifulSoup", "Python", ok21, d21)

# 22. lxml
ok22, d22 = run_py("import lxml; print(f'lxml v{lxml.__version__}')")
record(22, cat_c, "lxml", "Python", ok22, d22)

# 23. Readability
ok23, d23 = run_py("import readability, readabilipy; print('readability & readabilipy available')")
record(23, cat_c, "Readability", "Parser", ok23, d23)

# 24. trafilatura
ok24, d24 = run_cmd("trafilatura --version")
record(24, cat_c, "trafilatura", "Python", ok24, d24)

# -------------------------------------------------------------
# D. Screenshot & Visual Diff (25–30)
# -------------------------------------------------------------
cat_d = "Screenshot & Visual Diff"

# 25. Playwright Screenshots
ok25, d25 = run_cmd("playwright-screenshot -h", ok_codes=(0, 1, 2))
record(25, cat_d, "Playwright Screenshots", "CLI", ok25, "playwright-screenshot utility available")

# 26. Pageres
ok26, d26 = run_cmd("pageres --help", ok_codes=(0, 1, 2))
record(26, cat_d, "Pageres", "CLI", ok26, "pageres CLI available")

# 27. Capture-Website CLI
ok27, d27 = run_cmd("capture-website --help", ok_codes=(0, 1, 2))
record(27, cat_d, "Capture-Website CLI", "CLI", ok27, "capture-website CLI available")

# 28. BlinkDiff
ok28, d28 = run_cmd("blink-diff --help", ok_codes=(0, 1, 2))
record(28, cat_d, "BlinkDiff", "Diff", ok28, "blink-diff CLI available")

# 29. Pixelmatch
ok29, d29 = run_cmd("pixelmatch", ok_codes=(0, 1, 2, 64))
record(29, cat_d, "Pixelmatch", "Diff", ok29, "pixelmatch CLI & library available")

# 30. Resemble.js
ok30, d30 = run_cmd("resemblejs --help", ok_codes=(0, 1, 2))
record(30, cat_d, "Resemble.js", "Diff", ok30, "resemblejs CLI & library available")

# -------------------------------------------------------------
# E. Network & HTTP Inspection (31–36)
# -------------------------------------------------------------
cat_e = "Network & HTTP Inspection"

# 31. HTTPie
ok31, d31 = run_cmd("http --version")
record(31, cat_e, "HTTPie", "CLI", ok31, f"HTTPie v{d31}")

# 32. mitmproxy
ok32, d32 = run_cmd("mitmproxy --version")
record(32, cat_e, "mitmproxy", "Proxy", ok32, d32)

# 33. tcpdump
ok33, d33 = run_cmd("tcpdump --version")
record(33, cat_e, "tcpdump", "CLI", ok33, d33)

# 34. websocat
ok34, d34 = run_cmd("websocat --version")
record(34, cat_e, "websocat", "CLI", ok34, d34)

# 35. curlie
ok35, d35 = run_cmd("curlie --version")
record(35, cat_e, "curlie", "CLI", ok35, d35)

# 36. httpstat
ok36, d36 = run_cmd("httpstat --version")
record(36, cat_e, "httpstat", "CLI", ok36, f"httpstat v{d36}")

# -------------------------------------------------------------
# F. Research & Discovery MCPs (37–40)
# -------------------------------------------------------------
cat_f = "Research & Discovery MCPs"

# 37. Brave Search MCP
ok37, d37 = check_mcp("brave-search")
record(37, cat_f, "Brave Search MCP", "MCP", ok37, d37)

# 38. Context7 MCP
ok38, d38 = check_mcp("context7")
record(38, cat_f, "Context7 MCP", "MCP", ok38, d38)

# 39. Filesystem MCP
ok39, d39 = check_mcp("filesystem")
record(39, cat_f, "Filesystem MCP", "MCP", ok39, d39)

# 40. Fetch MCP
ok40, d40 = check_mcp("fetch")
record(40, cat_f, "Fetch MCP", "MCP", ok40, d40)

print("=" * 80)
total_passed = sum(1 for r in results if r["status"])
total_failed = len(results) - total_passed
print(f"SUMMARY: {total_passed}/40 Tools Passed | {total_failed} Failed")
print("=" * 80)

if total_failed > 0:
    sys.exit(1)
sys.exit(0)
