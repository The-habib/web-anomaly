"""Configuration for Project Atlas Pilot and Live Experiments."""

from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict

class PilotConfig(BaseModel):
    pilot_id: str = "pilot-live-200"
    pilot_name: str = "Phase 1.3 200-Domain Live Pilot"
    experiment_mode: str = "LIVE"
    total_domains: int = 200
    batch_size: int = 50
    seed: int = 42
    category_quotas: Dict[str, int] = Field(default_factory=lambda: {
        "Universities": 40,
        "Government": 40,
        "Nonprofits": 30,
        "Long-running companies": 30,
        "Open-source/project sites": 30,
        "Personal/independent sites": 30
    })
    corpus_v2_path: Path = Path("data/corpus_v2")
    pilot_dir: Path = Path("data/phase1_3_live")
    pilot_data_path: Path = Path("data/phase1_3_live")
    benchmark_v2_path: Path = Path("data/benchmark_v2")
    evidence_path: Path = Path("data/phase1_3_live/evidence")
    checkpoints_path: Path = Path("data/phase1_3_live/checkpoints")
    reports_path: Path = Path("reports")
    review_sample_size: int = 20
