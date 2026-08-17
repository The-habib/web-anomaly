"""Unified Command Line Interface for Project Atlas (Phase 0.5)."""

import sys
import json
import hashlib
import argparse
from pathlib import Path

from atlas import __version__, __codename__
from atlas.core.config import FINDINGS_DIR, REPORTS_DIR, EXPERIMENTS_DIR, ROOT_DIR
from atlas.core.logger import logger
from atlas.core.models import FindingVerificationReport, ArtifactVerificationResult
from atlas.pipeline.pipeline import EvidencePipeline
from atlas.experiments.ledger import ExperimentLedger

def print_banner():
    print(f"""
===============================================================
       PROJECT ATLAS — Web Anomaly Research Laboratory
   Version: {__version__} | Codename: {__codename__} | Scientific Mode (Phase 0.5)
===============================================================
""")

def cmd_scan(args):
    print_banner()
    pipeline = EvidencePipeline()
    finding = pipeline.run(args.url)
    print("\n" + "=" * 65)
    print(f"FINDING SUMMARY: {finding.finding_id}")
    print(f"Target:          {finding.target_url}")
    print(f"Anomaly Score:   {finding.anomaly_score}")
    print(f"Confidence:      {finding.confidence:.2f}")
    print(f"Evidence State:  [{finding.evidence_state.value}]")
    print(f"Classification:  {finding.classification}")
    print(f"Signals ({len(finding.signals)}):")
    for s in finding.signals:
        print(f"  - [{s.evidence_state.value}] [{s.category}] +{s.score_awarded} (conf: {s.confidence:.2f}) {s.name}: {s.description}")
    print(f"Report:          reports/REPORT_{finding.finding_id}.md")
    print("=" * 65 + "\n")

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
    print(f"{'FINDING ID':<28} {'SCORE':<7} {'CONF':<6} {'STATE':<13} {'CLASSIFICATION':<28} {'TARGET'}")
    print("-" * 110)
    for f in findings:
        conf_str = f"{f.get('confidence', 0.5):.2f}"
        state_str = f"[{f.get('evidence_state', 'CANDIDATE')}]"
        print(f"{f.get('finding_id', 'N/A'):<28} {f.get('anomaly_score', 0):<7} {conf_str:<6} {state_str:<13} {f.get('classification', 'N/A'):<28} {f.get('target_url', 'N/A')}")
    print()

def cmd_evidence_verify(args):
    print_banner()
    finding_files = []
    if args.finding_id:
        target_file = FINDINGS_DIR / f"{args.finding_id}.json"
        if not target_file.exists():
            # Try searching without prefix
            matches = list(FINDINGS_DIR.glob(f"*{args.finding_id}*.json"))
            if matches:
                target_file = matches[0]
            else:
                print(f"Error: Finding '{args.finding_id}' not found in {FINDINGS_DIR}")
                sys.exit(1)
        finding_files.append(target_file)
    else:
        finding_files = sorted(FINDINGS_DIR.glob("*.json"))

    if not finding_files:
        print("No findings available to verify.")
        return

    print(f"Verifying cryptographic integrity for {len(finding_files)} finding(s)...\n")

    for f_path in finding_files:
        with open(f_path, "r", encoding="utf-8") as f:
            finding_data = json.load(f)

        f_id = finding_data.get("finding_id", f_path.stem)
        target_url = finding_data.get("target_url", "Unknown")
        artifacts = finding_data.get("artifacts", [])

        print(f"Finding: {f_id} ({target_url})")
        print(f"{'ARTIFACT':<35} {'SIZE':<12} {'CHECKSUM':<18} {'STATUS'}")
        print("-" * 75)

        passed = 0
        failed = 0
        missing = 0

        for art in artifacts:
            rel_path = art.get("relative_path", "")
            expected_hash = art.get("sha256", "")
            file_name = art.get("file_name", rel_path)
            full_path = ROOT_DIR / rel_path

            if not full_path.exists():
                print(f"{file_name:<35} {'N/A':<12} {'N/A':<18} \033[91mMISSING\033[0m")
                missing += 1
                continue

            with open(full_path, "rb") as af:
                file_bytes = af.read()
                actual_hash = hashlib.sha256(file_bytes).hexdigest()
                actual_size = len(file_bytes)

            if actual_hash == expected_hash:
                print(f"{file_name:<35} {actual_size:<12} {actual_hash[:12]}... \033[92mPASS\033[0m")
                passed += 1
            else:
                print(f"{file_name:<35} {actual_size:<12} {actual_hash[:12]}... \033[91mFAIL_MISMATCH\033[0m")
                failed += 1

        print("-" * 75)
        status_color = "\033[92mALL PASS\033[0m" if failed == 0 and missing == 0 else "\033[91mCORRUPTED/INCOMPLETE\033[0m"
        print(f"Integrity Result: {passed}/{len(artifacts)} Verified | {status_color}\n")

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

    # evidence
    evidence_parser = subparsers.add_parser("evidence", help="Evidence operations")
    evidence_sub = evidence_parser.add_subparsers(dest="subcommand")
    evidence_verify = evidence_sub.add_parser("verify", help="Verify cryptographic SHA-256 integrity of evidence artifacts")
    evidence_verify.add_argument("finding_id", nargs="?", help="Specific Finding ID to verify (verifies all if omitted)")

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
    elif args.command == "evidence":
        if args.subcommand == "verify":
            cmd_evidence_verify(args)
        else:
            evidence_parser.print_help()
    else:
        print_banner()
        parser.print_help()

if __name__ == "__main__":
    main()
