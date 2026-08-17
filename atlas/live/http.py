"""Live HTTP fetching and HTML DOM architectural feature extraction."""

import time
import hashlib
import requests
from pathlib import Path
from typing import Tuple, List, Dict, Optional
from bs4 import BeautifulSoup

from atlas.core.config import DEFAULT_USER_AGENT
from atlas.live.models import LiveEvidenceRecord, EvidenceFailureRecord, CollectionAuditLogEntry
from atlas.live.logger import LiveAuditLogger
from atlas.live.guard import assert_live_mode

# Modern framework signatures
FRAMEWORK_SIGNATURES = {
    "Next.js": ["__NEXT_DATA__", "_next/static"],
    "React": ["data-reactroot", "react-dom", "_reactListening"],
    "Vue": ["data-v-", "vue.js", "__VUE__"],
    "Angular": ["ng-version", "ng-app"],
    "Bootstrap": ["bootstrap.min.css", "bootstrap.bundle.min.js"],
    "TailwindCSS": ["tailwind", "tw-"],
    "WordPress": ["wp-content", "wp-includes"],
    "USWDS": ["usa-banner", "usa-header", "uswds"]
}

def fetch_live_page(
    domain: str,
    raw_artifacts_dir: Path = Path("data/phase1_3_live/evidence/raw_artifacts"),
    timeout: int = 10,
    audit_logger: Optional[LiveAuditLogger] = None
) -> Tuple[Optional[LiveEvidenceRecord], Optional[EvidenceFailureRecord]]:
    """
    Perform a real HTTP request to the target domain, extracting architectural features.
    Saves the exact raw HTML payload to disk with SHA-256 verification.
    """
    assert_live_mode(f"Live HTTP Fetch for {domain}")

    raw_artifacts_dir.mkdir(parents=True, exist_ok=True)
    if audit_logger is None:
        audit_logger = LiveAuditLogger()

    start_time = time.time()
    url = f"https://{domain}"
    redirect_chain: List[str] = []

    session = requests.Session()
    session.headers.update({
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    })

    try:
        try:
            resp = session.get(url, timeout=timeout, allow_redirects=True)
        except requests.exceptions.SSLError:
            # Fallback to http if SSL fails on legacy domain
            url = f"http://{domain}"
            resp = session.get(url, timeout=timeout, allow_redirects=True)

        duration_ms = (time.time() - start_time) * 1000

        for r in resp.history:
            redirect_chain.append(r.url)
        redirect_chain.append(resp.url)

        raw_bytes = resp.content
        html_text = resp.text
        html_hash = hashlib.sha256(raw_bytes).hexdigest()

        # Save raw artifact
        clean_name = domain.replace(":", "_").replace("/", "_")
        artifact_path = raw_artifacts_dir / f"{clean_name}_live.html"
        with open(artifact_path, "wb") as f_art:
            f_art.write(raw_bytes)

        # Parse DOM structure
        soup = BeautifulSoup(html_text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        extracted_text = soup.get_text(separator=" ", strip=True)

        # Architectural Feature Detection
        has_frameset = bool(soup.find("frameset") or soup.find("frame"))
        
        # Table layout detection (tables with presentational attributes or nested tables)
        tables = soup.find_all("table")
        has_tables = False
        if len(tables) > 0:
            for t in tables:
                if t.get("cellpadding") or t.get("cellspacing") or t.get("border") in ("0", "1"):
                    has_tables = True
                    break
                if t.find("table"):  # Nested table structure typical of 1990s layout
                    has_tables = True
                    break

        # Retro markup detection (<font>, <center>, <marquee>, <blink>, inline bgcolor)
        retro_tags = bool(
            soup.find("font") or
            soup.find("center") or
            soup.find("marquee") or
            soup.find("blink") or
            soup.find(lambda el: el.has_attr("bgcolor") or el.has_attr("background"))
        )

        # Inline style density check
        inline_style_count = len(soup.find_all(lambda el: el.has_attr("style")))
        has_inline = inline_style_count > 5

        # Modern framework detection
        detected_frameworks: List[str] = []
        html_lower = html_text.lower()
        for fw_name, sigs in FRAMEWORK_SIGNATURES.items():
            if any(s.lower() in html_lower for s in sigs):
                detected_frameworks.append(fw_name)

        record = LiveEvidenceRecord(
            domain=domain,
            requested_url=url,
            final_url=resp.url,
            redirect_chain=redirect_chain,
            http_status=resp.status_code,
            content_type=resp.headers.get("Content-Type", ""),
            collection_duration_ms=round(duration_ms, 2),
            page_title=title[:200],
            html_raw_sha256=html_hash,
            html_bytes=len(raw_bytes),
            extracted_text_bytes=len(extracted_text.encode("utf-8")),
            raw_artifact_path=str(artifact_path),
            frameworks_detected=detected_frameworks,
            has_tables_layout=has_tables,
            has_inline_styles=has_inline,
            has_frameset=has_frameset,
            has_retro_elements=retro_tags,
            collection_method="LIVE_HTTP_REQUEST",
            provenance_verified=True
        )

        audit_logger.log_live_event(CollectionAuditLogEntry(
            domain=domain,
            source="LIVE_HTTP",
            operation="GET",
            status="SUCCESS" if resp.status_code < 400 else f"HTTP_{resp.status_code}",
            duration_ms=round(duration_ms, 2),
            bytes_received=len(raw_bytes),
            artifact_hash=html_hash
        ))

        return record, None

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        err_msg = str(e)
        err_code = "TIMEOUT" if "timeout" in err_msg.lower() else "CONNECTION_ERROR"

        fail_rec = EvidenceFailureRecord(
            domain=domain,
            target_url=url,
            stage="LIVE_HTTP",
            error_code=err_code,
            error_message=err_msg,
            fallback_action="RECORD_FAILURE_AS_INSUFFICIENT_EVIDENCE"
        )

        audit_logger.log_error_event(CollectionAuditLogEntry(
            domain=domain,
            source="LIVE_HTTP",
            operation="GET",
            status="FAILURE",
            duration_ms=round(duration_ms, 2),
            bytes_received=0,
            error=err_msg
        ))

        return None, fail_rec
