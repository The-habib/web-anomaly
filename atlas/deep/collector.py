"""Targeted Retrieval & Deep Evidence Capture Module for Phase 1.5."""

import hashlib
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Optional, Tuple
from atlas.deep.models import DeepEvidenceCapture, PathCandidate
from atlas.live.http import FRAMEWORK_SIGNATURES

def fetch_and_extract_deep_evidence(
    study_id: str,
    domain: str,
    target_url: str,
    path: str,
    candidate: Optional[PathCandidate] = None,
    raw_artifacts_dir: Optional[Path] = None,
    timeout: int = 8
) -> DeepEvidenceCapture:
    """
    Fetch a targeted deep URL, extract structural signals, and freeze raw HTML.
    """
    clean_name = f"{domain}_{path.strip('/').replace('/', '_')}" if path != "/" else domain
    clean_name = clean_name[:80].replace(":", "_").replace("~", "tilde_")

    is_root = (path == "/" or not path)
    status_code = 0
    html_bytes = 0
    text_bytes = 0
    title = ""
    frameworks = []
    has_tables = False
    has_inline = False
    has_frameset = False
    has_retro = False
    has_ascii = False
    evidence_sha = "UNREACHABLE"
    artifact_path_str = None

    try:
        resp = requests.get(
            target_url,
            headers={"User-Agent": "ProjectAtlas-DeepArchaeology/1.5 (+https://github.com/The-habib/web-anomaly)"},
            timeout=timeout,
            allow_redirects=True
        )
        status_code = resp.status_code
        raw_bytes = resp.content
        html_bytes = len(raw_bytes)
        evidence_sha = hashlib.sha256(raw_bytes).hexdigest()

        if raw_artifacts_dir:
            raw_artifacts_dir.mkdir(parents=True, exist_ok=True)
            art_file = raw_artifacts_dir / f"{clean_name}.html"
            art_file.write_bytes(raw_bytes)
            artifact_path_str = str(art_file)

        soup = BeautifulSoup(raw_bytes.decode("utf-8", errors="ignore"), "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        extracted_text = soup.get_text(separator=" ", strip=True)
        text_bytes = len(extracted_text.encode("utf-8"))

        # DOM feature detection
        has_frameset = bool(soup.find("frameset") or soup.find("frame"))
        tables = soup.find_all("table")
        if len(tables) > 0:
            for t in tables:
                if t.get("cellpadding") or t.get("cellspacing") or t.get("border") in ("0", "1") or t.find("table"):
                    has_tables = True
                    break

        retro_tags = bool(
            soup.find("font") or soup.find("center") or soup.find("marquee") or
            soup.find("blink") or soup.find(lambda el: el.has_attr("bgcolor") or el.has_attr("background"))
        )
        has_retro = retro_tags

        inline_count = len(soup.find_all(lambda el: el.has_attr("style")))
        has_inline = inline_count > 5

        # Plain-Text / ASCII Layout: <pre> tags hold majority of body text
        pre_tags = soup.find_all("pre")
        if pre_tags:
            pre_text_len = sum(len(p.get_text()) for p in pre_tags)
            if pre_text_len > 100 and text_bytes > 0 and (pre_text_len / max(len(extracted_text), 1)) > 0.60:
                has_ascii = True

        html_lower = raw_bytes.decode("utf-8", errors="ignore").lower()
        for fw_name, sigs in FRAMEWORK_SIGNATURES.items():
            if any(s.lower() in html_lower for s in sigs):
                frameworks.append(fw_name)

    except Exception:
        pass

    earliest_yr = candidate.first_observed_year if candidate else None
    latest_yr = candidate.last_observed_year if candidate else None
    cdx_count = candidate.capture_count if candidate else 0

    return DeepEvidenceCapture(
        study_id=study_id,
        domain=domain,
        target_url=target_url,
        is_root=is_root,
        path=path,
        path_category=candidate.path_category if candidate else None,
        live_status_code=status_code,
        page_title=title,
        extracted_text_bytes=text_bytes,
        html_bytes=html_bytes,
        frameworks_detected=frameworks,
        has_tables_layout=has_tables,
        has_inline_styles=has_inline,
        has_frameset=has_frameset,
        has_retro_elements=has_retro,
        has_ascii_layout=has_ascii,
        cdx_capture_count=cdx_count,
        earliest_archive_year=earliest_yr,
        latest_archive_year=latest_yr,
        historical_similarity_score=0.75 if (has_tables or has_retro or has_ascii) else 0.20,
        evidence_sha256=evidence_sha,
        raw_artifact_path=artifact_path_str
    )
