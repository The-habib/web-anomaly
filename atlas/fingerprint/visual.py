"""
Visual Layout Fingerprint Subsystem for Project Atlas.
Extracts geometry, block density, whitespace distribution, and layout patterns from DOM.
"""

from typing import Dict, Any, List
from bs4 import BeautifulSoup
from pydantic import BaseModel

class VisualLayoutFingerprint(BaseModel):
    block_container_count: int
    sidebar_detected: bool
    navigation_bar_detected: bool
    text_to_markup_ratio: float
    estimated_whitespace_density: float
    dominant_geometry: str  # TABLE_GRID, SINGLE_COLUMN_TEXT, MULTI_COLUMN_CONTAINER, MINIMAL_PREFORMATTED
    visual_complexity_score: float
    visual_hash: str

def compute_visual_fingerprint(html: str) -> VisualLayoutFingerprint:
    """Analyze DOM elements to extract visual layout geometry metrics."""
    import hashlib
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style for text calculation
    for s in soup(["script", "style"]):
        s.decompose()

    text_len = len(soup.get_text())
    html_len = max(1, len(html))
    text_ratio = round(text_len / html_len, 4)

    # Containers
    divs = soup.find_all("div")
    sections = soup.find_all(["section", "article", "main", "aside"])
    blocks = len(divs) + len(sections)

    # Sidebars & Navigation
    sidebar = bool(soup.find(["aside"]) or soup.find(id=lambda i: i and "sidebar" in i.lower()) or soup.find(class_=lambda c: c and "sidebar" in str(c).lower()))
    nav = bool(soup.find(["nav"]) or soup.find(id=lambda i: i and "nav" in i.lower()) or soup.find(class_=lambda c: c and "nav" in str(c).lower()))

    # Dominant geometry
    tables = soup.find_all("table")
    pres = soup.find_all("pre")

    if len(pres) >= 1 and text_len > 200 and len(divs) < 3:
        geometry = "MINIMAL_PREFORMATTED"
    elif len(tables) >= 2 or (len(tables) == 1 and len(soup.find_all("td")) > 6):
        geometry = "TABLE_GRID"
    elif blocks >= 10:
        geometry = "MULTI_COLUMN_CONTAINER"
    else:
        geometry = "SINGLE_COLUMN_TEXT"

    # Whitespace and complexity
    whitespace_density = round(min(1.0, max(0.0, 1.0 - (text_ratio * 2))), 3)
    complexity = round(min(100.0, (blocks * 1.5) + (len(tables) * 4) + (len(soup.find_all("a")) * 0.5)), 2)

    vis_repr = f"{geometry}|{blocks}|{sidebar}|{nav}|{text_ratio}|{complexity}"
    v_hash = hashlib.sha256(vis_repr.encode("utf-8")).hexdigest()[:16]

    return VisualLayoutFingerprint(
        block_container_count=blocks,
        sidebar_detected=sidebar,
        navigation_bar_detected=nav,
        text_to_markup_ratio=text_ratio,
        estimated_whitespace_density=whitespace_density,
        dominant_geometry=geometry,
        visual_complexity_score=complexity,
        visual_hash=v_hash
    )
