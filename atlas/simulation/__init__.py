"""Simulation and test fixture subsystem for Project Atlas.
FOR TEST AND OFFLINE REGRESSION EXPERIMENTS ONLY. STRICTLY PROHIBITED IN LIVE EMPIRICAL MODE.
"""

from atlas.simulation.generator import generate_synthetic_evidence_profile
from atlas.simulation.profiles import KNOWN_TEST_PROFILES

__all__ = [
    "generate_synthetic_evidence_profile",
    "KNOWN_TEST_PROFILES"
]
