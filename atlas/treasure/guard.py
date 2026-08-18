"""
Execution Mode Guard & World Isolation Subsystem for Project Atlas — Treasure Mode.
Enforces strict runtime separation between DISCOVERY WORLD, REFERENCE WORLD,
TEST WORLD, and SIMULATION WORLD.
"""

import sys
import os
from enum import Enum
from typing import List, Optional

class ExecutionMode(str, Enum):
    LIVE_BLIND = "LIVE_BLIND"
    REPLAY = "REPLAY"
    SIMULATION = "SIMULATION"
    REFERENCE_EVALUATION = "REFERENCE_EVALUATION"

FORBIDDEN_SIMULATION_MODULES: List[str] = [
    "atlas.simulation.synthetic",
    "atlas.simulation.engine"
]

FORBIDDEN_REFERENCE_TOKENS: List[str] = [
    "KNOWN_ARCHAEOLOGICAL_SEEDS",
    "known_fossils",
    "benchmark_labels"
]

def assert_live_blind_isolation(mode: ExecutionMode, context: str = "Candidate Discovery") -> None:
    """
    Assert that the current execution environment is completely isolated from
    simulation artifacts, reference labels, and seeded answer keys during LIVE_BLIND mode.
    Raises RuntimeError immediately upon contamination.
    """
    if mode != ExecutionMode.LIVE_BLIND:
        return

    # 1. Inspect caller stack and treasure modules for forbidden simulation imports or reference tokens
    import inspect
    frame = inspect.currentframe()
    try:
        while frame:
            f_globals = frame.f_globals
            mod_name = f_globals.get("__name__", "")
            if mod_name.startswith("atlas.treasure"):
                for forbidden_mod in FORBIDDEN_SIMULATION_MODULES:
                    if forbidden_mod in f_globals:
                        raise RuntimeError(
                            f"[CONTAMINATION DETECTED] Forbidden simulation module '{forbidden_mod}' imported in '{mod_name}' during {context} in LIVE_BLIND mode."
                        )
                for token in FORBIDDEN_REFERENCE_TOKENS:
                    if token in f_globals:
                        raise RuntimeError(
                            f"[CONTAMINATION DETECTED] Forbidden reference token '{token}' found in '{mod_name}' scope during {context} in LIVE_BLIND mode."
                        )
            frame = frame.f_back
    finally:
        del frame

    # 2. In non-test execution, ensure forbidden modules are not in sys.modules
    if "PYTEST_CURRENT_TEST" not in os.environ:
        loaded_modules = set(sys.modules.keys())
        for forbidden_mod in ["atlas.simulation.synthetic", "atlas.simulation.engine"]:
            if forbidden_mod in loaded_modules:
                raise RuntimeError(
                    f"[CONTAMINATION DETECTED] Forbidden simulation module '{forbidden_mod}' is loaded in LIVE_BLIND mode during {context}."
                )
