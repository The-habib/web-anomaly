"""Comprehensive unit tests for Corpus v2 and Provenance Subsystem."""

import pytest
from pathlib import Path
from atlas.provenance.models import (
    CandidateRecord, SourceType, RejectionCode, VerificationStatus
)
from atlas.provenance.validator import (
    validate_candidate, normalize_domain, validate_corpus_integrity, SYNTHETIC_PATTERNS
)
from atlas.provenance.collector import collect_candidate_pools
from atlas.provenance.sampler import sample_corpus_v2
from atlas.provenance.quality import calculate_corpus_quality
from atlas.provenance.builder import build_corpus_v2

def test_normalize_domain():
    assert normalize_domain("https://www.HARVARD.edu/") == "www.harvard.edu"
    assert normalize_domain("http://MIT.EDU:8080/path") == "mit.edu"
    assert normalize_domain("example.com.") == "example.com"

def test_synthetic_pattern_rejection():
    seen = set()
    fake_candidates = [
        CandidateRecord(domain="univ-001.edu", input_url="https://univ-001.edu", category="Universities", source_type=SourceType.SYNTHETIC, source_name="Generator", source_url="mock", source_reference="None"),
        CandidateRecord(domain="company-042.com", input_url="https://company-042.com", category="Long-running companies", source_type=SourceType.SYNTHETIC, source_name="Generator", source_url="mock", source_reference="None"),
        CandidateRecord(domain="example.org", input_url="https://example.org", category="Nonprofits", source_type=SourceType.SYNTHETIC, source_name="Generator", source_url="mock", source_reference="None"),
    ]
    for c in fake_candidates:
        valid, prov, rej = validate_candidate(c, seen)
        assert valid is False
        assert prov is None
        assert rej is not None
        assert rej.rejection_code == RejectionCode.SYNTHETIC_PATTERN

def test_duplicate_rejection():
    seen = {"harvard.edu"}
    dup_cand = CandidateRecord(
        domain="harvard.edu",
        input_url="https://harvard.edu",
        category="Universities",
        source_type=SourceType.PUBLIC_DATASET,
        source_name="US IPEDS",
        source_url="https://harvard.edu",
        source_reference="US IPEDS Record"
    )
    valid, prov, rej = validate_candidate(dup_cand, seen)
    assert valid is False
    assert rej.rejection_code == RejectionCode.DUPLICATE

def test_candidate_pool_counts():
    pools = collect_candidate_pools()
    assert len(pools) == 6
    assert len(pools["Universities"]) >= 200
    assert len(pools["Government"]) >= 200
    assert len(pools["Nonprofits"]) >= 150
    assert len(pools["Long-running companies"]) >= 150
    assert len(pools["Open-source/project sites"]) >= 150
    assert len(pools["Personal/independent sites"]) >= 150

def test_deterministic_sampler():
    from atlas.provenance.validator import validate_candidate
    pools = collect_candidate_pools()
    validated_pools = {}
    seen = set()
    for cat, candidates in pools.items():
        validated_pools[cat] = []
        for c in candidates:
            valid, prov, rej = validate_candidate(c, seen)
            if valid and prov:
                seen.add(prov.domain)
                validated_pools[cat].append(prov)

    # Sample twice with seed=42
    res1 = sample_corpus_v2(validated_pools, seed=42)
    res2 = sample_corpus_v2(validated_pools, seed=42)

    assert len(res1) == 1000
    assert len(res2) == 1000
    assert [r.domain for r in res1] == [r.domain for r in res2]

def test_corpus_v2_quality():
    corpus, quality, manifest = build_corpus_v2()
    assert len(corpus) == 1000
    assert quality.overall_quality_score == 1.0
    assert quality.synthetic_rate == 0.0
    assert quality.duplicate_rate == 0.0
    assert quality.provenance_completeness == 1.0
    assert manifest.synthetic_count == 0
    assert manifest.duplicate_count == 0
    assert manifest.unknown_provenance_count == 0

def test_corpus_integrity_validation():
    val_res = validate_corpus_integrity()
    assert val_res["passed"] is True
    assert val_res["total_domains"] == 1000
    assert val_res["synthetic_count"] == 0
    assert val_res["duplicate_count"] == 0
