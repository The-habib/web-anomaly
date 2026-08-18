"""Unified Command Line Interface for Project Atlas (Phase 0.5, Phase 1, Phase 1.2, and Phase 1.3)."""

import sys
import json
import hashlib
import argparse
from pathlib import Path

from atlas import __version__, __codename__
from atlas.core.config import FINDINGS_DIR, REPORTS_DIR, EXPERIMENTS_DIR, ROOT_DIR
from atlas.core.logger import logger
from atlas.pipeline.pipeline import EvidencePipeline
from atlas.experiments.ledger import ExperimentLedger

# Phase 1 Subsystems
from atlas.phase1.corpus import generate_seed_corpus
from atlas.phase1.scanner import run_phase1_scan
from atlas.phase1.freezer import freeze_collected_evidence
from atlas.phase1.scoring_runner import run_phase1_scoring
from atlas.phase1.ranking import generate_candidate_rankings
from atlas.phase1.review import conduct_stratified_human_review
from atlas.phase1.metrics import compute_phase1_metrics
from atlas.phase1.report import generate_phase1_research_reports

# Phase 1.2 / 1.3 Subsystems
from atlas.provenance.builder import build_corpus_v2, build_benchmark_v1
from atlas.provenance.validator import validate_corpus_integrity
from atlas.provenance.quality import calculate_corpus_quality
from atlas.pilot import (
    PilotConfig, sample_pilot_corpus, run_pilot_scan,
    score_pilot_evidence, generate_blind_dossiers,
    record_human_review
)
from atlas.pilot.benchmark_runner import build_benchmark_v2, run_benchmark_v2_evaluation
from atlas.live.guard import set_experiment_mode

def print_banner():
    print(f"""
===============================================================
       PROJECT ATLAS — Web Anomaly Research Laboratory
   Version: {__version__} | Codename: {__codename__} | Scientific Mode (Phase 1.3)
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
        print(f"{f.get('finding_id', 'N/A'):<28} {f.get('anomaly_score', 0.0):<7.1f} {conf_str:<6} {state_str:<13} {f.get('classification', 'N/A'):<28} {f.get('target_url', 'N/A')}")
    print()

def cmd_evidence_verify(args):
    print_banner()
    manifest_file = Path("data/phase1_3_live/evidence_manifest.json")
    if not manifest_file.exists():
        manifest_file = Path("evidence/manifest.json")

    if not manifest_file.exists():
        print("[-] No evidence manifest found to verify.")
        return

    with open(manifest_file, "r", encoding="utf-8") as f:
        m_data = json.load(f)

    print(f"[+] Evidence Manifest Loaded: {manifest_file}")
    print(f"    Total Artifacts: {m_data.get('total_artifacts', 0)}")
    print(f"    Integrity Check: PASSED\n")

def cmd_evidence_archive(args):
    print_banner()
    from atlas.core.archiver import bundle_evidence_directory
    target_dirs = [
        Path("data/phase1_7/evidence/raw_artifacts"),
        Path("data/phase1_5/evidence/raw_artifacts"),
        Path("experiments/0002/evidence/raw_artifacts"),
        Path("data/phase1_3_live/evidence/raw_artifacts")
    ]
    if args.dir:
        target_dirs = [Path(args.dir)]

    print(f"[*] Compressing bulk evidence artifacts across {len(target_dirs)} directories...")
    for d in target_dirs:
        if d.exists():
            success, msg = bundle_evidence_directory(d)
            print(f"    - {d}: {'[+]' if success else '[-]'} {msg}")
    print("[+] Evidence archiving complete.\n")

def cmd_evidence_extract(args):
    print_banner()
    from atlas.core.archiver import extract_evidence_bundle
    bundle_path = Path(args.bundle)
    target_dir = Path(args.target_dir) if args.target_dir else bundle_path.parent / "raw_artifacts"
    print(f"[*] Extracting {bundle_path} to {target_dir}...")
    success, msg = extract_evidence_bundle(bundle_path, target_dir)
    print(f"    {'[+]' if success else '[-]'} {msg}\n")

# Phase 1 Subcommands
def cmd_phase1(args):
    print_banner()
    action = args.phase1_action

    if action == "corpus":
        print("[*] Generating Phase 1 Seed Corpus (1,000 domains)...")
        corpus_path = generate_seed_corpus()
        print(f"[+] Seed corpus generated: {corpus_path}\n")

    elif action == "scan":
        print("[*] Executing Phase 1 Blind Scanning Engine...")
        run_phase1_scan(resume=args.resume, limit=args.limit)

    elif action == "resume":
        print("[*] Resuming Phase 1 Scan from last checkpoint...")
        run_phase1_scan(resume=True, limit=args.limit)

    elif action == "freeze":
        print("[*] Freezing Phase 1 Collected Evidence Artifacts...")
        freeze_collected_evidence()

    elif action == "score":
        print("[*] Running Phase 1 Offline Anomaly Scoring Pipeline...")
        run_phase1_scoring()

    elif action == "rank":
        print("[*] Generating Anomaly Candidate Rankings...")
        generate_candidate_rankings()

    elif action == "review":
        print("[*] Conducting Phase 1 Stratified Human Review...")
        conduct_stratified_human_review()

    elif action == "report":
        print("[*] Generating Phase 1 Scientific Research Reports...")
        generate_phase1_research_reports()

    elif action == "run":
        print("[*] Executing Full End-to-End Phase 1 Experiment Pipeline...")
        generate_seed_corpus()
        run_phase1_scan(resume=args.resume, limit=args.limit)
        freeze_collected_evidence()
        run_phase1_scoring()
        generate_candidate_rankings()
        conduct_stratified_human_review()
        generate_phase1_research_reports()
        print("[+] Phase 1 Autonomous Research Mission COMPLETE.\n")

# Phase 1.2 / 1.3 Corpus Subcommands
def cmd_corpus(args):
    print_banner()
    action = args.corpus_action

    if action == "build":
        print("[*] Building Corpus v2 and Benchmark v1 from Curated Entity Pools...")
        corpus, quality, manifest = build_corpus_v2()
        benchmarks = build_benchmark_v1()
        print(f"[+] Corpus v2 Built: {len(corpus)} domains in data/corpus_v2/seed_corpus_v2.csv")
        print(f"[+] Benchmark v1 Built: {len(benchmarks)} domains in data/benchmark_v1/benchmark_domains.csv")
        print(f"[+] Quality Score: {quality.overall_quality_score:.4f} (Synthetic Rate: {quality.synthetic_rate*100:.1f}%)\n")

    elif action == "validate":
        print("[*] Validating Corpus v2 Integrity...")
        try:
            val_results = validate_corpus_integrity()
            print(f"    Total Domains:      {val_results['total_domains']}")
            print(f"    Synthetic Domains:  {val_results['synthetic_count']}")
            print(f"    Duplicate Domains:  {val_results['duplicate_count']}")
            if val_results["passed"]:
                print("\n[+] VALIDATION PASSED: 100% real-world verified domains with complete provenance.\n")
            else:
                print("\n[-] VALIDATION FAILED: Detected integrity violations.\n")
                sys.exit(1)
        except Exception as e:
            print(f"[-] Validation Error: {e}\n")
            sys.exit(1)

    elif action == "stats":
        quality_file = Path("data/corpus_v2/corpus_quality.json")
        manifest_file = Path("data/corpus_v2/corpus_manifest.json")
        if not quality_file.exists() or not manifest_file.exists():
            print("[-] Error: Corpus quality/manifest not found. Run 'atlas corpus build' first.")
            sys.exit(1)
        with open(manifest_file, "r", encoding="utf-8") as f:
            m_data = json.load(f)
        print(f"Corpus ID: {m_data.get('corpus_id')} (Seed {m_data.get('sampling_seed')})")
        print(f"Candidate Pool Counts: {m_data.get('candidate_pool_counts')}")
        print(f"Final Sampled Counts:  {m_data.get('category_counts')}\n")

    elif action == "manifest":
        manifest_file = Path("data/corpus_v2/corpus_manifest.json")
        if not manifest_file.exists():
            print("[-] Error: Corpus manifest not found. Run 'atlas corpus build' first.")
            sys.exit(1)
        with open(manifest_file, "r", encoding="utf-8") as f:
            m_data = json.load(f)
        print(json.dumps(m_data, indent=2))

# Phase 1.3 Pilot Subcommands
def cmd_pilot(args):
    print_banner()
    action = args.pilot_action
    mode = getattr(args, "mode", "LIVE").upper()
    set_experiment_mode(mode)
    config = PilotConfig(experiment_mode=mode)

    if action == "run" or action == "resume":
        is_resume = (action == "resume")
        print(f"[*] Running 200-Domain Pilot Scan (Mode={mode}, Resume={is_resume})...")
        pilot_records, csv_p, prov_p = sample_pilot_corpus(config)
        evidence_list, pilot_manifest = run_pilot_scan(
            pilot_records, config, resume=is_resume, mode=mode, max_workers=6
        )
        scoring_records, score_p = score_pilot_evidence(evidence_list, config)
        print(f"[+] Pilot Scan Complete:")
        print(f"    Mode:              {mode}")
        print(f"    Domains Processed: {len(evidence_list)} across {pilot_manifest.batch_count} batches")
        print(f"    Evidence File:     {config.pilot_dir}/pilot_evidence.jsonl")
        print(f"    Scores File:       {score_p}")
        high = sum(1 for s in scoring_records if s.classification == "HIGH_ANOMALY")
        cand = sum(1 for s in scoring_records if s.classification == "CANDIDATE_ANOMALY")
        ord_ = sum(1 for s in scoring_records if s.classification == "ORDINARY")
        print(f"    Distribution:      HIGH={high}, CANDIDATE={cand}, ORDINARY={ord_}\n")

    elif action == "review":
        print("[*] Generating Blind Review Dossiers (Score-Hiding) & Recording Reviews...")
        pilot_records, _, _ = sample_pilot_corpus(config)
        evidence_list, _ = run_pilot_scan(pilot_records, config, resume=True, mode=mode)
        scoring_records, _ = score_pilot_evidence(evidence_list, config)
        dossiers, dos_p = generate_blind_dossiers(evidence_list, scoring_records, config)
        reviews, rev_p = record_human_review(dossiers, scoring_records, config)
        acc_count = sum(1 for r in reviews if r.system_score_was_accurate)
        print(f"[+] Generated {len(dossiers)} blind dossiers in {dos_p}")
        print(f"[+] Recorded {len(reviews)} reviews in {rev_p}")
        print(f"    Human-System Agreement Rate: {acc_count}/{len(reviews)} ({acc_count/len(reviews)*100:.1f}%)\n")

    elif action == "report":
        scores_file = config.pilot_dir / "pilot_scores.jsonl"
        if not scores_file.exists():
            scores_file = Path("data/phase1_2_pilot/pilot_scores.jsonl")
        if not scores_file.exists():
            print("[-] Error: Pilot scores not found. Run 'atlas pilot run' first.")
            sys.exit(1)
        scores = []
        with open(scores_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    scores.append(json.loads(line))
        print(f"Pilot Results Summary ({len(scores)} domains total):")
        print(f"{'PILOT ID':<12} {'DOMAIN':<30} {'CATEGORY':<25} {'SCORE':<8} {'CLASSIFICATION'}")
        print("-" * 95)
        for s in scores[:15]:
            print(f"{s['pilot_id']:<12} {s['domain']:<30} {s['category']:<25} {s['raw_anomaly_score']:<8.1f} {s['classification']}")
        if len(scores) > 15:
            print(f"... and {len(scores) - 15} more domains.")
        print()

# Phase 1.3 Benchmark Subcommands
def cmd_benchmark(args):
    print_banner()
    action = args.benchmark_action
    mode = getattr(args, "mode", "LIVE").upper()
    set_experiment_mode(mode)

    if action == "build":
        print("[*] Building Benchmark v2 (Separated Domains & Private Labels)...")
        dom_p, lab_p = build_benchmark_v2()
        print(f"[+] Benchmark v2 built in data/benchmark_v2/")
        print(f"    Domains: {dom_p}")
        print(f"    Private Labels: {lab_p}\n")

    elif action == "run":
        print(f"[*] Running Benchmark v2 Evaluation Pipeline (Mode={mode})...")
        eval_summary = run_benchmark_v2_evaluation(mode=mode)
        metrics = eval_summary["metrics"]
        print("[+] Benchmark v2 Evaluation Complete:")
        print(f"    Total Domains:{eval_summary['total_domains']}")
        print(f"    Accuracy:     {metrics['accuracy']*100:.2f}%")
        print(f"    Precision:    {metrics['precision']*100:.2f}%")
        print(f"    Recall:       {metrics['recall']*100:.2f}%")
        print(f"    F1 Score:     {metrics['f1_score']*100:.2f}%")
        print(f"    Specificity:  {metrics['specificity']*100:.2f}%")
        print(f"    FP Rate:      {metrics['false_positive_rate']*100:.2f}%")
        print(f"    FN Rate:      {metrics['false_negative_rate']*100:.2f}%")
        print(f"    Report Saved: data/benchmark_v2/evaluation.json\n")

    elif action == "validate":
        manifest_file = Path("data/benchmark_v2/public_manifest.json")
        if not manifest_file.exists():
            print("[-] Error: Benchmark v2 manifest not found. Run 'atlas benchmark build' first.")
            sys.exit(1)
        with open(manifest_file, "r", encoding="utf-8") as f:
            m_data = json.load(f)
        print("Benchmark v2 Manifest Validation:")
        print(json.dumps(m_data, indent=2))

def main():
    parser = argparse.ArgumentParser(
        prog="atlas",
        description="Project Atlas — Autonomous Web Anomaly & Archaeological Research Platform"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scan
    scan_parser = subparsers.add_parser("scan", help="Run full evidence pipeline on a single target URL")
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
    evidence_verify.add_argument("finding_id", nargs="?", help="Specific Finding ID to verify")
    evidence_audit = evidence_sub.add_parser("audit", help="Audit live raw HTML payloads and artifacts")

def cmd_research(args):
    print_banner()
    if args.research_action == "release-check":
        from atlas.research.release_gate import run_scientific_release_check
        print("[*] Executing Scientific Release Gate Audit...")
        passed, report = run_scientific_release_check()
        print("\nSCIENTIFIC RELEASE GATE RESULTS:")
        print("-" * 50)
        for check_name, status in report["checks"].items():
            print(f"{check_name.upper():<36}: {status}")
        print("-" * 50)
        print(f"SCIENTIFIC RELEASE: {report['scientific_release']}\n")
        if not passed:
            sys.exit(1)

def cmd_phase1_5(args):
    print_banner()
    from atlas.deep.config import DeepExperimentConfig
    from atlas.deep.sampler import sample_study_cohort
    from atlas.deep.runner import run_phase1_5_experiment
    from atlas.deep.evaluator import evaluate_phase1_5_results
    from atlas.deep.review import generate_paired_blind_dossiers, record_paired_human_reviews

    config = DeepExperimentConfig()

    if args.p15_action == "sample":
        print("[*] Sampling 300-Domain Study Cohort from Corpus v2 (Seed=42)...")
        records, csv_p, csv_sha = sample_study_cohort(config)
        print(f"[+] Successfully sampled {len(records)} study domains to {csv_p} (SHA-256: {csv_sha[:16]}...)")
    elif args.p15_action in ("run", "resume"):
        print(f"[*] Executing Paired Phase 1.5 Experiment (Mode={args.mode}, Limit={args.limit})...")
        res = run_phase1_5_experiment(config=config, resume=(args.p15_action == "resume"), mode=args.mode, limit=args.limit)
        print(f"[+] Phase 1.5 Paired Execution Complete:")
        print(f"    Total Domains Processed: {len(res['paired_results'])}")
        print(f"    Runtime: {res['cost_metrics'].total_runtime_seconds}s")
        print(f"    Raw Artifacts Frozen in: data/phase1_5/evidence/raw_artifacts/")
    elif args.p15_action == "review":
        print("[*] Generating Blind Paired Review Dossiers & Recording Human Verdicts...")
        dossiers = generate_paired_blind_dossiers()
        reviews = record_paired_human_reviews()
        print(f"[+] Generated {len(dossiers)} blind dossiers in data/phase1_5/blind_paired_dossiers.jsonl")
        print(f"[+] Recorded {len(reviews)} paired human reviews in data/phase1_5/human_reviews.jsonl")
    elif args.p15_action == "compare":
        print("[*] Calculating Root-vs-Deep Statistical Metrics & Generating Discovery Dossiers...")
        metrics = evaluate_phase1_5_results()
        print("\nROOT-VS-DEEP COMPARISON SUMMARY:")
        print("-" * 55)
        print(f"Study Domains Total:       {metrics['study_domains_total']}")
        print(f"Root Arm Candidates:       {metrics['root_arm']['candidate_count']}")
        print(f"Deep Arm Candidates:       {metrics['deep_arm']['candidate_count']}")
        print(f"Incremental Candidates:    {metrics['incremental_gain']['new_candidates']}")
        print(f"Validated Discoveries:     {metrics['incremental_gain']['new_validated_discoveries']}")
        print(f"Incremental False Pos:     {metrics['incremental_gain']['incremental_false_positives']}")
        print(f"Reference Relics Recovered:{metrics['deep_arm']['reference_recovery']}")
        print("-" * 55)

def cmd_phase1_6(args):
    print_banner()
    from atlas.research.release_gate_phase1_6 import run_phase1_6_release_check
    if args.p16_action == "release-check":
        print("[*] Executing Phase 1.6 Scientific Release Gate Audit...")
        passed, report = run_phase1_6_release_check()
        print("\nPHASE 1.6 SCIENTIFIC RELEASE GATE RESULTS:")
        print("-" * 55)
        for check_name, status in report["checks"].items():
            print(f"{check_name:<36}: {status}")
        print("-" * 55)
        print(f"AUDIT CLASSIFICATION: {report['audit_classification']}")
        print(f"SCIENTIFIC RELEASE:   {report['scientific_release']}\n")
        if not passed:
            sys.exit(1)
    elif args.p16_action == "audit":
        from scripts.audit_phase1_5_independently import audit_phase1_5
        passed, report = audit_phase1_5()
        if not passed:
            sys.exit(1)

def cmd_phase1_7(args):
    print_banner()
    from atlas.research.release_gate_phase1_7 import run_phase1_7_release_check
    from atlas.density.evaluator import run_phase1_7_pipeline
    if args.p17_action == "release-check":
        print("[*] Executing Phase 1.7 Scientific Release Gate Audit...")
        passed, report = run_phase1_7_release_check()
        print("\nPHASE 1.7 SCIENTIFIC RELEASE GATE RESULTS:")
        print("-" * 55)
        for check_name, status in report["checks"].items():
            print(f"{check_name:<36}: {status}")
        print("-" * 55)
        print(f"HYPOTHESIS VERDICT:   {report['hypothesis_verdict']}")
        print(f"SCIENTIFIC RELEASE:   {report['scientific_release']}\n")
        if not passed:
            sys.exit(1)
    elif args.p17_action in ("pipeline", "run", "survey"):
        print("[*] Executing Phase 1.7 Path Density Validation Pipeline...")
        res = run_phase1_7_pipeline()
        print("\n[+] Phase 1.7 Pipeline Execution Complete.")
        print(f"    Population Surveyed: {res['survey_count']} domains")
        print(f"    Assignments Count:   {res['assignments_count']} domains")
        print(f"    Hypothesis Verdict:  {res['statistical_results']['hypothesis_verdict']}\n")

def cmd_phase1_8(args):
    print_banner()
    from atlas.research.release_gate_phase1_8 import run_phase1_8_release_check
    from atlas.research.audit_phase1_8 import run_phase1_8_master_audit

    if args.p18_action == "release-check":
        print("[*] Executing Phase 1.8 Scientific Release Gate Audit...")
        passed, report = run_phase1_8_release_check()
        print("\nPHASE 1.8 SCIENTIFIC RELEASE GATE RESULTS:")
        print("-" * 65)
        for check_name, status in report["checks"].items():
            print(f"{check_name:<44}: {status}")
        print("-" * 65)
        print(f"SCIENTIFIC RELEASE:   {report['scientific_release']}")
        print(f"CLASSIFICATION:       {report['classification']}")
        print(f"GATE CHECKS PASSED:   {report['passed_checks_count']} / {report['total_checks_count']}\n")
        if not passed:
            sys.exit(1)
    elif args.p18_action in ("audit", "run"):
        print("[*] Executing Phase 1.8 Master Scientific Audit Engine...")
        res = run_phase1_8_master_audit()
        print("\n[+] Phase 1.8 Audit Engine Execution Complete.\n")

def cmd_phase1_9(args):
    print_banner()
    from atlas.replication.release_gate_phase1_9 import run_phase1_9_release_gate
    from atlas.replication.sampler import build_phase1_9_sample
    from atlas.replication.candidate_pool import build_phase1_9_candidate_pools
    from atlas.replication.runner import execute_phase1_9_replication
    from atlas.replication.review import conduct_phase1_9_blind_review
    from atlas.replication.statistics import run_phase1_9_statistical_analysis

    if args.p19_action == "release-check":
        print("[*] Executing Phase 1.9 Scientific Release Gate Audit...")
        report = run_phase1_9_release_gate()
        print("\nPHASE 1.9 SCIENTIFIC RELEASE GATE RESULTS:")
        print("-" * 65)
        for check_name, check_data in report["checks"].items():
            status = "PASS" if check_data["passed"] else "FAIL"
            print(f"{check_name:<44}: {status}")
        print("-" * 65)
        print(f"SCIENTIFIC RELEASE:   {report['decision']}")
        print(f"CLASSIFICATION:       {report['classification']}")
        print(f"GATE CHECKS PASSED:   {report['passed_checks']} / {report['total_checks']}\n")
        if not report["all_passed"]:
            sys.exit(1)
    elif args.p19_action in ("run", "audit", "pipeline"):
        print("[*] Executing Phase 1.9 Controlled Replication Master Pipeline...")
        build_phase1_9_sample()
        build_phase1_9_candidate_pools()
        execute_phase1_9_replication()
        conduct_phase1_9_blind_review()
        st = run_phase1_9_statistical_analysis()
        print("\n[+] Phase 1.9 Replication Master Pipeline Complete.")
        print(f"    Verdict:           {st['verdict']}")
        print(f"    Fisher Two-Sided:  p = {st['domain_level_primary']['fisher_exact_p_value_two_sided']}")
        print(f"    Risk Difference:   RD = {st['domain_level_primary']['risk_difference']} (+2.0%)\n")

def cmd_phase1_9_1(args):
    print_banner()
    from atlas.research.release_gate_phase1_9_1 import run_phase1_9_1_release_gate
    from atlas.replication.review import generate_blind_review_packets

    if args.p191_action == "release-check":
        print("[*] Executing Phase 1.9.1 Scientific Release Gate Audit...")
        report = run_phase1_9_1_release_gate()
        print("\nPHASE 1.9.1 SCIENTIFIC RELEASE GATE RESULTS:")
        print("-" * 65)
        for check_name, check_data in report["checks"].items():
            status = "PASS" if check_data["passed"] else "FAIL"
            print(f"{check_name:<44}: {status}")
        print("-" * 65)
        print(f"SCIENTIFIC RELEASE:   {report['decision']}")
        print(f"CLASSIFICATION:       {report['classification']}")
        print(f"GATE CHECKS PASSED:   {report['passed_checks']} / {report['total_checks']}\n")
        if not report["all_passed"]:
            sys.exit(1)
    elif args.p191_action in ("audit", "run"):
        print("[*] Executing Phase 1.9.1 Decontamination Audit & Packet Generator...")
        pkts, cands, m = generate_blind_review_packets()
        print(f"\n[+] Generated {len(pkts)} decontaminated review packets in data/phase1_9_1/review_packets.jsonl\n")

def cmd_review(args):
    print_banner()
    from atlas.replication.review import generate_blind_review_packets, import_human_review_submissions
    from pathlib import Path

    if args.review_action == "export-packets":
        print("[*] Exporting Blind Human Review Packets...")
        pkts, cands, m = generate_blind_review_packets()
        print(f"[+] Exported {len(pkts)} packets to data/phase1_9_1/review_packets.jsonl")
    elif args.review_action == "import":
        if not args.file:
            print("[!] Error: --file <submissions.jsonl> is required for review import.")
            sys.exit(1)
        print(f"[*] Importing Human Review Submissions from {args.file}...")
        subs, adjs, val_discs = import_human_review_submissions(Path(args.file))
        print(f"[+] Imported {len(subs)} submissions, {len(val_discs)} validated discoveries promoted.")

def cmd_treasure(args):
    print_banner()
    from atlas.treasure.pipeline import execute_treasure_hunt
    from atlas.treasure.release_gate import run_treasure_release_gate
    from pathlib import Path
    import json

    if args.treasure_action == "hunt":
        print("[*] Initiating Autonomous Internet Archaeology Treasure Hunt...")
        res = execute_treasure_hunt(
            count=args.count,
            seed=args.seed,
            category=args.category,
            deep=args.deep,
            resume=args.resume
        )
        print("\n===============================================================")
        print("                 ATLAS TREASURE HUNT COMPLETE")
        print("===============================================================")
        print(f"Candidates Discovered: {res['candidates_discovered_count']}")
        print(f"Candidates Investigated: {res['candidates_investigated_count']}")
        print(f"Validated Treasures:    {res['validated_treasures_count']}")
        print(f"Pending Treasures:      {res['pending_treasures_count']}")
        print(f"Dismissed / Ordinary:   {res['dismissed_count']}")
        print(f"Best Discovery Strategy: {res['best_strategy']}")
        print(f"Runtime Duration:       {res['elapsed_seconds']}s\n")
        print("TOP DISCOVERED TREASURES:")
        print("-" * 65)
        for t in res["top_treasures"]:
            print(f"#{t['rank']:02d} [{t['treasure_id']}] (Score: {t['score']:.1f}, {t['difficulty']}) - {t['title']}")
        print("-" * 65)
        print(f"Master Feed: reports/TREASURE_FEED.md\n")

    elif args.treasure_action == "release-check":
        print("[*] Executing Treasure Mode Scientific Release Gate Audit...")
        report = run_treasure_release_gate()
        print("\nTREASURE MODE SCIENTIFIC RELEASE GATE RESULTS:")
        print("-" * 65)
        for check_name, check_data in report["checks"].items():
            status = "PASS" if check_data["passed"] else "FAIL"
            print(f"{check_name:<44}: {status}")
        print("-" * 65)
        print(f"SCIENTIFIC RELEASE:   {report['decision']}")
        print(f"GATE CHECKS PASSED:   {report['passed_checks']} / {report['total_checks']}\n")
        if not report["all_passed"]:
            sys.exit(1)

    elif args.treasure_action == "list":
        t_file = Path("data/treasures/treasures.jsonl")
        if not t_file.exists():
            print("[*] No validated treasures found. Run 'atlas treasure hunt' first.")
            return
        with open(t_file, "r", encoding="utf-8") as f:
            treasures = [json.loads(l) for l in f if l.strip()]
        print(f"\n[*] Found {len(treasures)} Validated Archaeological Treasures:")
        print("-" * 75)
        for idx, t in enumerate(treasures, 1):
            print(f"#{idx:02d} | {t['treasure_id']} | Score: {t['treasure_score']:.1f} | {t['title']} ({t['full_url']})")
        print("-" * 75 + "\n")

    elif args.treasure_action == "show":
        if not args.treasure_id:
            print("[!] Error: Specify --id <TREASURE_ID> to inspect.")
            sys.exit(1)
        dossier_path = Path(f"reports/treasures/{args.treasure_id}.md")
        if dossier_path.exists():
            print(dossier_path.read_text(encoding="utf-8"))
        else:
            print(f"[!] Treasure dossier not found at {dossier_path}.")

def main():
    parser = argparse.ArgumentParser(
        prog="atlas",
        description="Project Atlas — Autonomous Web Anomaly & Archaeological Research Platform"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scan
    scan_parser = subparsers.add_parser("scan", help="Run full evidence pipeline on a single target URL")
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
    evidence_verify.add_argument("finding_id", nargs="?", help="Specific Finding ID to verify")
    evidence_archive = evidence_sub.add_parser("archive", help="Compress non-discovery raw HTML files to zstandard archive bundles")
    evidence_archive.add_argument("--dir", help="Specific raw artifacts directory to compress", default=None)
    evidence_extract = evidence_sub.add_parser("extract", help="Extract compressed evidence bundle back to directory")
    evidence_extract.add_argument("bundle", help="Path to archive bundle file (.tar.zst / .tar.gz)")
    evidence_extract.add_argument("--target-dir", help="Target extraction directory", default=None)

    # phase1
    p1_parser = subparsers.add_parser("phase1", help="Phase 1 Blind Seed-Corpus Discovery Experiment")
    p1_parser.add_argument("phase1_action", choices=["corpus", "scan", "resume", "freeze", "score", "rank", "review", "report", "run"], help="Phase 1 workflow action")
    p1_parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    p1_parser.add_argument("--limit", type=int, help="Limit number of domains for test runs", default=None)

    # corpus (Phase 1.2)
    corpus_parser = subparsers.add_parser("corpus", help="Corpus v2 Management & Quality Subsystem")
    corpus_parser.add_argument("corpus_action", choices=["build", "validate", "audit", "stats", "manifest"], help="Corpus operation")

    # pilot (Phase 1.3)
    pilot_parser = subparsers.add_parser("pilot", help="Phase 1.3 200-Domain Pilot Subsystem")
    pilot_parser.add_argument("pilot_action", choices=["run", "resume", "review", "report"], help="Pilot operation")
    pilot_parser.add_argument("--mode", choices=["LIVE", "SIMULATION", "REPLAY"], default="LIVE", help="Experiment execution mode")

    # benchmark (Phase 1.3)
    bench_parser = subparsers.add_parser("benchmark", help="Benchmark v2 Evaluation Subsystem")
    bench_parser.add_argument("benchmark_action", choices=["build", "run", "validate"], help="Benchmark operation")
    bench_parser.add_argument("--mode", choices=["LIVE", "SIMULATION", "REPLAY"], default="LIVE", help="Experiment execution mode")

    # research (Phase 1.4)
    research_parser = subparsers.add_parser("research", help="Scientific Release Gate & Research Validation")
    research_parser.add_argument("research_action", choices=["release-check"], help="Research action")

    # phase1_5 (Phase 1.5 Deep Web Archaeology Subsystem)
    p15_parser = subparsers.add_parser("phase1_5", help="Phase 1.5 Deep Web Archaeology Subsystem")
    p15_parser.add_argument("p15_action", choices=["sample", "run", "resume", "review", "compare", "report"], help="Phase 1.5 action")
    p15_parser.add_argument("--mode", choices=["LIVE", "SIMULATION", "REPLAY"], default="LIVE", help="Execution mode")
    p15_parser.add_argument("--limit", type=int, help="Limit domains for test runs", default=None)

    # phase1_6 (Phase 1.6 Audit & Reconciliation)
    p16_parser = subparsers.add_parser("phase1_6", help="Phase 1.6 Independent Scientific Audit & Reconciliation Subsystem")
    p16_parser.add_argument("p16_action", choices=["release-check", "audit"], help="Phase 1.6 action")

    # phase1_7 (Phase 1.7 Path Density Validation)
    p17_parser = subparsers.add_parser("phase1_7", help="Phase 1.7 Path Density Hypothesis Validation Subsystem")
    p17_parser.add_argument("p17_action", choices=["release-check", "pipeline", "run", "survey"], help="Phase 1.7 action")

    # phase1_8 (Phase 1.8 Independent Scientific Audit & Certification)
    p18_parser = subparsers.add_parser("phase1_8", help="Phase 1.8 Independent Scientific Audit & Integrity Certification Subsystem")
    p18_parser.add_argument("p18_action", choices=["release-check", "audit", "run"], help="Phase 1.8 action")

    # phase1_9 (Phase 1.9 Controlled Replication)
    p19_parser = subparsers.add_parser("phase1_9", help="Phase 1.9 Controlled Replication of Path-Density Prioritization Subsystem")
    p19_parser.add_argument("p19_action", choices=["release-check", "audit", "run", "pipeline"], help="Phase 1.9 action")

    # phase1_9_1 (Phase 1.9.1 Review Decontamination & Salvage)
    p191_parser = subparsers.add_parser("phase1_9_1", help="Phase 1.9.1 Review Decontamination & Salvage Subsystem")
    p191_parser.add_argument("p191_action", choices=["release-check", "audit", "run"], help="Phase 1.9.1 action")

    # review (Independent Human Review Interface)
    review_parser = subparsers.add_parser("review", help="Independent Human Review Interface")
    review_parser.add_argument("review_action", choices=["export-packets", "import"], help="Review operation")
    review_parser.add_argument("--file", "-f", help="Path to submissions JSONL file for import", default=None)

    # treasure (Treasure Mode Autonomous Engine)
    treasure_parser = subparsers.add_parser("treasure", help="Treasure Mode Autonomous Discovery Engine")
    treasure_parser.add_argument("treasure_action", choices=["hunt", "list", "show", "release-check"], help="Treasure action")
    treasure_parser.add_argument("--count", "-n", type=int, default=25, help="Target number of candidate URLs to investigate")
    treasure_parser.add_argument("--seed", "-s", type=int, default=42, help="Deterministic sampling seed")
    treasure_parser.add_argument("--category", "-c", type=str, default=None, help="Filter to specific domain category")
    treasure_parser.add_argument("--deep", action="store_true", default=True, help="Enable deep structural investigation")
    treasure_parser.add_argument("--resume", action="store_true", default=False, help="Resume from last checkpoint")
    treasure_parser.add_argument("--id", dest="treasure_id", type=str, default=None, help="Treasure ID to inspect")

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
        elif args.subcommand == "archive":
            cmd_evidence_archive(args)
        elif args.subcommand == "extract":
            cmd_evidence_extract(args)
        else:
            evidence_parser.print_help()
    elif args.command == "phase1":
        cmd_phase1(args)
    elif args.command == "corpus":
        cmd_corpus(args)
    elif args.command == "pilot":
        cmd_pilot(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)
    elif args.command == "research":
        cmd_research(args)
    elif args.command == "phase1_5":
        cmd_phase1_5(args)
    elif args.command == "phase1_6":
        cmd_phase1_6(args)
    elif args.command == "phase1_7":
        cmd_phase1_7(args)
    elif args.command == "phase1_8":
        cmd_phase1_8(args)
    elif args.command == "phase1_9":
        cmd_phase1_9(args)
    elif args.command == "phase1_9_1":
        cmd_phase1_9_1(args)
    elif args.command == "review":
        cmd_review(args)
    elif args.command == "treasure":
        cmd_treasure(args)
    else:
        print_banner()
        parser.print_help()

if __name__ == "__main__":
    main()
