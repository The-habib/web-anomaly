"""
Evidence-Linked Discovery Explanation Engine for Project Atlas.
Synthesizes grounded archaeological discovery narratives directly tied to observed facts.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from atlas.explain.validator import validate_explanation

class DiscoveryExplanation(BaseModel):
    candidate_id: str
    url: str
    domain: str
    one_line_summary: str
    detailed_narrative: str
    evidence_citations: List[str]
    is_valid_scientific_claim: bool
    validation_violations: List[str]

def generate_discovery_explanation(
    candidate_id: str,
    url: str,
    domain: str,
    path: str,
    strategy: str,
    earliest_year: Optional[int],
    live_status: int,
    html_features: List[str],
    sha256_hash: str
) -> DiscoveryExplanation:
    """Generate structured, evidence-linked explanation for why Atlas prioritized and preserved an artifact."""
    citations = []

    # Grounded narrative construction
    parts = []
    
    # 1. Discovery reason
    parts.append(
        f"Atlas prioritized '{url}' via the {strategy} channel based on public web discovery."
    )
    citations.append(f"Discovery Channel: {strategy}")

    # 2. Historical context
    if earliest_year and earliest_year > 1990:
        parts.append(
            f"Historical archive indexes record early public observation dating to approximately {earliest_year}."
        )
        citations.append(f"Earliest Archive Observation: {earliest_year}")
    else:
        parts.append(
            "Historical observation timestamps remain unconfirmed in public archive indexes."
        )
        citations.append("Earliest Archive Observation: UNCONFIRMED")

    # 3. Live status and features
    if live_status == 200:
        feat_desc = ", ".join(html_features) if html_features else "minimal legacy layout"
        parts.append(
            f"A live HTTP probe confirmed active service (HTTP {live_status}) exhibiting {feat_desc}."
        )
        citations.append(f"Live HTTP Status: {live_status}")
        citations.append(f"DOM Features: {feat_desc}")
    else:
        parts.append(f"Live HTTP probe returned status code {live_status}.")
        citations.append(f"Live HTTP Status: {live_status}")

    # 4. Cryptographic preservation
    if sha256_hash:
        parts.append(f"Raw HTML bytes were preserved with SHA-256 digest `{sha256_hash[:16]}...`.")
        citations.append(f"SHA-256 Digest: {sha256_hash}")

    detailed = " ".join(parts)
    one_line = f"Surviving {strategy.lower().replace('_', ' ')} on {domain} exhibiting {len(html_features)} historical structural markers."

    is_valid, violations = validate_explanation(detailed)

    return DiscoveryExplanation(
        candidate_id=candidate_id,
        url=url,
        domain=domain,
        one_line_summary=one_line,
        detailed_narrative=detailed,
        evidence_citations=citations,
        is_valid_scientific_claim=is_valid,
        validation_violations=violations
    )
