"""Unified Command Line Interface for Project Atlas."""

import sys
import json
import argparse
from pathlib import Path

from atlas import __version__, __codename__
from atlas.core.config import FINDINGS_DIR, REPORTS_DIR, EXPERIMENTS_DIR
from atlas.core.logger import logger
from atlas.pipeline.pipeline import EvidencePipeline
from atlas.experiments.ledger import ExperimentLedger

def print_banner():
    print(f"""
===============================================================
       PROJECT ATLAS — Web Anomaly Research Laboratory
   Version: {__version__} | Codename: {__codename__} | Scientific Mode
===============================================================
""")

def cmd_scan(args):
    print_banner()
    pipeline = EvidencePipeline()
    finding = pipeline.run(args.url)
    print("\n" + "=" * 60)
    print(f"FINDING SUMMARY: {finding.finding_id}")
    print(f"Target:          {finding.target_url}")
    print(f"Anomaly Score:   {finding.anomaly_score}")
    print(f"Classification:  {finding.classification}")
    print(f"Signals ({len(finding.signals)}):")
    for s in finding.signals:
        print(f"  - [{s.category}] +{s.score_awarded} {s.name}: {s.description}")
    print(f"Report:          reports/REPORT_{finding.finding_id}.md")
    print("=" * 60 + "\n")

def cmd_experiment_new(args):
    print_banner()
    ledger = ExperimentLedger()
    exp_dir = ledger.create_experiment(
        title=args.title,
        hypothesis=args.hypothesis or "Investigate web anomalies and temporal stability.",
        target_urls=args.urls
    )
    print(f"\n[+] Created Experiment {exp_dir.name} at: {exp_dir}")
    print(f"    - {exp_dir}/hypothesis.md")
    print(f"    - {exp_dir}/setup.md")
    print(f"    - {exp_dir}/notes.md")
    print(f"    - {exp_dir}/result.md")
    print(f"    - {exp_dir}/evidence/\n")

def cmd_experiment_list(args):
    print_banner()
    ledger = ExperimentLedger()
    exps = ledger.list_experiments()
    print(f"Found {len(exps)} experiments in ledger:\n")
    print(f"{'ID':<6} {'STATUS':<12} {'TITLE'}")
    print("-" * 60)
    for e in exps:
        print(f"{e.get('experiment_id', 'N/A'):<6} {e.get('status', 'N/A'):<12} {e.get('title', 'Untitled')}")
    print()

def cmd_findings_list(args):
    print_banner()
    if not FINDINGS_DIR.exists():
        print("No findings recorded yet.\n")
        return

    findings = []
    for p in sorted(FINDINGS_DIR.glob("*.json")):
        try:
            with open(p, "r", encoding="utf-8") as f:
                findings.append(json.load(f))
        except Exception:
            continue

    print(f"Recorded Findings ({len(findings)} total):\n")
    print(f"{'FINDING ID':<28} {'SCORE':<7} {'CLASSIFICATION':<32} {'TARGET'}")
    print("-" * 90)
    for f in findings:
        print(f"{f.get('finding_id', 'N/A'):<28} {f.get('anomaly_score', 0):<7} {f.get('classification', 'N/A'):<32} {f.get('target_url', 'N/A')}")
    print()

def main():
    parser = argparse.ArgumentParser(
        prog="atlas",
        description="Project Atlas — Autonomous Web Anomaly & Archaeological Research Platform"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scan
    scan_parser = subparsers.add_parser("scan", help="Run full evidence pipeline on a target URL")
    scan_parser.add_argument("url", help="Target URL to inspect")

    # experiment
    exp_parser = subparsers.add_parser("experiment", help="Manage experiment ledger")
    exp_sub = exp_parser.add_subparsers(dest="subcommand")

    exp_new = exp_sub.add_parser("new", help="Provision next numbered experiment in ledger")
    exp_new.add_argument("title", help="Experiment Title")
    exp_new.add_argument("--hypothesis", "-H", help="Hypothesis statement", default="")
    exp_new.add_argument("--urls", "-u", nargs="*", help="Initial target URLs", default=[])

    exp_list = exp_sub.add_parser("list", help="List all experiments in ledger")

    # findings
    findings_parser = subparsers.add_parser("findings", help="Inspect research findings")
    findings_sub = findings_parser.add_subparsers(dest="subcommand")
    findings_list = findings_sub.add_parser("list", help="List all recorded findings")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "experiment":
        if args.subcommand == "new":
            cmd_experiment_new(args)
        elif args.subcommand == "list":
            cmd_experiment_list(args)
        else:
            exp_parser.print_help()
    elif args.command == "findings":
        if args.subcommand == "list":
            cmd_findings_list(args)
        else:
            findings_parser.print_help()
    else:
        print_banner()
        parser.print_help()

if __name__ == "__main__":
    main()
