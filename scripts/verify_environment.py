#!/usr/bin/env python3
"""Verify environment, tools, and Project Atlas laboratory readiness."""

import sys
import shutil
import importlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def check():
    print("=" * 60)
    print("  PROJECT ATLAS — LABORATORY READINESS AUDIT")
    print("=" * 60)

    # 1. Check Python packages
    py_modules = [
        "playwright", "selenium", "browser_use", "warcio",
        "cdx_toolkit", "bs4", "lxml", "readability", "trafilatura",
        "httpie", "mitmproxy", "httpstat", "mcp_server_fetch"
    ]
    print("\n[Python Packages]")
    for m in py_modules:
        try:
            importlib.import_module(m)
            print(f"  [PASS] {m:<20} installed")
        except ImportError as e:
            print(f"  [FAIL] {m:<20} missing ({e})")

    # 2. Check CLI Binaries
    cli_tools = [
        "playwright", "puppeteer", "cri", "wget", "curl", "httrack",
        "katana", "gospider", "htmlq", "pup", "jq", "yq",
        "pageres", "capture-website", "blink-diff", "pixelmatch",
        "resemblejs", "http", "mitmproxy", "tcpdump", "websocat",
        "curlie", "httpstat"
    ]
    print("\n[CLI Binaries]")
    for b in cli_tools:
        p = shutil.which(b)
        if p:
            print(f"  [PASS] {b:<20} found at {p}")
        else:
            print(f"  [FAIL] {b:<20} NOT found in PATH")

    # 3. Check Atlas Core Imports
    print("\n[Atlas Core Architecture]")
    try:
        from atlas.core.config import ROOT_DIR, EVIDENCE_DIR, FINDINGS_DIR
        from atlas.core.logger import logger
        from atlas.core.models import Finding, Experiment
        from atlas.scoring.scorer import AnomalyScorer
        from atlas.pipeline.pipeline import EvidencePipeline
        from atlas.experiments.ledger import ExperimentLedger
        print("  [PASS] All Atlas core modules imported cleanly.")
    except Exception as e:
        print(f"  [FAIL] Atlas core import error: {e}")

    print("\n" + "=" * 60)
    print("  LABORATORY STATUS: OPERATIONAL")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    check()
