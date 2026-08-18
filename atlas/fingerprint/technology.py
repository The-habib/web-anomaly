"""
Technology Stack Fingerprint Subsystem for Project Atlas.
Detects evidence-backed web technologies, server paradigms, frameworks, and legacy formats.
"""

import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from pydantic import BaseModel

class TechnologyFingerprint(BaseModel):
    primary_platform: str  # STATIC_HTML, SERVER_DIRECTORY, CGI_SSI, CMS, SSG, MODERN_JS_SPA, UNKNOWN
    detected_frameworks: List[str]
    legacy_markers_found: List[str]
    is_static_html: bool
    is_server_directory: bool
    is_cgi_or_ssi: bool
    is_modern_js_app: bool
    technology_hash: str

def compute_technology_fingerprint(html: str, url: str = "") -> TechnologyFingerprint:
    """Analyze HTML and URL patterns for evidence-backed web technology signals."""
    import hashlib
    soup = BeautifulSoup(html, "html.parser")
    html_lower = html.lower()

    frameworks = []
    legacy_markers = []

    # 1. Server Directory / Index
    is_directory = False
    title = soup.find("title")
    title_text = title.get_text().strip().lower() if title else ""
    if "index of /" in title_text or "directory listing" in title_text or "<address>apache" in html_lower or "<address>nginx" in html_lower:
        if soup.find("pre") and soup.find_all("a", href=True):
            is_directory = True

    # 2. CGI / SSI markers
    is_cgi_ssi = False
    if "/cgi-bin/" in url.lower() or ".cgi" in url.lower() or ".pl" in url.lower():
        is_cgi_ssi = True
        legacy_markers.append("CGI_URL_PATTERN")
    if "<!--#include" in html_lower or "<!--#echo" in html_lower:
        is_cgi_ssi = True
        legacy_markers.append("SSI_DIRECTIVE")

    # 3. Legacy web markers
    if soup.find(["center", "font", "marquee", "blink", "frame", "frameset"]):
        legacy_markers.append("DEPRECATED_HTML_TAGS")
    if 'bgcolor=' in html_lower or 'text=' in html_lower or 'link=' in html_lower:
        legacy_markers.append("BODY_PRESENTATIONAL_ATTRIBUTES")
    if re.search(r'generator["\']?\s+content=["\']?(frontpage|hotdog|dreamweaver|claris|pagemill|netscape)', html_lower):
        legacy_markers.append("LEGACY_AUTHORING_TOOL")
        frameworks.append("LEGACY_WYSIWYG")

    # 4. Modern JS framework markers
    is_modern_js = False
    if "react" in html_lower or "next" in html_lower or "__next" in html_lower or "_next/static" in html_lower:
        frameworks.append("REACT_NEXT")
        is_modern_js = True
    if "vue" in html_lower or "nuxt" in html_lower or "_nuxt" in html_lower:
        frameworks.append("VUE_NUXT")
        is_modern_js = True
    if "ng-" in html_lower or "angular" in html_lower:
        frameworks.append("ANGULAR")
        is_modern_js = True

    # 5. CMS markers
    if "wp-content" in html_lower or "wp-includes" in html_lower or "wordpress" in html_lower:
        frameworks.append("WORDPRESS")
    if "drupal" in html_lower:
        frameworks.append("DRUPAL")
    if "joomla" in html_lower:
        frameworks.append("JOOMLA")

    # 6. Static HTML
    is_static = False
    if not is_modern_js and not is_directory and len(soup.find_all("script")) <= 2:
        is_static = True

    # Determine primary platform
    if is_directory:
        platform = "SERVER_DIRECTORY"
    elif is_cgi_ssi:
        platform = "CGI_SSI"
    elif is_modern_js:
        platform = "MODERN_JS_SPA"
    elif any(cms in frameworks for cms in ["WORDPRESS", "DRUPAL", "JOOMLA"]):
        platform = "CMS"
    elif is_static:
        platform = "STATIC_HTML"
    else:
        platform = "LEGACY_DYNAMIC"

    tech_repr = f"{platform}|{','.join(sorted(frameworks))}|{','.join(sorted(legacy_markers))}"
    t_hash = hashlib.sha256(tech_repr.encode("utf-8")).hexdigest()[:16]

    return TechnologyFingerprint(
        primary_platform=platform,
        detected_frameworks=sorted(frameworks),
        legacy_markers_found=sorted(legacy_markers),
        is_static_html=is_static,
        is_server_directory=is_directory,
        is_cgi_or_ssi=is_cgi_ssi,
        is_modern_js_app=is_modern_js,
        technology_hash=t_hash
    )
