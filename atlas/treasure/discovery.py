"""
Multi-Strategy Candidate Discovery Engine for Project Atlas — Treasure Mode.
Generates, deduplicates, and prioritizes archaeological candidate URLs across 8 independent
discovery channels using authentic archival index queries and real historical metadata.
"""

import json
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from atlas.treasure.models import (
    TreasureStrategy,
    CandidateRecord,
    CandidateState
)
from atlas.treasure.guard import ExecutionMode, assert_live_blind_isolation
from atlas.density.path_classifier import classify_path_14, PathCategory14
from atlas.deep.discovery import discover_historical_paths_cdx
from atlas.deep.models import PathCandidate, PathCategory

def fetch_domain_cdx_candidates(dom: str, max_limit: int = 25, timeout: int = 4) -> List[PathCandidate]:
    """
    Fetch authentic historical and structural path candidates for a domain using live Wayback CDX,
    falling back to live homepage link extraction and public robots.txt paths.
    """
    candidates: List[PathCandidate] = []
    seen_paths = set()

    # 1. Try Live Wayback CDX
    try:
        raw_cands = discover_historical_paths_cdx(dom, limit=max_limit, timeout=timeout)
        if raw_cands:
            for c in raw_cands:
                if c.path not in seen_paths:
                    seen_paths.add(c.path)
                    candidates.append(c)
    except Exception:
        pass

    # 2. Live Homepage & Public Index Discovery
    if len(candidates) < 5:
        try:
            resp = requests.get(
                f"https://{dom}/",
                headers={"User-Agent": "ProjectAtlas-Archaeologist/2.0 (+https://github.com/The-habib/web-anomaly)"},
                timeout=timeout,
                allow_redirects=True
            )
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for a_tag in soup.find_all("a", href=True):
                    href = a_tag["href"].strip()
                    parsed = urlparse(href)
                    if not parsed.netloc or parsed.netloc == dom or parsed.netloc.endswith("." + dom):
                        p = parsed.path
                        if p and p != "/" and not p.startswith(("/static", "/assets", "/cdn-cgi", "/wp-content", "/wp-includes")):
                            if not any(p.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".css", ".js", ".ico"]):
                                if p not in seen_paths:
                                    seen_paths.add(p)
                                    candidates.append(PathCandidate(
                                        domain=dom,
                                        candidate_url=f"https://{dom}{p}",
                                        path=p,
                                        path_category=PathCategory.GENERAL_DIRECTORY,
                                        discovery_source="LIVE_ROOT_LINK",
                                        first_observed_year=None,
                                        last_observed_year=None,
                                        capture_count=1
                                    ))
                                    if len(candidates) >= max_limit:
                                        break
        except Exception:
            pass

    # Always ensure root is in candidate list
    if "/" not in seen_paths:
        candidates.insert(0, PathCandidate(
            domain=dom,
            candidate_url=f"https://{dom}/",
            path="/",
            path_category=PathCategory.GENERAL_DIRECTORY,
            discovery_source="LIVE_ROOT",
            first_observed_year=None,
            last_observed_year=None,
            capture_count=1
        ))

    return candidates

def evaluate_path_strategies(norm_path: str, path_cat: PathCategory14) -> List[Tuple[TreasureStrategy, str]]:
    """
    Evaluate which of the 8 archaeological strategies apply to a candidate path.
    Strictly rule-based DOM/URL pattern analysis without domain hardcoding.
    """
    matching_strategies: List[Tuple[TreasureStrategy, str]] = []
    lower_path = norm_path.lower()

    # 1. Strategy A: USER_SPACE
    if path_cat == PathCategory14.USER_SPACE or "/~" in lower_path or "/users/" in lower_path or "/people/" in lower_path or "/homepages/" in lower_path or "/staff/" in lower_path:
        matching_strategies.append((
            TreasureStrategy.USER_SPACE,
            "Public personal user-space directory matching vintage tilde or multi-user structure."
        ))

    # 2. Strategy B: ORPHAN_PATH
    if norm_path.count("/") >= 2 and any(k in lower_path for k in ["/doc", "/web/", "/pub/", "/archive", "/software/", "/legacy/"]):
        matching_strategies.append((
            TreasureStrategy.ORPHAN_PATH,
            "Deep nested directory historically indexed with high probability of isolation from modern root navigation."
        ))

    # 3. Strategy C: TECHNOLOGY_FOSSIL
    if any(lower_path.endswith(ext) for ext in [".html", ".htm", ".cgi", ".pl", ".shtml", ".txt", ".cfm"]):
        matching_strategies.append((
            TreasureStrategy.TECHNOLOGY_FOSSIL,
            "Vintage static document extension or CGI script indicating pre-CMS markup layout."
        ))

    # 4. Strategy D: HISTORICAL_SURVIVOR
    matching_strategies.append((
        TreasureStrategy.HISTORICAL_SURVIVOR,
        "Historical path documented across public archival continuity."
    ))

    # 5. Strategy E: STRUCTURAL_SURVIVOR
    if path_cat in (PathCategory14.DOCS, PathCategory14.RESEARCH, PathCategory14.SOFTWARE) or any(k in lower_path for k in ["/rfc", "/man", "/manual", "/spec"]):
        matching_strategies.append((
            TreasureStrategy.STRUCTURAL_SURVIVOR,
            "Long-running technical documentation, software repository, or specification surface."
        ))

    # 6. Strategy F: ARCHIVE_ONLY
    if any(k in lower_path for k in ["/archive", "/archives", "/old", "/legacy", "/history", "/retro", "/classic"]):
        matching_strategies.append((
            TreasureStrategy.ARCHIVE_ONLY,
            "Dedicated historical archive or legacy preservation subpath."
        ))

    # 7. Strategy G: WEB_ODDITY
    if any(k in lower_path for k in ["/mirror", "/bbs", "/gopher", "/curiosities", "/oddities", "/fun", "/museum"]):
        matching_strategies.append((
            TreasureStrategy.WEB_ODDITY,
            "Peculiar mirror, vintage computer museum, or cultural web artifact."
        ))

    # 8. Strategy H: RESURRECTION
    if any(f"/{yr}" in lower_path for yr in range(1990, 2006)):
        matching_strategies.append((
            TreasureStrategy.RESURRECTION,
            "Early web era timestamped directory surface active in the current century."
        ))

    return matching_strategies

def generate_multi_strategy_candidates(
    sampled_domains: List[Dict[str, str]],
    mode: ExecutionMode = ExecutionMode.LIVE_BLIND,
    output_file: Path = Path("data/treasure_runs/TREASURE_RUN_0002/candidates.jsonl"),
    max_workers: int = 15
) -> List[CandidateRecord]:
    """
    Execute 8 modular discovery strategies across the frozen domain sample and live CDX indices.
    """
    assert_live_blind_isolation(mode, context="generate_multi_strategy_candidates")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    candidates_map: Dict[str, CandidateRecord] = {}
    now_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    cand_counter = 0

    print(f"[*] Discovering archaeological candidates across {len(sampled_domains)} domains using 8 strategies...")

    # Parallel path discovery via CDX
    domain_cdx_results: Dict[str, List[PathCandidate]] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_dom = {
            executor.submit(fetch_domain_cdx_candidates, d["domain"], 20, 4): d
            for d in sampled_domains if d.get("domain")
        }
        for future in as_completed(future_to_dom):
            d_info = future_to_dom[future]
            dom_name = d_info["domain"]
            try:
                domain_cdx_results[dom_name] = future.result()
            except Exception:
                domain_cdx_results[dom_name] = [PathCandidate(
                    domain=dom_name,
                    candidate_url=f"https://{dom_name}/",
                    path="/",
                    path_category=PathCategory.GENERAL_DIRECTORY,
                    discovery_source="FALLBACK_ROOT",
                    first_observed_year=None,
                    last_observed_year=None,
                    capture_count=0
                )]

    for dom_info in sampled_domains:
        dom = dom_info["domain"]
        cat = dom_info.get("category", "General")
        if not dom:
            continue

        cdx_cands = domain_cdx_results.get(dom, [])

        for cand_meta in cdx_cands:
            path = cand_meta.path
            norm_path = path if path.startswith("/") else f"/{path}"
            full_url = f"https://{dom}{norm_path}"
            url_key = f"{dom}:{norm_path}"

            path_cat = classify_path_14(norm_path)
            matching_strategies = evaluate_path_strategies(norm_path, path_cat)
            if not matching_strategies:
                matching_strategies = [(
                    TreasureStrategy.HISTORICAL_SURVIVOR,
                    "General historical discovery path."
                )]

            primary_strat, reason = matching_strategies[0]
            strategy_names = [s[0].value for s in matching_strategies]

            if url_key in candidates_map:
                existing = candidates_map[url_key]
                for sn in strategy_names:
                    if sn not in existing.seen_by_strategies:
                        existing.seen_by_strategies.append(sn)
                        existing.research_priority = min(100.0, existing.research_priority + 10.0)
            else:
                cand_counter += 1
                cand_id = f"TCAND_{cand_counter:04d}"

                # Calculate objective research priority based on structural features and age
                base_prio = 25.0
                if path_cat == PathCategory14.USER_SPACE:
                    base_prio += 25.0
                if path_cat in (PathCategory14.DOCS, PathCategory14.LEGACY, PathCategory14.ARCHIVE):
                    base_prio += 20.0
                if cat in ("Personal/independent sites", "Universities", "Government"):
                    base_prio += 10.0
                if any(ext in norm_path.lower() for ext in [".html", ".htm", ".cgi", "/~"]):
                    base_prio += 10.0
                if cand_meta.first_observed_year and cand_meta.first_observed_year <= 2005:
                    base_prio += 15.0
                base_prio += (len(strategy_names) - 1) * 10.0
                base_prio = min(100.0, max(10.0, base_prio))

                span = 0
                if cand_meta.first_observed_year and cand_meta.last_observed_year:
                    span = max(0, cand_meta.last_observed_year - cand_meta.first_observed_year)

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
                    archive_presence="WAYBACK_CDX" if cand_meta.first_observed_year else "UNKNOWN",
                    current_status=None,
                    raw_evidence_available=False,
                    earliest_capture_year=cand_meta.first_observed_year,
                    latest_capture_year=cand_meta.last_observed_year,
                    historical_span_years=span,
                    capture_count=cand_meta.capture_count or 0,
                    research_priority=base_prio,
                    seen_by_strategies=strategy_names,
                    state=CandidateState.DISCOVERED
                )
                candidates_map[url_key] = rec

    candidates_list = list(candidates_map.values())
    candidates_list.sort(key=lambda x: x.research_priority, reverse=True)

    with open(output_file, "w", encoding="utf-8") as f:
        for c in candidates_list:
            f.write(c.model_dump_json() + "\n")

    print(f"[+] Candidate generation complete: {len(candidates_list)} unique candidates saved in {output_file}.")
    return candidates_list
