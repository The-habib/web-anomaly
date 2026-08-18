"""
Orphan Path Detection Subsystem for Project Atlas.
Detects unlinked or detached historical paths on live domains by inspecting root navigation trees.
Records search scope, links checked, depth inspected, and assigns ORPHAN_CANDIDATE or ORPHAN_PROVEN.
"""

from enum import Enum
from typing import Dict, Any, List, Set, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pydantic import BaseModel

class OrphanVerdict(str, Enum):
    CONNECTED_TO_ROOT = "CONNECTED_TO_ROOT"
    ORPHAN_CANDIDATE = "ORPHAN_CANDIDATE"
    ORPHAN_PROVEN = "ORPHAN_PROVEN"
    INSUFFICIENT_SEARCH = "INSUFFICIENT_SEARCH"

class OrphanInspectionRecord(BaseModel):
    candidate_url: str
    target_path: str
    domain: str
    search_scope: str  # ROOT_PAGE_ONLY, SHALLOW_CRAWL_DEPTH_1, SITEMAP_AND_ROOT
    links_checked: int
    depth_checked: int
    found_in_navigation: bool
    verdict: OrphanVerdict
    evidence_notes: str

def inspect_orphan_status(
    target_url: str,
    domain: str,
    root_html: Optional[str] = None,
    sitemap_urls: Optional[List[str]] = None
) -> OrphanInspectionRecord:
    """
    Evaluate whether target_url is reachable from current domain root navigation.
    Guarantees explicit scope and links_checked tracking.
    """
    parsed_target = urlparse(target_url)
    target_path = parsed_target.path.rstrip("/")
    if not target_path:
        target_path = "/"

    if not root_html:
        return OrphanInspectionRecord(
            candidate_url=target_url,
            target_path=target_path,
            domain=domain,
            search_scope="NONE",
            links_checked=0,
            depth_checked=0,
            found_in_navigation=False,
            verdict=OrphanVerdict.INSUFFICIENT_SEARCH,
            evidence_notes="Root HTML not supplied for navigation inspection"
        )

    # Parse root HTML links
    soup = BeautifulSoup(root_html, "html.parser")
    links_checked = 0
    found = False

    for a in soup.find_all("a", href=True):
        links_checked += 1
        href = a["href"].strip()
        parsed = urlparse(href)
        if not parsed.netloc or parsed.netloc == domain:
            p = parsed.path.rstrip("/")
            if not p:
                p = "/"
            if p == target_path:
                found = True
                break

    if not found and sitemap_urls:
        for u in sitemap_urls:
            links_checked += 1
            if target_path in u:
                found = True
                break

    if found:
        verdict = OrphanVerdict.CONNECTED_TO_ROOT
        notes = f"Target path was found among {links_checked} inspected navigation links."
    else:
        # If checked root only, it's ORPHAN_CANDIDATE
        verdict = OrphanVerdict.ORPHAN_CANDIDATE
        notes = f"Target path was NOT linked in root navigation across {links_checked} links checked."

    return OrphanInspectionRecord(
        candidate_url=target_url,
        target_path=target_path,
        domain=domain,
        search_scope="ROOT_PAGE_ONLY",
        links_checked=links_checked,
        depth_checked=1,
        found_in_navigation=found,
        verdict=verdict,
        evidence_notes=notes
    )
