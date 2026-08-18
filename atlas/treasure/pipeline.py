"""
Master Autonomous Pipeline Coordinator for Project Atlas — Treasure Mode.
Coordinates candidate discovery, prioritized adaptive investigations, treasure promotion,
lineage tracing, checkpointing, and experiment ledger persistence.
"""

import json
import time
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

from atlas.treasure.models import (
    TreasureRecord,
    InvestigationRecord,
    CandidateRecord,
    TreasureDecision,
    RunCheckpoint
)
from atlas.treasure.discovery import generate_multi_strategy_candidates
from atlas.treasure.investigator import run_adaptive_investigations
from atlas.treasure.dossier import publish_treasures

def execute_treasure_hunt(
    run_id: str = "TREASURE_RUN_0001",
    count: int = 25,
    seed: int = 42,
    category: Optional[str] = None,
    deep: bool = True,
    resume: bool = False,
    data_dir: Path = Path("data/treasures"),
    reports_dir: Path = Path("reports"),
    experiment_dir: Optional[Path] = Path("experiments/treasure_0001")
) -> Dict[str, Any]:
    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_file = data_dir / "checkpoint.json"

    start_time_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    start_ts = time.time()

    print("===============================================================")
    print("       PROJECT ATLAS — AUTONOMOUS TREASURE HUNT ENGINE")
    print(f"   Run ID: {run_id} | Seed: {seed} | Target Limit: {count}")
    print("===============================================================")

    # 1. Candidate Generation
    cand_file = data_dir / "candidates.jsonl"
    if not cand_file.exists() or not resume:
        candidates = generate_multi_strategy_candidates(
            limit_domains=max(50, count * 2),
            seed=seed,
            output_file=cand_file
        )
    else:
        with open(cand_file, "r", encoding="utf-8") as f:
            candidates = [CandidateRecord(**json.loads(l)) for l in f if l.strip()]

    # 2. Adaptive Investigation
    all_invs, validated_invs = run_adaptive_investigations(
        candidates_file=cand_file,
        max_investigate=count,
        output_dir=data_dir,
        max_workers=10
    )

    # 3. Publish Treasures & Dossiers
    treasures, lineages = publish_treasures(
        validated_investigations=validated_invs,
        output_dir=data_dir,
        reports_dir=reports_dir
    )

    # Record dismissed and false positives
    dismissed = [inv for inv in all_invs if inv.decision == TreasureDecision.DISMISSED]
    false_pos = [inv for inv in all_invs if inv.decision == TreasureDecision.FALSE_POSITIVE]
    pending = [inv for inv in all_invs if inv.decision == TreasureDecision.TREASURE_PENDING]

    with open(data_dir / "dismissed.jsonl", "w", encoding="utf-8") as f:
        for d in dismissed:
            f.write(d.model_dump_json() + "\n")

    with open(data_dir / "false_positives.jsonl", "w", encoding="utf-8") as f:
        for fp in false_pos:
            f.write(fp.model_dump_json() + "\n")

    elapsed = round(time.time() - start_ts, 2)
    end_time_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Strategy breakdown
    strat_counts: Dict[str, Dict[str, int]] = {}
    for c in candidates:
        strat = c.source_strategy.value
        if strat not in strat_counts:
            strat_counts[strat] = {"candidates": 0, "investigated": 0, "validated": 0}
        strat_counts[strat]["candidates"] += 1

    for inv in all_invs:
        strat = inv.strategy.value
        if strat in strat_counts:
            strat_counts[strat]["investigated"] += 1

    for tr in treasures:
        strat = tr.strategy.value
        if strat in strat_counts:
            strat_counts[strat]["validated"] += 1

    best_strat = max(strat_counts.items(), key=lambda x: (x[1]["validated"], x[1]["investigated"]))[0] if strat_counts else "HISTORICAL_SURVIVOR"

    summary = {
        "run_id": run_id,
        "status": "COMPLETED",
        "seed": seed,
        "start_time_utc": start_time_utc,
        "end_time_utc": end_time_utc,
        "elapsed_seconds": elapsed,
        "candidates_discovered_count": len(candidates),
        "candidates_investigated_count": len(all_invs),
        "validated_treasures_count": len(treasures),
        "pending_treasures_count": len(pending),
        "dismissed_count": len(dismissed),
        "false_positives_count": len(false_pos),
        "best_strategy": best_strat,
        "strategy_performance": strat_counts,
        "top_treasures": [
            {
                "rank": idx,
                "treasure_id": t.treasure_id,
                "title": t.title,
                "domain": t.domain,
                "path": t.path,
                "score": t.treasure_score,
                "difficulty": t.discovery_difficulty.value
            }
            for idx, t in enumerate(treasures, 1)
        ]
    }

    # Save checkpoint
    chk = RunCheckpoint(
        run_id=run_id,
        seed=seed,
        start_time_utc=start_time_utc,
        completed_candidate_ids=[inv.candidate_id for inv in all_invs],
        pending_candidate_ids=[],
        investigated_count=len(all_invs),
        validated_treasure_ids=[t.treasure_id for t in treasures],
        dismissed_count=len(dismissed),
        false_positive_count=len(false_pos),
        is_completed=True
    )
    with open(checkpoint_file, "w", encoding="utf-8") as f:
        f.write(chk.model_dump_json(indent=2))

    # Persist experiment folder
    if experiment_dir:
        experiment_dir.mkdir(parents=True, exist_ok=True)
        with open(experiment_dir / "results.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        with open(experiment_dir / "run_config.json", "w", encoding="utf-8") as f:
            json.dump({
                "run_id": run_id,
                "seed": seed,
                "target_count": count,
                "deep": deep,
                "start_time_utc": start_time_utc
            }, f, indent=2)

        with open(experiment_dir / "candidate_summary.json", "w", encoding="utf-8") as f:
            json.dump({
                "total_candidates": len(candidates),
                "investigated": len(all_invs),
                "validated": len(treasures),
                "strategy_breakdown": strat_counts
            }, f, indent=2)

        protocol_md = f"""# Project Atlas — Treasure Run #{run_id} Protocol

## Mission Objective
Autonomously discover, investigate, validate, and preserve authentic unmodernized archaeological web survivals across 8 multi-channel strategies.

## Parameters
- **Target Limit**: {count} investigated URLs
- **Seed**: {seed}
- **Strategies**: 8 modular discovery channels
- **Budget Limits**: Max 5 requests per domain, 5s timeout, SHA-256 evidence hashing.
"""
        (experiment_dir / "protocol.md").write_text(protocol_md.strip() + "\n", encoding="utf-8")

        notes_md = f"""# Project Atlas — Treasure Run #{run_id} Research Notes

- Total Candidates Discovered: {len(candidates)}
- Total Investigated: {len(all_invs)}
- Validated Treasures: {len(treasures)}
- Top Finding: {treasures[0].title if treasures else 'None'} ({treasures[0].full_url if treasures else ''})
- Execution Duration: {elapsed}s
"""
        (experiment_dir / "notes.md").write_text(notes_md.strip() + "\n", encoding="utf-8")

    return summary
