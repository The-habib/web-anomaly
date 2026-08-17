"""Experiment Ledger for numbering, provisioning, and tracking scientific experiments."""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional

from atlas.core.config import EXPERIMENTS_DIR
from atlas.core.logger import logger
from atlas.core.models import Experiment, ExperimentStatus

class ExperimentLedger:
    """Manages sequential numbered experiments in the laboratory."""

    def __init__(self, base_dir: Path = EXPERIMENTS_DIR):
        self.base_dir = base_dir

    def get_next_experiment_id(self) -> str:
        """Scan existing experiment directories and return next 4-digit ID (e.g. '0001')."""
        existing_numbers = []
        if self.base_dir.exists():
            for p in self.base_dir.iterdir():
                if p.is_dir() and p.name.isdigit():
                    existing_numbers.append(int(p.name))
        next_num = max(existing_numbers, default=0) + 1
        return f"{next_num:04d}"

    def list_experiments(self) -> List[dict]:
        """List all experiments in the ledger with their metadata."""
        experiments = []
        if not self.base_dir.exists():
            return experiments

        for p in sorted(self.base_dir.iterdir()):
            if p.is_dir() and p.name.isdigit():
                meta_file = p / "experiment.json"
                if meta_file.exists():
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            experiments.append(json.load(f))
                    except Exception:
                        experiments.append({"experiment_id": p.name, "status": "unknown"})
                else:
                    experiments.append({"experiment_id": p.name, "status": "uninitialized"})
        return experiments

    def create_experiment(
        self,
        title: str,
        hypothesis: str,
        target_urls: Optional[List[str]] = None
    ) -> Path:
        """
        Create the next numbered experiment directory with all required scaffold files.
        """
        exp_id = self.get_next_experiment_id()
        exp_dir = self.base_dir / exp_id
        evidence_dir = exp_dir / "evidence"

        exp_dir.mkdir(parents=True, exist_ok=True)
        evidence_dir.mkdir(parents=True, exist_ok=True)

        target_urls = target_urls or []
        created_at = datetime.now(timezone.utc).isoformat()

        # 1. hypothesis.md
        with open(exp_dir / "hypothesis.md", "w", encoding="utf-8") as f:
            f.write(f"""# Experiment {exp_id} — Hypothesis

**Title**: {title}  
**Date**: {created_at}  
**Status**: `proposed`

## Scientific Hypothesis
{hypothesis}

## Target Candidate Scope
{chr(10).join(f"- {u}" for u in target_urls) if target_urls else "- *Target URLs to be defined during setup.*"}

## Expected Discovery Signals
- Persistence threshold >= 15 years
- Technology fossil signatures
- Structural / temporal resurrection patterns
""")

        # 2. setup.md
        with open(exp_dir / "setup.md", "w", encoding="utf-8") as f:
            f.write(f"""# Experiment {exp_id} — Setup & Methodology

## Execution Parameters
- **Experiment ID**: `{exp_id}`
- **Automated Pipeline**: `atlas.pipeline.pipeline.EvidencePipeline`
- **Scoring Ruleset**: `atlas/config/scoring_rules.json`

## Reproduction Commands
```bash
python3 scripts/run_pipeline.py <TARGET_URL>
```
""")

        # 3. notes.md
        with open(exp_dir / "notes.md", "w", encoding="utf-8") as f:
            f.write(f"""# Experiment {exp_id} — Field Notes & Observations

*Log experimental notes, intermediate hypotheses, and unexpected findings here.*

- `{created_at}`: Experiment ledger record initialized.
""")

        # 4. result.md
        with open(exp_dir / "result.md", "w", encoding="utf-8") as f:
            f.write(f"""# Experiment {exp_id} — Results & Conclusions

**Status**: `in_progress`

## Findings Ledger
*No findings finalized yet.*

## Conclusions
*To be populated upon experiment completion.*
""")

        # 5. experiment.json metadata
        exp_model = Experiment(
            experiment_id=exp_id,
            title=title,
            hypothesis=hypothesis,
            status=ExperimentStatus.PROPOSED,
            created_at=created_at,
            target_urls=target_urls,
            findings=[],
            notes=[f"Initialized at {created_at}"]
        )
        with open(exp_dir / "experiment.json", "w", encoding="utf-8") as f:
            f.write(exp_model.model_dump_json(indent=2))

        logger.info(f"Experiment {exp_id} successfully created at {exp_dir}")
        return exp_dir
