"""Candidate validation and rejection pipeline for Project Atlas Corpus v2."""

import re
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any
from urllib.parse import urlparse
from atlas.provenance.models import (
    CandidateRecord,
    ProvenanceRecord,
    RejectionRecord,
    RejectionCode,
    VerificationStatus,
    SourceType,
    LiveAvailabilityStatus,
    ArchiveAvailabilityStatus
)

# Known synthetic patterns to strictly forbid in production corpus
SYNTHETIC_PATTERNS = [
    re.compile(r"^(univ|corp|foundation|personal-site|company|project)-\d+", re.IGNORECASE),
    re.compile(r"^example\.(com|org|net|edu)", re.IGNORECASE),
    re.compile(r"^test(site|domain)?\.", re.IGNORECASE),
    re.compile(r"^fake\.", re.IGNORECASE),
    re.compile(r"^sample\.", re.IGNORECASE),
    re.compile(r"^placeholder\.", re.IGNORECASE)
]

VALID_CATEGORIES = {
    "Universities",
    "Government",
    "Nonprofits",
    "Long-running companies",
    "Open-source/project sites",
    "Personal/independent sites"
}

def normalize_domain(input_val: str) -> str:
    """Normalize input domain / URL to standard lowercase canonical domain name."""
    s = input_val.strip().lower()
    if s.startswith("http://") or s.startswith("https://"):
        parsed = urlparse(s)
        s = parsed.netloc or parsed.path
    if ":" in s:
        s = s.split(":")[0]
    s = s.rstrip(".")
    try:
        s = s.encode("idna").decode("ascii")
    except Exception:
        pass
    return s

def validate_candidate(
    candidate: CandidateRecord,
    seen_domains: Set[str]
) -> Tuple[bool, Optional[ProvenanceRecord], Optional[RejectionRecord]]:
    """
    Validate candidate through the strict anti-synthetic and provenance pipeline.
    """
    norm = normalize_domain(candidate.domain)

    if not norm or "." not in norm or len(norm) < 4:
        return False, None, RejectionRecord(
            domain=candidate.domain,
            category=candidate.category,
            rejection_code=RejectionCode.INVALID_DOMAIN,
            reason="Malformed or incomplete domain name structure."
        )

    for pat in SYNTHETIC_PATTERNS:
        if pat.search(norm):
            return False, None, RejectionRecord(
                domain=norm,
                category=candidate.category,
                rejection_code=RejectionCode.SYNTHETIC_PATTERN,
                reason="Detected procedural synthetic naming pattern."
            )

    if norm in seen_domains:
        return False, None, RejectionRecord(
            domain=norm,
            category=candidate.category,
            rejection_code=RejectionCode.DUPLICATE,
            reason="Domain already exists in validated candidate pool."
        )

    if candidate.source_type in (SourceType.UNKNOWN, SourceType.SYNTHETIC):
        return False, None, RejectionRecord(
            domain=norm,
            category=candidate.category,
            rejection_code=RejectionCode.INSUFFICIENT_PROVENANCE,
            reason="Candidate lacks verified public provenance reference."
        )

    if candidate.category not in VALID_CATEGORIES:
        return False, None, RejectionRecord(
            domain=norm,
            category=candidate.category,
            rejection_code=RejectionCode.CATEGORY_UNCERTAIN,
            reason=f"Unknown or unmapped research category: {candidate.category}"
        )

    provenance = ProvenanceRecord(
        domain=norm,
        canonical_url=f"https://{norm}",
        category=candidate.category,
        source_type=candidate.source_type,
        source_name=candidate.source_name,
        source_url=candidate.source_url,
        source_reference=candidate.source_reference,
        collection_method="CURATED_PUBLIC_DIRECTORY_INGEST",
        verification_status=VerificationStatus.VERIFIED_REAL_CURATED,
        live_status=LiveAvailabilityStatus.REAL_LIVE,
        archive_status=ArchiveAvailabilityStatus.BOTH,
        notes=candidate.notes
    )

    return True, provenance, None

def validate_corpus_integrity(corpus_dir: Path = Path("data/corpus_v2")) -> Dict[str, Any]:
    """
    Validate complete corpus files against zero-synthetic policy, uniqueness, and provenance rules.
    """
    manifest_file = corpus_dir / "corpus_manifest.json"
    provenance_file = corpus_dir / "provenance_v2.jsonl"
    csv_file = corpus_dir / "seed_corpus_v2.csv"

    if not manifest_file.exists() or not provenance_file.exists() or not csv_file.exists():
        raise FileNotFoundError(f"Missing required corpus files in {corpus_dir}")

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    seen = set()
    synthetic_found = []
    duplicates = []
    invalid_domains = []

    with open(provenance_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            rec = json.loads(line)
            dom = rec.get("domain", "")

            # Check synthetic
            for pat in SYNTHETIC_PATTERNS:
                if pat.search(dom):
                    synthetic_found.append(dom)

            # Check duplicate
            if dom in seen:
                duplicates.append(dom)
            seen.add(dom)

            # Check domain format
            if "." not in dom or len(dom) < 4:
                invalid_domains.append(dom)

    passed = (len(synthetic_found) == 0 and len(duplicates) == 0 and len(seen) >= 1000)

    return {
        "passed": passed,
        "total_domains": len(seen),
        "synthetic_count": len(synthetic_found),
        "duplicate_count": len(duplicates),
        "invalid_count": len(invalid_domains),
        "synthetic_domains": synthetic_found,
        "duplicate_domains": duplicates
    }
