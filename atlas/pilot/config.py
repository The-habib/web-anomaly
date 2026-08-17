"""Configuration for Phase 1.2 Pilot Experiment."""

from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict

class PilotConfig(BaseModel):
    pilot_name: str = "Phase 1.2 200-Domain Pilot"
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
    pilot_data_path: Path = Path("data/phase1_2_pilot")
    benchmark_v1_path: Path = Path("data/benchmark_v1")
    evidence_path: Path = Path("data/phase1_2_pilot/evidence")
    checkpoints_path: Path = Path("data/phase1_2_pilot/checkpoints")
    reports_path: Path = Path("reports")
    review_sample_size: int = 20
