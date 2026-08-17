"""Independent Benchmark v2 Auditor for Project Atlas Phase 1.4.
Strictly decoupled from atlas modules: reads raw CSV and JSONL files directly.
"""

import csv
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any

def sha256_file(p: Path) -> str:
    if not p.exists():
        return ""
    return hashlib.sha256(p.read_bytes()).hexdigest()

def audit_benchmark_inventory(benchmark_dir: Path = Path("data/benchmark_v2")) -> Dict[str, Any]:
    inventory = {}
    for p in sorted(benchmark_dir.rglob("*")):
        if p.is_file():
            rel_path = str(p.relative_to(benchmark_dir))
            line_count = 0
            if p.suffix in (".csv", ".jsonl", ".json", ".html"):
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        line_count = sum(1 for _ in f)
                except Exception:
                    line_count = -1

            inventory[rel_path] = {
                "size_bytes": p.stat().st_size,
                "sha256": sha256_file(p),
                "line_count": line_count
            }
    return inventory

def run_independent_benchmark_audit(
    benchmark_dir: Path = Path("data/benchmark_v2"),
    output_dir: Path = Path("audit/phase1_4")
) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    domains_csv = benchmark_dir / "domains.csv"
    labels_file = benchmark_dir / "labels_private.jsonl"
    predictions_file = benchmark_dir / "predictions.jsonl"

    # 1. Read Domains CSV
    domains_list = []
    with open(domains_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            domains_list.append(row["domain"].strip())

    # 2. Read Private Labels
    labels_map = {}
    label_records = []
    with open(labels_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                dom = rec["domain"].strip()
                labels_map[dom] = rec
                label_records.append(rec)

    # 3. Read Predictions
    preds_map = {}
    pred_records = []
    with open(predictions_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                dom = rec["domain"].strip()
                preds_map[dom] = rec
                pred_records.append(rec)

    # 4. Join Audit
    missing_in_labels = [d for d in domains_list if d not in labels_map]
    missing_in_preds = [d for d in domains_list if d not in preds_map]
    extra_in_labels = [d for d in labels_map if d not in domains_list]
    extra_in_preds = [d for d in preds_map if d not in domains_list]

    join_audit = {
        "domains_csv_count": len(domains_list),
        "labels_count": len(label_records),
        "predictions_count": len(pred_records),
        "unique_domains_in_csv": len(set(domains_list)),
        "unique_domains_in_labels": len(set(labels_map.keys())),
        "unique_domains_in_preds": len(set(preds_map.keys())),
        "is_1_to_1_join": (
            len(domains_list) == len(labels_map) == len(preds_map) and
            len(missing_in_labels) == 0 and len(missing_in_preds) == 0
        ),
        "missing_in_labels": missing_in_labels,
        "missing_in_predictions": missing_in_preds,
        "extra_in_labels": extra_in_labels,
        "extra_in_predictions": extra_in_preds
    }

    with open(output_dir / "benchmark_join_audit.json", "w") as f:
        json.dump(join_audit, f, indent=2)

    # 5. Case-by-Case Confusion Matrix Calculation
    tp = tn = fp = fn = 0
    case_reconciliation = []

    for dom in domains_list:
        label_rec = labels_map.get(dom, {})
        pred_rec = preds_map.get(dom, {})

        ref_label = label_rec.get("reference_label", "REFERENCE_ORDINARY")
        score = pred_rec.get("raw_anomaly_score", 0.0)
        pred_class = pred_rec.get("classification", "ORDINARY")
        pred_anomaly = pred_rec.get("predicted_anomaly", (pred_class in ("HIGH_ANOMALY", "CANDIDATE_ANOMALY") or score >= 40.0))

        is_ref_anomaly = (ref_label == "REFERENCE_ANOMALY")

        if is_ref_anomaly and pred_anomaly:
            res = "TRUE_POSITIVE"
            tp += 1
        elif not is_ref_anomaly and not pred_anomaly:
            res = "TRUE_NEGATIVE"
            tn += 1
        elif not is_ref_anomaly and pred_anomaly:
            res = "FALSE_POSITIVE"
            fp += 1
        else:
            res = "FALSE_NEGATIVE"
            fn += 1

        case_reconciliation.append({
            "domain": dom,
            "category": label_rec.get("category", ""),
            "reference_label": ref_label,
            "raw_anomaly_score": score,
            "classification": pred_class,
            "predicted_anomaly": pred_anomaly,
            "result": res
        })

    with open(output_dir / "benchmark_case_reconciliation.jsonl", "w") as f:
        for c in case_reconciliation:
            f.write(json.dumps(c) + "\n")

    total = len(domains_list)
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 1.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    metrics_summary = {
        "dataset_analyzed": str(predictions_file),
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
        }
    }

    with open(output_dir / "metric_reconciliation.json", "w") as f:
        json.dump(metrics_summary, f, indent=2)

    inventory = audit_benchmark_inventory(benchmark_dir)
    with open(output_dir / "benchmark_inventory.json", "w") as f:
        json.dump(inventory, f, indent=2)

    return {
        "join_audit": join_audit,
        "metrics": metrics_summary,
        "inventory": inventory
    }

if __name__ == "__main__":
    res = run_independent_benchmark_audit()
    print("Independent Benchmark Audit Completed.")
    print("Join Audit:", res["join_audit"]["is_1_to_1_join"])
    print("Confusion Matrix:", res["metrics"]["confusion_matrix"])
    print("Metrics:", res["metrics"]["metrics"])
