#!/usr/bin/env python3
"""Run Project Atlas Evidence Pipeline on a target URL."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from atlas.cli import main

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/run_pipeline.py <TARGET_URL>")
        sys.exit(1)
    url = sys.argv[1]
    sys.argv = ["atlas", "scan", url]
    main()
