"""Structured audit logger for Phase 1.3 Live Evidence operations."""

import json
from pathlib import Path
from typing import Optional
from atlas.live.models import CollectionAuditLogEntry

class LiveAuditLogger:
    """Thread-safe and file-backed structured logger recording all live network operations."""

    def __init__(self, log_dir: Path = Path("logs/phase1_3")):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.live_log_file = self.log_dir / "live_collection.jsonl"
        self.archive_log_file = self.log_dir / "archive_collection.jsonl"
        self.error_log_file = self.log_dir / "collection_errors.jsonl"

    def log_live_event(self, entry: CollectionAuditLogEntry):
        with open(self.live_log_file, "a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")

    def log_archive_event(self, entry: CollectionAuditLogEntry):
        with open(self.archive_log_file, "a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")

    def log_error_event(self, entry: CollectionAuditLogEntry):
        with open(self.error_log_file, "a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")
