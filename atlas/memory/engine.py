"""
Cross-Run Memory Subsystem for Project Atlas.
Maintains 5 strictly isolated archaeological memory partitions:
DISCOVERY_MEMORY, REFERENCE_MEMORY, REVIEW_MEMORY, STRATEGY_MEMORY, EXPERIMENT_MEMORY.
Enforces runtime isolation to prevent memory leakage into blind discovery pipelines.
"""

import json
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class MemoryDomain(str, Enum):
    DISCOVERY_MEMORY = "DISCOVERY_MEMORY"
    REFERENCE_MEMORY = "REFERENCE_MEMORY"
    REVIEW_MEMORY = "REVIEW_MEMORY"
    STRATEGY_MEMORY = "STRATEGY_MEMORY"
    EXPERIMENT_MEMORY = "EXPERIMENT_MEMORY"

class MemoryEntry(BaseModel):
    entry_id: str
    memory_domain: MemoryDomain
    source_run_id: str
    key: str
    value: Dict[str, Any]
    created_at_utc: str
    is_quarantined_from_live_blind: bool = True

class CrossRunMemoryStore:
    """Isolated persistence manager for cross-run historical memory."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.partitions: Dict[MemoryDomain, Dict[str, MemoryEntry]] = {
            dom: {} for dom in MemoryDomain
        }
        self.load_all()

    def record(self, domain: MemoryDomain, key: str, value: Dict[str, Any], run_id: str, timestamp_utc: str) -> MemoryEntry:
        """Store a memory entry in an isolated partition."""
        entry_id = f"MEM-{domain.value[:3]}-{key[:12]}"
        entry = MemoryEntry(
            entry_id=entry_id,
            memory_domain=domain,
            source_run_id=run_id,
            key=key,
            value=value,
            created_at_utc=timestamp_utc,
            is_quarantined_from_live_blind=True
        )
        self.partitions[domain][key] = entry
        self._append_entry(domain, entry)
        return entry

    def query(self, domain: MemoryDomain, key: str, execution_mode: str = "LIVE_BLIND") -> Optional[MemoryEntry]:
        """Query memory with strict LIVE_BLIND isolation check."""
        if execution_mode == "LIVE_BLIND" and domain in (MemoryDomain.REFERENCE_MEMORY, MemoryDomain.REVIEW_MEMORY):
            raise PermissionError(
                f"[ISOLATION VIOLATION] Attempted to query quarantined memory partition '{domain.value}' during LIVE_BLIND execution mode."
            )
        return self.partitions[domain].get(key)

    def _append_entry(self, domain: MemoryDomain, entry: MemoryEntry) -> None:
        file_path = self.base_dir / f"{domain.value.lower()}.jsonl"
        with open(file_path, "a", encoding="utf-8") as f:
            data = entry.model_dump()
            data["schema_version"] = "1.0.0"
            f.write(json.dumps(data) + "\n")

    def load_all(self) -> None:
        for dom in MemoryDomain:
            fpath = self.base_dir / f"{dom.value.lower()}.jsonl"
            if fpath.exists():
                with open(fpath, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            data = json.loads(line)
                            data.pop("schema_version", None)
                            entry = MemoryEntry(**data)
                            self.partitions[dom][entry.key] = entry
