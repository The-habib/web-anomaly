"""Phase 1.5 Deep Web Archaeology Configuration."""

from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict

class DeepExperimentConfig(BaseModel):
    experiment_name: str = "Phase 1.5 Deep Web Archaeology"
    sampling_seed: int = 42
    total_study_domains: int = 300
    category_quotas: Dict[str, int] = Field(default_factory=lambda: {
        "Universities": 60,
        "Government": 60,
        "Nonprofits": 45,
        "Long-running companies": 45,
        "Open-source/project sites": 45,
        "Personal/independent sites": 45
    })
    max_candidates_per_domain: int = 50
    max_retrievals_per_domain: int = 15
    batch_size: int = 50
    batch_count: int = 6
    http_timeout: int = 8
    max_workers: int = 6
    output_dir: Path = Path("data/phase1_5")
    experiments_dir: Path = Path("experiments/phase1_5")
    checkpoints_dir: Path = Path("data/phase1_5/checkpoints")
    audit_dir: Path = Path("audit/phase1_5")
    reports_dir: Path = Path("reports")
    discoveries_dir: Path = Path("reports/discoveries")
