"""Headless screenshot capture module using Playwright."""

import hashlib
import time
from pathlib import Path
from typing import Optional, Tuple
from playwright.sync_api import sync_playwright

from atlas.core.config import SCREENSHOTS_DIR, PLAYWRIGHT_NAVIGATION_TIMEOUT_MS, PLAYWRIGHT_VIEWPORT
from atlas.core.logger import logger
from atlas.core.models import ArtifactType, EvidenceArtifact

def capture_screenshot(url: str, output_prefix: str) -> Tuple[Optional[EvidenceArtifact], Optional[str]]:
    """
    Capture high-resolution screenshot using headless Chromium.
    Returns (EvidenceArtifact, error_string).
    """
    start_time = time.time()
    filename = f"{output_prefix}_screenshot.png"
    filepath = SCREENSHOTS_DIR / filename

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport=PLAYWRIGHT_VIEWPORT,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 ProjectAtlas/0.1"
            )
            page = context.new_page()
            page.goto(url, timeout=PLAYWRIGHT_NAVIGATION_TIMEOUT_MS, wait_until="networkidle")
            page.screenshot(path=str(filepath), full_page=True)
            browser.close()

        # Calculate file hash and size
        with open(filepath, "rb") as f:
            content = f.read()
            sha256 = hashlib.sha256(content).hexdigest()
            size = len(content)

        artifact = EvidenceArtifact(
            artifact_id=f"art_ss_{output_prefix}",
            artifact_type=ArtifactType.SCREENSHOT,
            relative_path=str(filepath.relative_to(SCREENSHOTS_DIR.parent.parent)),
            file_name=filename,
            sha256=sha256,
            size_bytes=size,
            metadata={"url": url, "viewport": PLAYWRIGHT_VIEWPORT}
        )

        duration_ms = (time.time() - start_time) * 1000
        logger.log_action("capture_screenshot", url, duration_ms, True, extra={"size": size, "sha256": sha256})
        return artifact, None

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        err_msg = str(e)
        logger.log_action("capture_screenshot", url, duration_ms, False, error=err_msg)
        return None, err_msg
