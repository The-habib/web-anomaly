"""
Unbiased Deterministic Domain Sampler for Project Atlas — Treasure Mode.
Samples 100 domains from Atlas Corpus v2 using deterministic category stratification
and creates an immutable sample manifest frozen prior to candidate discovery.
"""

import json
import random
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple

from atlas.treasure.models import SampleManifest

DEFAULT_CATEGORY_QUOTAS: Dict[str, int] = {
    "Universities": 20,
    "Government": 20,
    "Nonprofits": 15,
    "Long-running companies": 15,
    "Open-source/project sites": 15,
    "Personal/independent sites": 15
}

def load_corpus_v2_population(
    corpus_index_path: Path = Path("data/corpus_v2/category_index.json"),
    corpus_csv_path: Path = Path("data/corpus_v2/seed_corpus_v2.csv")
) -> Dict[str, List[str]]:
    """
    Load the complete 1,000-domain population grouped by canonical categories.
    """
    if corpus_index_path.exists():
        with open(corpus_index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure canonical alphabetical sorting for deterministic base state
            return {cat: sorted(domains) for cat, domains in data.items()}

    if corpus_csv_path.exists():
        import csv
        cat_map: Dict[str, List[str]] = {}
        with open(corpus_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                dom = row.get("domain", "").strip()
                cat = row.get("seed_category", "").strip() or "General"
                if dom:
                    cat_map.setdefault(cat, []).append(dom)
        return {cat: sorted(domains) for cat, domains in cat_map.items()}

    raise FileNotFoundError(f"Corpus v2 files not found at {corpus_index_path} or {corpus_csv_path}")

def sample_blind_domain_population(
    run_id: str = "TREASURE_RUN_0002",
    sample_size: int = 100,
    seed: int = 101,
    quotas: Dict[str, int] = DEFAULT_CATEGORY_QUOTAS,
    output_manifest_path: Path = Path("data/treasure_runs/TREASURE_RUN_0002/sample_manifest.json")
) -> SampleManifest:
    """
    Deterministically sample domains from the complete eligible population.
    Freezes the sample manifest to disk before discovery begins.
    """
    population = load_corpus_v2_population()
    
    # Calculate population hash
    all_domains_sorted = sorted([d for doms in population.values() for d in doms])
    pop_hash = hashlib.sha256("\n".join(all_domains_sorted).encode("utf-8")).hexdigest()

    rng = random.Random(seed)
    selected_domains: List[Dict[str, str]] = []

    for cat, quota in quotas.items():
        pool = population.get(cat, [])
        if len(pool) < quota:
            sampled = list(pool)
        else:
            sampled = rng.sample(pool, quota)
        
        for d in sampled:
            selected_domains.append({
                "domain": d,
                "category": cat
            })

    # Sort selected deterministically
    selected_domains.sort(key=lambda x: x["domain"])
    sel_domains_str = "\n".join(f"{d['domain']}:{d['category']}" for d in selected_domains)
    sel_hash = hashlib.sha256(sel_domains_str.encode("utf-8")).hexdigest()

    import time
    manifest = SampleManifest(
        run_id=run_id,
        corpus_version="Atlas Corpus v2 (1,000 domains)",
        sample_seed=seed,
        sample_size=len(selected_domains),
        category_quotas={k: len([d for d in selected_domains if d["category"] == k]) for k in quotas},
        population_sha256=pop_hash,
        selected_domains_sha256=sel_hash,
        selected_domains=selected_domains,
        created_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )

    output_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(indent=2))

    return manifest

if __name__ == "__main__":
    m = sample_blind_domain_population()
    print(f"[+] Sampled {m.sample_size} domains. SHA-256: {m.selected_domains_sha256}")
