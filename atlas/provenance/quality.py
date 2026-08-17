"""Corpus Quality Score Calculator for Project Atlas Corpus v2."""

import math
from typing import List, Dict
from atlas.provenance.models import ProvenanceRecord, CorpusQualityMetrics, SourceType

def calculate_corpus_quality(corpus: List[ProvenanceRecord]) -> CorpusQualityMetrics:
    """
    Calculate transparent, multi-dimensional quality metrics for a corpus.
    All formulas are deterministic and fully documented.
    """
    total = len(corpus)
    if total == 0:
        return CorpusQualityMetrics(
            total_domains=0,
            provenance_completeness=0.0,
            synthetic_rate=0.0,
            duplicate_rate=0.0,
            verification_rate=0.0,
            category_integrity=0.0,
            source_diversity=0.0,
            overall_quality_score=0.0,
            weakest_dimension="empty_corpus",
            dimension_scores={}
        )

    # 1. Provenance Completeness
    complete_count = sum(
        1 for r in corpus
        if r.domain and r.canonical_url and r.category and r.source_type and r.source_name and r.source_reference
    )
    provenance_completeness = round(complete_count / total, 4)

    # 2. Synthetic Rate (Strict 0.0 is perfect 1.0)
    synthetic_count = sum(1 for r in corpus if r.source_type == SourceType.SYNTHETIC or "example.com" in r.domain)
    synthetic_rate = round(synthetic_count / total, 4)
    synthetic_score = 1.0 if synthetic_count == 0 else max(0.0, 1.0 - (synthetic_rate * 5.0))

    # 3. Duplicate Rate (Strict 0.0 is perfect 1.0)
    seen = set()
    dup_count = 0
    for r in corpus:
        if r.domain in seen:
            dup_count += 1
        seen.add(r.domain)
    duplicate_rate = round(dup_count / total, 4)
    duplicate_score = 1.0 if dup_count == 0 else max(0.0, 1.0 - (duplicate_rate * 5.0))

    # 4. Verification Rate
    verified_count = sum(
        1 for r in corpus if r.verification_status.value in ("VERIFIED_REAL_CURATED", "VERIFIED_ACTIVE", "VERIFIED_HISTORICAL")
    )
    verification_rate = round(verified_count / total, 4)

    # 5. Category Integrity
    valid_categories = {
        "Universities",
        "Government",
        "Nonprofits",
        "Long-running companies",
        "Open-source/project sites",
        "Personal/independent sites"
    }
    cat_count = sum(1 for r in corpus if r.category in valid_categories)
    category_integrity = round(cat_count / total, 4)

    # 6. Source Diversity (Normalized Shannon entropy over source names)
    source_counts: Dict[str, int] = {}
    for r in corpus:
        source_counts[r.source_name] = source_counts.get(r.source_name, 0) + 1

    num_sources = len(source_counts)
    if num_sources <= 1:
        source_diversity = 0.0
    else:
        entropy = -sum((c / total) * math.log2(c / total) for c in source_counts.values())
        max_entropy = math.log2(num_sources)
        source_diversity = round(entropy / max_entropy, 4) if max_entropy > 0 else 0.0

    # Dimension Scores Dictionary
    dimension_scores = {
        "provenance_completeness": provenance_completeness,
        "synthetic_resistance": synthetic_score,
        "duplicate_resistance": duplicate_score,
        "verification_rate": verification_rate,
        "category_integrity": category_integrity,
        "source_diversity": source_diversity
    }

    # Overall Weighted Score (Weights prioritize scientific validity)
    weights = {
        "provenance_completeness": 0.20,
        "synthetic_resistance": 0.25,
        "duplicate_resistance": 0.15,
        "verification_rate": 0.20,
        "category_integrity": 0.10,
        "source_diversity": 0.10
    }
    overall_quality_score = round(
        sum(dimension_scores[k] * weights[k] for k in weights),
        4
    )

    # Find weakest dimension
    weakest_dim = min(dimension_scores.items(), key=lambda x: x[1])[0]

    return CorpusQualityMetrics(
        total_domains=total,
        provenance_completeness=provenance_completeness,
        synthetic_rate=synthetic_rate,
        duplicate_rate=duplicate_rate,
        verification_rate=verification_rate,
        category_integrity=category_integrity,
        source_diversity=source_diversity,
        overall_quality_score=overall_quality_score,
        weakest_dimension=weakest_dim,
        dimension_scores=dimension_scores
    )
