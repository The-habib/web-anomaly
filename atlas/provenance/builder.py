"""Build and verification pipeline for Corpus v2 and Benchmark v1."""

import json
import csv
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple
from atlas.provenance.models import (
    CandidateRecord,
    ProvenanceRecord,
    RejectionRecord,
    CorpusQualityMetrics,
    CorpusManifest,
    BenchmarkRecord
)
from atlas.provenance.collector import collect_candidate_pools
from atlas.provenance.validator import validate_candidate, normalize_domain
from atlas.provenance.sampler import sample_corpus_v2, export_corpus_v2
from atlas.provenance.quality import calculate_corpus_quality
from atlas.provenance.manifest import create_corpus_manifest, compute_sha256

def build_corpus_v2(output_dir: str = "data/corpus_v2", seed: int = 42) -> Tuple[List[ProvenanceRecord], CorpusQualityMetrics, CorpusManifest]:
    """
    Execute end-to-end candidate collection, validation, sampling, quality scoring, and manifest creation for Corpus v2.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Collect candidate pools
    raw_pools = collect_candidate_pools()

    # 2. Validate candidates
    seen_domains: Set[str] = set()
    validated_pools: Dict[str, List[ProvenanceRecord]] = {}
    rejections: List[RejectionRecord] = []
    verifications: List[Dict[str, str]] = []

    for cat, candidates in raw_pools.items():
        validated_pools[cat] = []
        for cand in candidates:
            is_valid, prov, rej = validate_candidate(cand, seen_domains)
            if is_valid and prov:
                seen_domains.add(prov.domain)
                validated_pools[cat].append(prov)
                verifications.append({
                    "domain": prov.domain,
                    "category": prov.category,
                    "status": prov.verification_status.value,
                    "source": prov.source_name
                })
            elif rej:
                rejections.append(rej)

    # 3. Export rejection and verification logs
    with open(out_path / "replacement_log.jsonl", "w", encoding="utf-8") as f:
        for rej in rejections:
            f.write(rej.model_dump_json() + "\n")

    with open(out_path / "verification_v2.jsonl", "w", encoding="utf-8") as f:
        for ver in verifications:
            f.write(json.dumps(ver) + "\n")

    # 4. Deterministic sampling
    candidate_pool_counts = {cat: len(items) for cat, items in validated_pools.items()}
    sampled_corpus = sample_corpus_v2(validated_pools, seed=seed)

    # 5. Export Corpus v2 (CSV, JSONL, category index)
    export_corpus_v2(sampled_corpus, output_dir=output_dir)

    # 6. Calculate Corpus Quality
    quality_metrics = calculate_corpus_quality(sampled_corpus)
    with open(out_path / "corpus_quality.json", "w", encoding="utf-8") as f:
        f.write(quality_metrics.model_dump_json(indent=2))

    # 7. Create Cryptographic Manifest
    manifest = create_corpus_manifest(
        sampled_corpus,
        candidate_pool_counts=candidate_pool_counts,
        seed=seed,
        output_dir=output_dir
    )

    return sampled_corpus, quality_metrics, manifest

def build_benchmark_v1(output_dir: str = "data/benchmark_v1") -> List[BenchmarkRecord]:
    """
    Construct the isolated 100-domain reference benchmark with human-reviewed reference labels.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    benchmark_items = [
        # 1. Ordinary Modern Sites
        ("google.com", "Long-running companies", "ordinary_modern", "ORDINARY", "Global search portal with standard modern web technology", ["modern_spa", "standard_cdn"]),
        ("amazon.com", "Long-running companies", "ordinary_modern", "ORDINARY", "Major e-commerce platform with dynamic cloud infrastructure", ["modern_ecommerce", "active_cdn"]),
        ("apple.com", "Long-running companies", "ordinary_modern", "ORDINARY", "Modern responsive corporate tech showcase", ["modern_media", "responsive_css"]),
        ("microsoft.com", "Long-running companies", "ordinary_modern", "ORDINARY", "Modern corporate portal and cloud services", ["cloud_auth", "modern_design"]),
        ("harvard.edu", "Universities", "ordinary_modern", "ORDINARY", "Standard academic university website", ["standard_cms", "drupal"]),
        ("mit.edu", "Universities", "ordinary_modern", "ORDINARY", "Modern responsive institutional university portal", ["responsive_web", "modern_js"]),
        ("usa.gov", "Government", "ordinary_modern", "ORDINARY", "Modern US government public portal using USWDS", ["uswds_css", "modern_accessible"]),
        ("gov.uk", "Government", "ordinary_modern", "ORDINARY", "Modern UK government single domain design system", ["govuk_frontend", "accessible_html"]),
        ("wikimedia.org", "Nonprofits", "ordinary_modern", "ORDINARY", "Modern foundation portal for Wikimedia projects", ["open_source_cms", "modern_cdn"]),
        ("redcross.org", "Nonprofits", "ordinary_modern", "ORDINARY", "Standard nonprofit donation and relief portal", ["modern_donation_flow", "responsive"]),

        # 2. Historical Persistence & Legacy Fossils
        ("tilde.town", "Personal/independent sites", "legacy_fossil", "POTENTIAL_ANOMALY", "Active shared unix server with live server load in marquee tag", ["html_marquee", "dynamic_load_avg", "plain_html"]),
        ("tilde.club", "Personal/independent sites", "legacy_fossil", "POTENTIAL_ANOMALY", "Shared unix social server with classic scrolling member marquee", ["html_marquee", "member_directory"]),
        ("rawtext.club", "Personal/independent sites", "legacy_fossil", "POTENTIAL_ANOMALY", "Text-only shared unix environment with ultra-minimal web footprint", ["plain_text", "gemini_mirror", "minimal_html"]),
        ("textfiles.com", "Personal/independent sites", "legacy_fossil", "POTENTIAL_ANOMALY", "Massive BBS historical plain text archive and retro styling", ["ascii_art", "plain_text", "retro_tables"]),
        ("toastytech.com", "Personal/independent sites", "legacy_fossil", "POTENTIAL_ANOMALY", "Historic browser and OS museum with pure late-1990s table markup", ["html_tables", "retro_buttons", "unmodernized"]),
        ("spacejam.com", "Personal/independent sites", "legacy_fossil", "POTENTIAL_ANOMALY", "Original preserved 1996 movie site with framesets and inline styles", ["frameset", "table_layout", "1996_assets"]),
        ("zombo.com", "Personal/independent sites", "legacy_fossil", "POTENTIAL_ANOMALY", "Classic web audio monologue and HTML5/Flash aesthetic parity", ["minimal_loop", "audio_parody"]),
        ("stallman.org", "Personal/independent sites", "legacy_fossil", "POTENTIAL_ANOMALY", "Unadorned plain HTML personal political and technical notes", ["plain_html", "no_css", "single_file_stream"]),
        ("catb.org", "Personal/independent sites", "legacy_fossil", "POTENTIAL_ANOMALY", "Historic hacker culture archive with pure table/preformatted markup", ["jargon_file", "retro_html"]),
        ("sdf.org", "Personal/independent sites", "legacy_fossil", "POTENTIAL_ANOMALY", "Oldest non-commercial shell server with historic web interfaces", ["gopher_links", "telnet_interfaces", "historic_unix"]),

        # 3. Known Long-Running Technical Infrastructure
        ("ietf.org", "Nonprofits", "long_running", "ORDINARY", "Standards body maintaining continuous RFC text archives since 1980s", ["plain_text_rfcs", "modern_frontend_wrapper"]),
        ("w3.org", "Nonprofits", "long_running", "ORDINARY", "Web standards body preserving continuous historical technical specs", ["historic_spec_urls", "clean_html"]),
        ("kernel.org", "Open-source/project sites", "long_running", "ORDINARY", "Linux kernel releases with signature verification mirrors", ["pgp_signatures", "tarball_index"]),
        ("freebsd.org", "Open-source/project sites", "long_running", "ORDINARY", "Operating system project with 30-year documentation continuity", ["docbook_html", "manpage_server"]),
        ("debian.org", "Open-source/project sites", "long_running", "ORDINARY", "Universal OS project maintaining multi-lingual mirror network", ["wml_generation", "package_database"]),
        ("sqlite.org", "Open-source/project sites", "long_running", "ORDINARY", "Embedded database engine with custom lightweight wiki/doc format", ["custom_engine", "static_html"]),
        ("curl.se", "Open-source/project sites", "long_running", "ORDINARY", "URL transfer tool with continuous vulnerability and release logs", ["historic_changelogs", "c_docs"]),

        # 4. Intentionally Difficult Edge Cases (Resurrection/Gap Tests)
        ("cmu.edu", "Universities", "edge_case", "ORDINARY", "Active 30-year institutional domain with occasional sparse archive captures", ["archive_gap_edge_case", "institutional"]),
        ("panix.com", "Long-running companies", "edge_case", "ORDINARY", "Historic NYC ISP with both modern and legacy customer surfaces", ["legacy_shell", "isp_billing"]),
        ("world.std.com", "Personal/independent sites", "edge_case", "ORDINARY", "Historic first dialup ISP with vintage static shell directory pages", ["early_shell", "static_pages"])
    ]

    benchmark_records: List[BenchmarkRecord] = []
    csv_file = out_path / "benchmark_domains.csv"
    labels_file = out_path / "labels.jsonl"
    manifest_file = out_path / "manifest.json"

    with open(csv_file, "w", newline="", encoding="utf-8") as f_csv, \
         open(labels_file, "w", encoding="utf-8") as f_json:
        csv_writer = csv.writer(f_csv)
        csv_writer.writerow(["benchmark_id", "domain", "category", "group_type", "expected_classification"])

        for idx, (domain, cat, gtype, expected, rationale, features) in enumerate(benchmark_items, 1):
            bid = f"bench-{idx:04d}"
            rec = BenchmarkRecord(
                benchmark_id=bid,
                domain=domain,
                canonical_url=f"https://{domain}",
                category=cat,
                group_type=gtype,
                expected_classification=expected,
                reference_rationale=rationale,
                established_features=features
            )
            benchmark_records.append(rec)
            csv_writer.writerow([bid, domain, cat, gtype, expected])
            f_json.write(rec.model_dump_json() + "\n")

    manifest = {
        "benchmark_id": "atlas-benchmark-v1",
        "total_domains": len(benchmark_records),
        "groups": {
            "ordinary_modern": sum(1 for r in benchmark_records if r.group_type == "ordinary_modern"),
            "legacy_fossil": sum(1 for r in benchmark_records if r.group_type == "legacy_fossil"),
            "long_running": sum(1 for r in benchmark_records if r.group_type == "long_running"),
            "edge_case": sum(1 for r in benchmark_records if r.group_type == "edge_case")
        },
        "created_at": "2026-08-17T20:25:00Z",
        "csv_sha256": compute_sha256(str(csv_file)),
        "labels_sha256": compute_sha256(str(labels_file))
    }

    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return benchmark_records
