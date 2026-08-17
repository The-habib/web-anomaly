"""Structured logging system for Project Atlas."""

import os
import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from atlas.core.config import LOGS_DIR

class AtlasLogger:
    """Structured logger providing console and file output with performance metrics."""

    def __init__(self, name: str = "atlas"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # Console handler (clean formatting)
            c_handler = logging.StreamHandler(sys.stdout)
            c_handler.setLevel(logging.INFO)
            c_formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            c_handler.setFormatter(c_formatter)
            self.logger.addHandler(c_handler)

            # Daily file handler (detailed formatting)
            today_str = datetime.utcnow().strftime("%Y%m%d")
            log_file = LOGS_DIR / f"atlas_{today_str}.log"
            f_handler = logging.FileHandler(log_file, encoding="utf-8")
            f_handler.setLevel(logging.DEBUG)
            f_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%SZ"
            )
            f_handler.setFormatter(f_formatter)
            self.logger.addHandler(f_handler)

    def info(self, msg: str, **kwargs):
        self.logger.info(msg, **kwargs)

    def debug(self, msg: str, **kwargs):
        self.logger.debug(msg, **kwargs)

    def warning(self, msg: str, **kwargs):
        self.logger.warning(msg, **kwargs)

    def error(self, msg: str, **kwargs):
        self.logger.error(msg, **kwargs)

    def exception(self, msg: str, **kwargs):
        self.logger.exception(msg, **kwargs)

    def log_action(
        self,
        action: str,
        target: str,
        duration_ms: float,
        success: bool,
        error: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Record a structured JSON action record to audit log."""
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action,
            "target": target,
            "duration_ms": round(duration_ms, 2),
            "success": success,
            "error": error,
            "extra": extra or {}
        }
        status_str = "SUCCESS" if success else "FAILURE"
        self.logger.info(f"ACTION {action} on {target} [{status_str}] ({duration_ms:.1f}ms)")
        self.logger.debug(f"ACTION_DETAIL: {json.dumps(record)}")

        # Append to audit JSONL log
        today_str = datetime.utcnow().strftime("%Y%m%d")
        audit_file = LOGS_DIR / f"audit_{today_str}.jsonl"
        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

# Global default logger instance
logger = AtlasLogger("atlas")
