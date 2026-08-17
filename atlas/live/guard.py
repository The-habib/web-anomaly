"""Emergency safety guard preventing simulation contamination in LIVE empirical mode."""

class SimulationContaminationError(RuntimeError):
    """Raised when simulation, mock, or synthetic fixture code is accessed in LIVE mode."""
    pass

_CURRENT_EXPERIMENT_MODE: str = "LIVE"

def set_experiment_mode(mode: str):
    """Set the active global experiment mode ('LIVE', 'SIMULATION', 'REPLAY')."""
    global _CURRENT_EXPERIMENT_MODE
    valid_modes = {"LIVE", "SIMULATION", "REPLAY"}
    mode_upper = mode.upper()
    if mode_upper not in valid_modes:
        raise ValueError(f"Invalid experiment mode: {mode}. Must be one of {valid_modes}")
    _CURRENT_EXPERIMENT_MODE = mode_upper

def get_experiment_mode() -> str:
    """Return the active global experiment mode."""
    return _CURRENT_EXPERIMENT_MODE

def assert_no_simulation(context_desc: str = "Simulation Function"):
    """
    Called inside simulation code. If active mode is 'LIVE', raises SimulationContaminationError.
    """
    if _CURRENT_EXPERIMENT_MODE == "LIVE":
        raise SimulationContaminationError(
            f"SECURITY GUARD VIOLATION in {context_desc}: "
            f"Attempted to invoke simulation/synthetic fixture while experiment mode is set to LIVE!"
        )

def assert_live_mode(context_desc: str = "Live Collector"):
    """
    Called inside live empirical collection code to verify that live collection is enabled.
    """
    if _CURRENT_EXPERIMENT_MODE not in ("LIVE", "REPLAY"):
        raise RuntimeError(
            f"Mode mismatch in {context_desc}: active mode is {_CURRENT_EXPERIMENT_MODE}, expected LIVE or REPLAY."
        )
