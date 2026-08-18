"""
Future Run Research Planner Subsystem for Project Atlas.
Synthesizes evidence-backed proposals for future blind archaeology hunts.
Enforces that planner output is strictly a PROPOSAL and never automatically executed.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field

class ResearchProposal(BaseModel):
    proposal_id: str
    target_area: str
    rationale: str
    recommended_strategy_mix: Dict[str, float]  # e.g., {"USER_SPACE": 0.35, "TECHNOLOGY_FOSSIL": 0.35, "ORPHAN_PATH": 0.30}
    exploration_vs_exploitation_ratio: str = "70% Exploration / 30% Exploitation"
    evidence_justification: str
    is_proposal_only: bool = True

def generate_future_hunt_proposals(
    current_run_id: str,
    strategy_metrics: Dict[str, Any],
    top_candidates: List[Dict[str, Any]]
) -> List[ResearchProposal]:
    """Generate structured research proposals for subsequent archaeology hunts."""
    proposals = []

    # Proposal 1: Unix User Communities
    proposals.append(ResearchProposal(
        proposal_id=f"PROP-{current_run_id}-01",
        target_area="Independent Unix & Tilde Personal Space Archaeology",
        rationale="High archaeological signal observed in ~user personal homepages exhibiting handcrafted HTML and ASCII zines.",
        recommended_strategy_mix={"USER_SPACE": 0.50, "TECHNOLOGY_FOSSIL": 0.30, "ORPHAN_PATH": 0.20},
        exploration_vs_exploitation_ratio="70% Exploration / 30% Exploitation",
        evidence_justification="Multiple high-interest candidates discovered in tilde web hosts in recent blind runs.",
        is_proposal_only=True
    ))

    # Proposal 2: Academic & Institutional Document Trees
    proposals.append(ResearchProposal(
        proposal_id=f"PROP-{current_run_id}-02",
        target_area="Surviving Academic Faculty Repositories and Government Tables",
        rationale="Pre-CSS table layouts and plaintext research archive trees survive under deep unindexed paths.",
        recommended_strategy_mix={"HISTORICAL_SURVIVOR": 0.40, "STRUCTURAL_SURVIVOR": 0.40, "ORPHAN_PATH": 0.20},
        exploration_vs_exploitation_ratio="70% Exploration / 30% Exploitation",
        evidence_justification="Isolated administrative directories persist across major educational and governmental domains.",
        is_proposal_only=True
    ))

    return proposals
