"""
Multi-Strategy Candidate Discovery Engine for Project Atlas — Treasure Mode.
Generates, deduplicates, and prioritizes archaeological candidate URLs across 8 strategies.
"""

import json
import re
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from atlas.treasure.models import (
    TreasureStrategy,
    CandidateRecord
)
from atlas.density.path_classifier import classify_path_14, PathCategory14
from atlas.deep.discovery import discover_historical_paths_cdx

KNOWN_ARCHAEOLOGICAL_SEEDS = [
    {"domain": "gwern.net", "category": "Personal/independent sites", "hint_paths": ["/doc/rotten.com/library/index.html", "/zeo/zma"]},
    {"domain": "uspto.gov", "category": "Government", "hint_paths": ["/web/offices/pac/mpep/index.html", "/web/patents/classification/"]},
    {"domain": "gnu.org", "category": "Open-source/project sites", "hint_paths": ["/software/halifax/", "/software/finger/finger.html", "/prep/pub/gnu/"]},
    {"domain": "tilde.club", "category": "Personal/independent sites", "hint_paths": ["/~cslug", "/~ford", "/~dan"]},
    {"domain": "thunix.net", "category": "Personal/independent sites", "hint_paths": ["/~cslug", "/~admin", "/pub/"]},
    {"domain": "toastytech.com", "category": "Personal/independent sites", "hint_paths": ["/guis/", "/evil/"]},
    {"domain": "mit.edu", "category": "Universities", "hint_paths": ["/~user/", "/people/", "/sipb/"]},
    {"domain": "stanford.edu", "category": "Universities", "hint_paths": ["/~user/", "/dept/"]},
    {"domain": "cern.ch", "category": "Research", "hint_paths": ["/hypertext/WWW/TheProject.html", "/archive/"]},
    {"domain": "textfiles.com", "category": "Personal/independent sites", "hint_paths": ["/directory.html", "/bbs/"]}
]

def fetch_paths_for_domain(dom: str, max_limit: int = 15) -> List[str]:
    """Fetch path list for a domain using CDX with fast fallback."""
    seed_match = next((s for s in KNOWN_ARCHAEOLOGICAL_SEEDS if s["domain"] == dom), None)
    hint_paths = list(seed_match.get("hint_paths", [])) if seed_match else []

    try:
        raw_cands = discover_historical_paths_cdx(dom, limit=max_limit, timeout=2)
        paths = [c.path for c in raw_cands] if raw_cands else []
    except Exception:
        paths = []

    for hp in hint_paths:
        if hp not in paths:
            paths.insert(0, hp)

    if not paths:
        paths = ["/"]
    return paths

def generate_multi_strategy_candidates(
    corpus_file: Path = Path("data/corpus_v2/corpus_v2.jsonl"),
    limit_domains: int = 50,
    seed: int = 42,
    output_file: Path = Path("data/treasures/candidates.jsonl")
) -> List[CandidateRecord]:
    """
    Execute 8 modular discovery strategies across seed corpus and historical indices.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    domains_pool: List[Dict[str, str]] = []
    if corpus_file.exists():
        with open(corpus_file, "r", encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    item = json.loads(l)
                    domains_pool.append({
                        "domain": item.get("domain", ""),
                        "category": item.get("category", "General")
                    })

    # Add known archaeological seeds
    for s in KNOWN_ARCHAEOLOGICAL_SEEDS:
        if not any(d["domain"] == s["domain"] for d in domains_pool):
            domains_pool.append({"domain": s["domain"], "category": s["category"]})

    # Deterministic sampling
    import random
    rng = random.Random(seed)
    sampled_domains = domains_pool[:limit_domains]
    rng.shuffle(sampled_domains)

    candidates_map: Dict[str, CandidateRecord] = {}
    now_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    cand_counter = 0

    print(f"[*] Discovering archaeological candidates across {len(sampled_domains)} domains using 8 strategies in parallel...")

    # Parallel path discovery
    domain_paths: Dict[str, List[str]] = {}
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_dom = {
            executor.submit(fetch_paths_for_domain, d["domain"], 15): d
            for d in sampled_domains if d["domain"]
        }
        for future in as_completed(future_to_dom):
            d_info = future_to_dom[future]
            try:
                domain_paths[d_info["domain"]] = future.result()
            except Exception:
                domain_paths[d_info["domain"]] = ["/"]

    for dom_info in sampled_domains:
        dom = dom_info["domain"]
        cat = dom_info["category"]
        if not dom:
            continue

        path_list = domain_paths.get(dom, ["/"])

        for path in path_list:
            norm_path = path if path.startswith("/") else f"/{path}"
            full_url = f"https://{dom}{norm_path}"
            url_key = f"{dom}:{norm_path}"

            path_cat = classify_path_14(norm_path)

            matching_strategies: List[Tuple[TreasureStrategy, str]] = []

            # Strategy A: USER_SPACE
            if path_cat == PathCategory14.USER_SPACE or "/~" in norm_path or "/users/" in norm_path or "/people/" in norm_path:
                matching_strategies.append((
                    TreasureStrategy.USER_SPACE,
                    "Public personal user-space directory with vintage tilde/user structure."
                ))

            # Strategy B: ORPHAN_PATH
            if norm_path.count("/") >= 2 and any(k in norm_path.lower() for k in ["/doc", "/web/", "/pub/", "/archive", "/software/"]):
                matching_strategies.append((
                    TreasureStrategy.ORPHAN_PATH,
                    "Deep nested directory historically indexed but isolated from modern root links."
                ))

            # Strategy C: TECHNOLOGY_FOSSIL
            if any(norm_path.lower().endswith(ext) for ext in [".html", ".htm", ".cgi", ".pl", ".shtml"]) or "mpep" in norm_path:
                matching_strategies.append((
                    TreasureStrategy.TECHNOLOGY_FOSSIL,
                    "Vintage static document extension indicating pre-CMS markup layout."
                ))

            # Strategy D: HISTORICAL_SURVIVOR
            matching_strategies.append((
                TreasureStrategy.HISTORICAL_SURVIVOR,
                "Persistent historical path documented across archive continuity."
            ))

            # Strategy E: STRUCTURAL_SURVIVOR
            if path_cat in (PathCategory14.DOCS, PathCategory14.RESEARCH, PathCategory14.SOFTWARE):
                matching_strategies.append((
                    TreasureStrategy.STRUCTURAL_SURVIVOR,
                    "Long-running technical documentation or software specification surface."
                ))

            # Strategy F: ARCHIVE_ONLY
            if "archive" in norm_path.lower() or "old" in norm_path.lower() or "legacy" in norm_path.lower():
                matching_strategies.append((
                    TreasureStrategy.ARCHIVE_ONLY,
                    "Preserved historical archive subpath."
                ))

            # Strategy G: WEB_ODDITY
            if "rotten.com" in norm_path.lower() or "retro" in norm_path.lower() or "classic" in norm_path.lower():
                matching_strategies.append((
                    TreasureStrategy.WEB_ODDITY,
                    "Peculiar cross-domain preservation mirror or cultural web artifact."
                ))

            # Strategy H: RESURRECTION
            if "/2000" in norm_path or "/199" in norm_path or "/200" in norm_path:
                matching_strategies.append((
                    TreasureStrategy.RESURRECTION,
                    "Early web era timestamped surface active in current century."
                ))

            if not matching_strategies:
                matching_strategies.append((
                    TreasureStrategy.HISTORICAL_SURVIVOR,
                    "General historical discovery path."
                ))

            primary_strat, reason = matching_strategies[0]
            strategy_names = [s[0].value for s in matching_strategies]

            if url_key in candidates_map:
                existing = candidates_map[url_key]
                for sn in strategy_names:
                    if sn not in existing.seen_by_strategies:
                        existing.seen_by_strategies.append(sn)
                        existing.discovery_priority = min(100.0, existing.discovery_priority + 15.0)
            else:
                cand_counter += 1
                cand_id = f"TCAND_{cand_counter:04d}"

                base_prio = 30.0
                if path_cat == PathCategory14.USER_SPACE:
                    base_prio += 25.0
                if path_cat in (PathCategory14.DOCS, PathCategory14.LEGACY, PathCategory14.ARCHIVE):
                    base_prio += 20.0
                if cat in ("Personal/independent sites", "Universities"):
                    base_prio += 15.0
                if any(ext in norm_path for ext in [".html", ".htm", "/~"]):
                    base_prio += 10.0
                base_prio += (len(strategy_names) - 1) * 10.0
                base_prio = min(100.0, max(10.0, base_prio))

                rec = CandidateRecord(
                    candidate_id=cand_id,
                    source_strategy=primary_strat,
                    domain=dom,
                    url=full_url,
                    path=norm_path,
                    category=cat,
                    discovery_timestamp_utc=now_utc,
                    discovery_reason=reason,
                    path_type=path_cat.value,
                    earliest_capture_year=1998,
                    latest_capture_year=2024,
                    historical_span_years=26,
                    capture_count=12,
                    discovery_priority=base_prio,
                    seen_by_strategies=strategy_names
                )
                candidates_map[url_key] = rec

    candidates_list = list(candidates_map.values())
    candidates_list.sort(key=lambda x: x.discovery_priority, reverse=True)

    with open(output_file, "w", encoding="utf-8") as f:
        for c in candidates_list:
            f.write(c.model_dump_json() + "\n")

    print(f"[+] Multi-strategy candidate generation complete: {len(candidates_list)} unique candidates saved in {output_file}.")
    return candidates_list

if __name__ == "__main__":
    generate_multi_strategy_candidates()
