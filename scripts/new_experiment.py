#!/usr/bin/env python3
"""Provision a new numbered experiment in the Project Atlas ledger."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from atlas.experiments.ledger import ExperimentLedger

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/new_experiment.py '<TITLE>' ['<HYPOTHESIS>']")
        sys.exit(1)

    title = sys.argv[1]
    hypothesis = sys.argv[2] if len(sys.argv) > 2 else "Investigate temporal stability and web anomalies."

    ledger = ExperimentLedger()
    exp_dir = ledger.create_experiment(title=title, hypothesis=hypothesis)
    print(f"Created Experiment {exp_dir.name} at: {exp_dir}")
