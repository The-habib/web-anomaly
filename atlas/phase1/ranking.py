"""Candidate ranking and report compilation engine for Project Atlas Phase 1."""

import json
from pathlib import Path
from typing import Dict, Any, List
from atlas.phase1.config import (
    SCAN_RESULTS_JSONL, FINDINGS_JSONL,
    NEAR_MISSES_JSONL, PHASE1_REPORTS_DIR
)
from atlas.core.logger import logger

def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    records = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    return records

def generate_candidate_rankings() -> Dict[str, Path]:
    """
    Generate multi-dimensional rankings and threshold summaries across the scored corpus.
    """
    all_results = load_jsonl(SCAN_RESULTS_JSONL)
    findings = load_jsonl(FINDINGS_JSONL)
    near_misses = load_jsonl(NEAR_MISSES_JSONL)

    reports = {}

    # 1. TOP_100_CANDIDATES.md (Ranking A: Anomaly Score)
    top_score = sorted(all_results, key=lambda x: (x["anomaly_score"], x["confidence"]), reverse=True)[:100]
    r_a_path = PHASE1_REPORTS_DIR / "TOP_100_CANDIDATES.md"
    with open(r_a_path, "w", encoding="utf-8") as f:
        f.write("# Top 100 Candidates by Anomaly Score (Ranking A)\n\n")
        f.write("| Rank | Domain | Category | Score | Conf | Evidence State | Classification | Triggered Signals |\n")
        f.write("| :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |\n")
        for idx, r in enumerate(top_score, start=1):
            signals_str = ", ".join([s["name"] for s in r.get("signals", []) if s.get("score_awarded", 0) > 0]) or "None"
            f.write(f"| {idx} | `{r['domain']}` | {r['category']} | **{r['anomaly_score']}** | {r['confidence']:.2f} | `[{r['evidence_state']}]` | {r['classification']} | {signals_str} |\n")
    reports["top_100"] = r_a_path

    # 2. TOP_50_HIGH_CONFIDENCE.md (Ranking B: Confidence Score)
    top_conf = sorted([r for r in all_results if r["anomaly_score"] > 0], key=lambda x: (x["confidence"], x["anomaly_score"]), reverse=True)[:50]
    r_b_path = PHASE1_REPORTS_DIR / "TOP_50_HIGH_CONFIDENCE.md"
    with open(r_b_path, "w", encoding="utf-8") as f:
        f.write("# Top 50 High-Confidence Candidates (Ranking B)\n\n")
        f.write("| Rank | Domain | Category | Confidence | Score | Evidence State | Classification | Observed Facts |\n")
        f.write("| :---: | :--- | :--- | :---: | :---: | :---: | :--- | :--- |\n")
        for idx, r in enumerate(top_conf, start=1):
            facts = []
            for s in r.get("signals", []):
                facts.extend(s.get("observed_facts", []))
            facts_str = "; ".join(facts[:2]) if facts else "Standard verified history"
            f.write(f"| {idx} | `{r['domain']}` | {r['category']} | **{r['confidence']:.2f}** | {r['anomaly_score']} | `[{r['evidence_state']}]` | {r['classification']} | {facts_str} |\n")
    reports["top_50_conf"] = r_b_path

    # 3. TOP_NEAR_MISSES.md
    r_nm_path = PHASE1_REPORTS_DIR / "TOP_NEAR_MISSES.md"
    with open(r_nm_path, "w", encoding="utf-8") as f:
        f.write("# Top Near-Miss Candidates & Sub-Threshold Signals\n\n")
        f.write("Near-misses represent candidate domains that scored slightly below the major discovery threshold (Score 1–4) or exhibited long spans with sparse archive captures.\n\n")
        f.write("| Domain | Category | Score | Conf | Span (Yrs) | Observed Ratio | Continuity Claim | Notes |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |\n")
        for r in near_misses[:50]:
            tl = r.get("timeline_metrics", {})
            f.write(f"| `{r['domain']}` | {r['category']} | {r['anomaly_score']} | {r['confidence']:.2f} | {tl.get('years_span', 0)} | {tl.get('observed_year_ratio', 0.0)*100:.1f}% | `{tl.get('continuity_claim', 'N/A')}` | Sparse captures / archive gap |\n")
    reports["near_misses"] = r_nm_path

    # 4. ZERO_SCORE_SUMMARY.md
    zero_scores = [r for r in all_results if r["anomaly_score"] == 0]
    r_zs_path = PHASE1_REPORTS_DIR / "ZERO_SCORE_SUMMARY.md"
    with open(r_zs_path, "w", encoding="utf-8") as f:
        f.write("# Zero-Score Baseline Population Analysis\n\n")
        f.write(f"Total Zero-Score Domains: **{len(zero_scores):,}** ({len(zero_scores)/max(1, len(all_results))*100:.1f}% of total corpus)\n\n")
        
        # Category breakdown of zero scores
        zero_by_cat = {}
        for z in zero_scores:
            cat = z["category"]
            zero_by_cat[cat] = zero_by_cat.get(cat, 0) + 1

        f.write("## Zero-Score Distribution by Category\n\n")
        f.write("| Category | Zero-Score Count | Category Share |\n")
        f.write("| :--- | :---: | :---: |\n")
        for cat, cnt in zero_by_cat.items():
            f.write(f"| **{cat}** | {cnt:,} | {cnt/len(zero_scores)*100:.1f}% |\n")
        
        f.write("\n## Characteristics of Zero-Score Web Surfaces\n\n")
        f.write("- Modern HTML5 layouts without legacy markup fossils.\n")
        f.write("- Consistent standard HTTP headers, modern CMS frameworks, and standard robots.txt policies.\n")
        f.write("- Lack of verified historical disappearance/resurrection intervals.\n")
    reports["zero_score"] = r_zs_path

    logger.info("Candidate rankings and summaries generated successfully.")
    return reports
