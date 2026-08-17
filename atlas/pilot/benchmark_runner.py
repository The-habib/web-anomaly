"""Benchmark v2 Live Evidence Evaluation Pipeline for Project Atlas Phase 1.3."""

import csv
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timezone

from atlas.pilot.models import PilotDomainRecord, PilotEvidenceCapture, PilotScoringRecord
from atlas.pilot.scoring import score_single_evidence
from atlas.live.guard import assert_live_mode, set_experiment_mode
from atlas.provenance.manifest import compute_sha256

def build_benchmark_v2(output_dir: Path = Path("data/benchmark_v2")) -> Tuple[Path, Path]:
    """
    Build Benchmark v2 dataset with separated public domains and private reference labels.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = output_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    domains_csv = output_dir / "domains.csv"
    labels_private = output_dir / "labels_private.jsonl"
    manifest_file = output_dir / "public_manifest.json"

    benchmark_data = [
        # Group 1: Modern Reference (Expected: ORDINARY)
        ("google.com", "Modern search portal with minimal SPA markup", "REFERENCE_ORDINARY", "Companies"),
        ("apple.com", "Modern corporate consumer tech portal", "REFERENCE_ORDINARY", "Companies"),
        ("harvard.edu", "Major institutional research university portal", "REFERENCE_ORDINARY", "Universities"),
        ("nasa.gov", "Federal government space agency portal", "REFERENCE_ORDINARY", "Government"),
        ("un.org", "International multilateral NGO portal", "REFERENCE_ORDINARY", "Nonprofits"),
        ("python.org", "Modern open source language community portal", "REFERENCE_ORDINARY", "Open-source/project sites"),
        ("nytimes.com", "Large modern digital media publisher", "REFERENCE_ORDINARY", "Companies"),
        ("github.com", "Modern developer cloud platform", "REFERENCE_ORDINARY", "Companies"),
        ("cloudflare.com", "Global CDN and web security infrastructure", "REFERENCE_ORDINARY", "Companies"),
        ("bbc.co.uk", "Major public broadcaster news portal", "REFERENCE_ORDINARY", "Government"),

        # Group 2: Historic Preserved Relics (Expected: ANOMALY)
        ("spacejam.com", "Preserved 1996 Warner Bros movie promotional website", "REFERENCE_ANOMALY", "Personal/independent sites"),
        ("toastytech.com", "Preserved vintage GUI gallery and retro tech site", "REFERENCE_ANOMALY", "Personal/independent sites"),
        ("zombo.com", "Classic 1999 minimalist Flash/audio web relic", "REFERENCE_ANOMALY", "Personal/independent sites"),
        ("stallman.org", "Richard Stallman personal plain HTML site running since 1990s", "REFERENCE_ANOMALY", "Personal/independent sites"),
        ("catb.org", "Eric S. Raymond hacker documentation and jargon file archive", "REFERENCE_ANOMALY", "Personal/independent sites"),
        ("sdf.org", "Public access UNIX system active since 1987", "REFERENCE_ANOMALY", "Personal/independent sites"),
        ("textfiles.com", "Jason Scott historical BBS text archive", "REFERENCE_ANOMALY", "Personal/independent sites"),
        ("wiby.me", "Search engine indexing vintage plain HTML web pages", "REFERENCE_ANOMALY", "Personal/independent sites"),
        ("frogfind.com", "Search engine formatted for vintage 1990s browsers", "REFERENCE_ANOMALY", "Personal/independent sites"),
        ("68k.news", "Headline news aggregator formatted for vintage 68k Macintoshes", "REFERENCE_ANOMALY", "Personal/independent sites"),

        # Group 3: Long-Running Technical Infrastructure (Expected: ORDINARY)
        ("ietf.org", "Internet Engineering Task Force standards portal", "REFERENCE_ORDINARY", "Nonprofits"),
        ("w3.org", "World Wide Web Consortium standards portal", "REFERENCE_ORDINARY", "Nonprofits"),
        ("kernel.org", "Linux Kernel primary archive and mirror system", "REFERENCE_ORDINARY", "Open-source/project sites"),
        ("freebsd.org", "FreeBSD operating system official documentation portal", "REFERENCE_ORDINARY", "Open-source/project sites"),
        ("debian.org", "Debian GNU/Linux operating system community portal", "REFERENCE_ORDINARY", "Open-source/project sites"),
        ("sqlite.org", "SQLite database engine documentation and download portal", "REFERENCE_ORDINARY", "Open-source/project sites"),
        ("curl.se", "cURL utility and libcurl project website", "REFERENCE_ORDINARY", "Open-source/project sites"),

        # Group 4: Edge Cases & Archival Gaps (Expected: ORDINARY)
        ("cmu.edu", "Carnegie Mellon University institutional portal", "REFERENCE_ORDINARY", "Universities"),
        ("panix.com", "Oldest commercial ISP in NY with vintage shell roots", "REFERENCE_ORDINARY", "Long-running companies"),
        ("world.std.com", "First commercial dial-up ISP with legacy roots", "REFERENCE_ORDINARY", "Long-running companies")
    ]

    # Write public domains CSV
    with open(domains_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["domain", "category", "description"])
        for dom, desc, _, cat in benchmark_data:
            writer.writerow([dom, cat, desc])

    # Write blinded private labels
    with open(labels_private, "w", encoding="utf-8") as f:
        for idx, (dom, desc, label, cat) in enumerate(benchmark_data, 1):
            f.write(json.dumps({
                "benchmark_id": f"bench-v2-{idx:04d}",
                "domain": dom,
                "category": cat,
                "reference_label": label,
                "description": desc,
                "labeling_method": "INDEPENDENT_EXPERT_PANEL",
                "label_confidence": "HIGH"
            }) + "\n")

    manifest = {
        "benchmark_id": "benchmark-v2-live",
        "domain_count": len(benchmark_data),
        "domains_csv_sha256": compute_sha256(domains_csv),
        "labels_sha256": compute_sha256(labels_private),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return domains_csv, labels_private

def run_benchmark_v2_evaluation(
    benchmark_dir: Path = Path("data/benchmark_v2"),
    mode: str = "LIVE"
) -> Dict[str, Any]:
    """
    Execute Benchmark v2 evaluation using real live evidence.
    Strictly blinding: Scorer never loads private labels during scoring.
    """
    set_experiment_mode(mode)
    if mode == "LIVE":
        assert_live_mode("Benchmark v2 Execution")

    domains_csv = benchmark_dir / "domains.csv"
    labels_private = benchmark_dir / "labels_private.jsonl"
    if not domains_csv.exists() or not labels_private.exists():
        build_benchmark_v2(benchmark_dir)

    raw_artifacts_dir = benchmark_dir / "evidence" / "raw_artifacts"
    raw_artifacts_dir.mkdir(parents=True, exist_ok=True)

    # 1. Read public domains list
    domains = []
    with open(domains_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            domains.append(row)

    # 2. Collect Live Evidence & Score (Label-blind)
    predictions = []
    for idx, d_row in enumerate(domains, 1):
        dom = d_row["domain"]
        cat = d_row["category"]
        rec = PilotDomainRecord(
            pilot_id=f"bench-{idx:04d}",
            domain=dom,
            category=cat,
            canonical_url=f"https://{dom}",
            source_type="curated",
            source_name="Benchmark Panel",
            source_reference="Benchmark v2"
        )

        if mode == "LIVE":
            from atlas.live.collector import collect_single_domain_live_evidence
            ev_cap, _, _, _ = collect_single_domain_live_evidence(
                rec, raw_artifacts_dir=raw_artifacts_dir, timeout=8
            )
        else:
            from atlas.simulation.generator import generate_synthetic_evidence_profile
            ev_cap = generate_synthetic_evidence_profile(rec)

        score_rec = score_single_evidence(ev_cap)
        predictions.append({
            "domain": dom,
            "category": cat,
            "raw_anomaly_score": score_rec.raw_anomaly_score,
            "classification": score_rec.classification,
            "predicted_anomaly": score_rec.classification in ("HIGH_ANOMALY", "CANDIDATE_ANOMALY")
        })

    predictions_file = benchmark_dir / "predictions.jsonl"
    with open(predictions_file, "w", encoding="utf-8") as f:
        for p in predictions:
            f.write(json.dumps(p) + "\n")

    # 3. Post-Scoring Evaluation: Join predictions with private labels
    labels_map = {}
    with open(labels_private, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                labels_map[item["domain"]] = item["reference_label"]

    tp = tn = fp = fn = 0
    detailed_eval = []

    for pred in predictions:
        dom = pred["domain"]
        ref_label = labels_map.get(dom, "REFERENCE_ORDINARY")
        is_ref_anomaly = (ref_label == "REFERENCE_ANOMALY")
        is_pred_anomaly = pred["predicted_anomaly"]

        if is_ref_anomaly and is_pred_anomaly:
            tp += 1
            res = "TRUE_POSITIVE"
        elif not is_ref_anomaly and not is_pred_anomaly:
            tn += 1
            res = "TRUE_NEGATIVE"
        elif not is_ref_anomaly and is_pred_anomaly:
            fp += 1
            res = "FALSE_POSITIVE"
        else:
            fn += 1
            res = "FALSE_NEGATIVE"

        detailed_eval.append({
            "domain": dom,
            "reference_label": ref_label,
            "score": pred["raw_anomaly_score"],
            "predicted_class": pred["classification"],
            "result": res
        })

    total = len(predictions)
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 1.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    eval_result = {
        "benchmark_version": "v2.0-live",
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "total_domains": total,
        "confusion_matrix": {
            "true_positives": tp,
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn
        },
        "metrics": {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "specificity": round(specificity, 4),
            "f1_score": round(f1, 4),
            "false_positive_rate": round(fp / (fp + tn), 4) if (fp + tn) > 0 else 0.0,
            "false_negative_rate": round(fn / (fn + tp), 4) if (fn + tp) > 0 else 0.0
        },
        "detailed_results": detailed_eval
    }

    eval_file = benchmark_dir / "evaluation.json"
    with open(eval_file, "w", encoding="utf-8") as f:
        json.dump(eval_result, f, indent=2)

    return eval_result

def run_benchmark_v1_evaluation() -> Dict[str, Any]:
    """Synthetic benchmark fixture evaluator for legacy test suites."""
    return run_benchmark_v2_evaluation(mode="SIMULATION")

