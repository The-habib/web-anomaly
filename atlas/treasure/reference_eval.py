"""
Post-Hoc Reference World Control Evaluator for Project Atlas — Treasure Mode.
Compares blind discoveries against the quarantined historical reference controls
strictly AFTER blind discovery and investigation runs are completed and frozen.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

from atlas.treasure.models import InvestigationRecord

def run_post_hoc_reference_evaluation(
    investigations_file: Path = Path("data/treasure_runs/TREASURE_RUN_0002/investigations.jsonl"),
    reference_domains_file: Path = Path("data/reference_controls/reference_domains.json"),
    output_comparison_file: Path = Path("data/reference_controls/reference_comparison.jsonl")
) -> Dict[str, Any]:
    """
    Execute post-hoc comparison between blind discoveries and reference controls.
    """
    if not reference_domains_file.exists():
        raise FileNotFoundError(f"Reference controls not found at {reference_domains_file}")

    with open(reference_domains_file, "r", encoding="utf-8") as f:
        ref_domains_data = json.load(f)
    
    ref_domain_set = {d["domain"].lower(): d for d in ref_domains_data}

    investigations: List[InvestigationRecord] = []
    if investigations_file.exists():
        with open(investigations_file, "r", encoding="utf-8") as f:
            investigations = [InvestigationRecord(**json.loads(l)) for l in f if l.strip()]

    output_comparison_file.parent.mkdir(parents=True, exist_ok=True)
    comparisons: List[Dict[str, Any]] = []

    reference_recoveries = 0
    new_to_atlas = 0

    for inv in investigations:
        dom_lower = inv.domain.lower()
        is_ref = dom_lower in ref_domain_set
        
        if is_ref:
            classification = "REFERENCE_RECOVERY"
            reference_recoveries += 1
            ref_info = ref_domain_set[dom_lower]
        else:
            classification = "DISCOVERY"
            new_to_atlas += 1
            ref_info = None

        comp_entry = {
            "candidate_id": inv.candidate_id,
            "domain": inv.domain,
            "url": inv.url,
            "path": inv.path,
            "strategy": inv.strategy.value,
            "treasure_score": inv.treasure_score,
            "decision": inv.decision.value,
            "classification": classification,
            "is_reference_landmark": is_ref,
            "reference_context": ref_info
        }
        comparisons.append(comp_entry)

    with open(output_comparison_file, "w", encoding="utf-8") as f:
        for c in comparisons:
            f.write(json.dumps(c) + "\n")

    summary = {
        "total_evaluated": len(investigations),
        "reference_recoveries_count": reference_recoveries,
        "new_to_atlas_count": new_to_atlas,
        "reference_comparison_file": str(output_comparison_file)
    }

    print(f"[+] Post-hoc reference evaluation complete: {reference_recoveries} reference recoveries, {new_to_atlas} new-to-Atlas candidates.")
    return summary
