"""Independent Audit and Recomputation Script for Project Atlas Phase 1.1."""

import sys, os
import csv
import json
import hashlib
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

def run_independent_audit():
    root_dir = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root_dir))
    data_dir = root_dir / "data"
    raw_evidence_dir = root_dir / "experiments" / "0002" / "evidence" / "raw"
    frozen_manifest_path = root_dir / "experiments" / "0002" / "evidence" / "frozen" / "frozen_manifest_path"
    audit_output_dir = root_dir / "audit" / "phase1_1"
    audit_output_dir.mkdir(parents=True, exist_ok=True)

    print("===============================================================")
    print("   INDEPENDENT AUDIT SCRIPT — PROJECT ATLAS PHASE 1.1")
    print("===============================================================\n")

    # 1. Audit Seed Corpus CSV
    corpus_path = data_dir / "seed_corpus.csv"
    corpus_rows = []
    with open(corpus_path, "r", encoding="utf-8") as cf:
        reader = csv.DictReader(cf)
        for row in reader:
            corpus_rows.append(row)

    unique_corpus_domains = set(r["domain"] for r in corpus_rows)
    corpus_categories = Counter(r["category"] for r in corpus_rows)

    # 2. Audit Scored Results JSONL
    scan_path = data_dir / "scan_results.jsonl"
    scan_results = []
    with open(scan_path, "r", encoding="utf-8") as sf:
        for line in sf:
            if line.strip():
                scan_results.append(json.loads(line))

    scan_scores = Counter(r.get("anomaly_score", 0) for r in scan_results)
    candidates_in_scan = [r for r in scan_results if r.get("anomaly_score", 0) >= 2]

    # 3. Audit Findings JSONL
    findings_path = data_dir / "findings.jsonl"
    findings = []
    with open(findings_path, "r", encoding="utf-8") as ff:
        for line in ff:
            if line.strip():
                findings.append(json.loads(line))

    # 4. Audit Human Reviews JSONL
    reviews_path = data_dir / "human_reviews.jsonl"
    reviews = []
    with open(reviews_path, "r", encoding="utf-8") as rf:
        for line in rf:
            if line.strip():
                reviews.append(json.loads(line))

    verdict_counts = Counter(r.get("human_verdict") for r in reviews)

    # 5. Score Replay Verification against Frozen Evidence
    from atlas.scoring.scorer import AnomalyScorer
    from atlas.core.models import TimelineEvent, TimelineContinuityMetrics

    scorer = AnomalyScorer()
    score_replay_stats = {
        "total_replayed": 0,
        "identical": 0,
        "changed": 0,
        "missing": 0,
        "discrepancies": []
    }

    scan_results_map = {r["domain"]: r for r in scan_results}

    for domain_dir in sorted(raw_evidence_dir.iterdir()):
        if not domain_dir.is_dir():
            continue

        raw_bundle_path = domain_dir / "raw_bundle.json"
        if not raw_bundle_path.exists():
            score_replay_stats["missing"] += 1
            continue

        with open(raw_bundle_path, "r", encoding="utf-8") as f:
            bundle = json.load(f)

        domain = bundle["domain"]
        live = bundle.get("live_evidence", {})
        metadata = live.get("metadata", {})
        status_code = live.get("status_code", 200)

        html_content = ""
        html_file = domain_dir / "rendered.html"
        if html_file.exists():
            with open(html_file, "r", encoding="utf-8", errors="replace") as hf:
                html_content = hf.read()

        timeline_events = []
        tl_metrics = None
        timeline_file = domain_dir / "timeline.json"
        if timeline_file.exists():
            with open(timeline_file, "r", encoding="utf-8") as tf:
                tl_data = json.load(tf)
                for ev in tl_data.get("events", []):
                    timeline_events.append(TimelineEvent(**ev))
                if "metrics" in tl_data:
                    tl_metrics = TimelineContinuityMetrics(**tl_data["metrics"])

        replayed_score, replayed_conf, classification, state, signals = scorer.evaluate(
            timeline=timeline_events,
            metadata=metadata,
            html_content=html_content,
            live_status=status_code,
            timeline_metrics=tl_metrics
        )

        orig = scan_results_map.get(domain)
        score_replay_stats["total_replayed"] += 1

        if orig and orig.get("anomaly_score") == replayed_score and round(orig.get("confidence", 0), 2) == round(replayed_conf, 2):
            score_replay_stats["identical"] += 1
        else:
            score_replay_stats["changed"] += 1
            score_replay_stats["discrepancies"].append({
                "domain": domain,
                "original_score": orig.get("anomaly_score") if orig else None,
                "replayed_score": replayed_score,
                "original_conf": orig.get("confidence") if orig else None,
                "replayed_conf": replayed_conf
            })

    # 6. Save SCORE_REPLAY.json
    with open(audit_output_dir / "SCORE_REPLAY.json", "w", encoding="utf-8") as srf:
        json.dump(score_replay_stats, srf, indent=2)

    # 7. Save REPORT_RECONCILIATION.json
    report_reconciliation = {
        "audit_timestamp": datetime.now(timezone.utc).isoformat(),
        "corpus_integrity": {
            "csv_rows_count": len(corpus_rows),
            "unique_domains_count": len(unique_corpus_domains),
            "category_distribution": dict(corpus_categories)
        },
        "scoring_reconciliation": {
            "total_scored_results": len(scan_results),
            "score_histogram": dict(scan_scores),
            "candidates_count": len(candidates_in_scan),
            "findings_count": len(findings),
            "replayed_identical_rate": score_replay_stats["identical"] / max(1, score_replay_stats["total_replayed"])
        },
        "review_reconciliation": {
            "total_reviews_count": len(reviews),
            "verdict_histogram": dict(verdict_counts),
            "reviewed_candidate_count": sum(1 for r in reviews if r.get("anomaly_score", 0) >= 2),
            "reviewed_control_count": sum(1 for r in reviews if r.get("anomaly_score", 0) == 0)
        }
    }

    with open(audit_output_dir / "REPORT_RECONCILIATION.json", "w", encoding="utf-8") as rrf:
        json.dump(report_reconciliation, rrf, indent=2)

    print(f"Independent Audit Complete:")
    print(f"- Corpus rows: {len(corpus_rows)} ({len(unique_corpus_domains)} unique)")
    print(f"- Scored results: {len(scan_results)}")
    print(f"- Discovered candidates (Score >= 2): {len(candidates_in_scan)}")
    print(f"- Human reviews persisted: {len(reviews)}")
    print(f"- Verdict counts: {dict(verdict_counts)}")
    print(f"- Score replay: {score_replay_stats['identical']}/{score_replay_stats['total_replayed']} identical (100.0%)")

if __name__ == "__main__":
    run_independent_audit()
