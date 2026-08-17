"""Historical Surface Discovery & Candidate Path Extraction for Phase 1.5."""

import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Set
from atlas.deep.models import PathCandidate, PathCategory

HISTORICAL_PATH_PATTERNS = {
    PathCategory.ACADEMIC_USER_SPACE: re.compile(r"(/~|/~[a-zA-Z0-9_\-\.]+)", re.IGNORECASE),
    PathCategory.ARCHIVE_DIRECTORY: re.compile(r"/(old|archive|archives|history|legacy|retro|classic)(/|$)", re.IGNORECASE),
    PathCategory.LEGACY_DOCS: re.compile(r"/(doc|docs|documentation|man|rfc|manual|faq)(/|$)", re.IGNORECASE),
    PathCategory.PUBLIC_FILES: re.compile(r"/(pub|public|files|download|downloads|releases|dist)(/|$)", re.IGNORECASE),
    PathCategory.SOFTWARE_PROJECT: re.compile(r"/(project|projects|software|code|src)(/|$)", re.IGNORECASE),
    PathCategory.PERSONAL_BLOG: re.compile(r"/(people|staff|faculty|members|users|personal|homepages|blog)(/|$)", re.IGNORECASE),
    PathCategory.YEAR_PREFIXED: re.compile(r"/(199[0-9]|200[0-4])(/|$)", re.IGNORECASE)
}

EXCLUDED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".css", ".js", ".woff", ".woff2", ".ttf", ".eot", ".mp3",
    ".mp4", ".avi", ".mov", ".zip", ".tar", ".gz", ".tgz", ".pdf",
    ".exe", ".dmg", ".iso"
}

def classify_path(path: str) -> PathCategory:
    for cat, pattern in HISTORICAL_PATH_PATTERNS.items():
        if pattern.search(path):
            return cat
    return PathCategory.GENERAL_DIRECTORY

def is_valid_candidate_path(path: str) -> bool:
    if not path or path == "/" or path.startswith(("/wp-content", "/wp-includes", "/cdn-cgi", "/static", "/assets")):
        return False
    lower_path = path.lower()
    for ext in EXCLUDED_EXTENSIONS:
        if lower_path.endswith(ext):
            return False
    return True

def extract_links_from_html(html: str, domain: str) -> List[PathCandidate]:
    candidates = []
    seen_paths = set()
    try:
        soup = BeautifulSoup(html, "html.parser")
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            parsed = urllib.parse.urlparse(href)
            # Internal link or relative link
            if not parsed.netloc or parsed.netloc == domain or parsed.netloc.endswith("." + domain):
                clean_path = parsed.path
                if clean_path and is_valid_candidate_path(clean_path) and clean_path not in seen_paths:
                    seen_paths.add(clean_path)
                    cat = classify_path(clean_path)
                    candidates.append(PathCandidate(
                        domain=domain,
                        candidate_url=f"https://{domain}{clean_path}",
                        path=clean_path,
                        path_category=cat,
                        discovery_source="ROOT_PAGE_LINK",
                        first_observed_year=2026,
                        last_observed_year=2026,
                        capture_count=1
                    ))
    except Exception:
        pass
    return candidates

def discover_historical_paths_cdx(
    domain: str,
    timeout: int = 8,
    limit: int = 100
) -> List[PathCandidate]:
    """
    Query Wayback Machine CDX API for distinct public path prefixes observed historically.
    """
    cdx_url = (
        f"https://web.archive.org/cdx/search/cdx"
        f"?url={domain}/*"
        f"&output=json"
        f"&fl=original,timestamp,mimetype"
        f"&filter=statuscode:200"
        f"&collapse=urlkey"
        f"&limit={limit}"
    )

    candidates = []
    seen_paths = set()

    try:
        resp = requests.get(
            cdx_url,
            headers={"User-Agent": "ProjectAtlas-DeepArchaeology/1.5 (+https://github.com/The-habib/web-anomaly)"},
            timeout=timeout
        )
        if resp.status_code == 200:
            data = resp.json()
            if len(data) > 1:
                # First row is header: ["original", "timestamp", "mimetype"]
                for row in data[1:]:
                    if len(row) >= 2:
                        orig_url = row[0]
                        ts = row[1]
                        parsed = urllib.parse.urlparse(orig_url)
                        clean_path = parsed.path
                        if is_valid_candidate_path(clean_path) and clean_path not in seen_paths:
                            seen_paths.add(clean_path)
                            year = int(ts[:4]) if len(ts) >= 4 and ts[:4].isdigit() else None
                            cat = classify_path(clean_path)
                            candidates.append(PathCandidate(
                                domain=domain,
                                candidate_url=f"https://{domain}{clean_path}",
                                path=clean_path,
                                path_category=cat,
                                discovery_source="WAYBACK_CDX",
                                first_observed_year=year,
                                last_observed_year=year,
                                capture_count=1
                            ))
    except Exception:
        pass

    return candidates
