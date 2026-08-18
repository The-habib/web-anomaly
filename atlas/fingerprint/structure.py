"""
HTML Structure Fingerprint Subsystem for Project Atlas.
Extracts normalized structural vectors from raw HTML DOM representations.
"""

from typing import Dict, Any, List
from bs4 import BeautifulSoup
from pydantic import BaseModel

DEPRECATED_HTML_TAGS = {
    "center", "font", "marquee", "blink", "frame", "frameset",
    "noframes", "big", "strike", "tt", "applet", "basefont", "dir"
}

class HtmlStructureFingerprint(BaseModel):
    total_dom_nodes: int
    max_tree_depth: int
    table_count: int
    table_cell_count: int
    table_density_ratio: float
    form_count: int
    frameset_present: bool
    link_count: int
    heading_count: int
    list_count: int
    image_count: int
    script_count: int
    stylesheet_count: int
    inline_style_count: int
    deprecated_tag_count: int
    deprecated_tags_found: List[str]
    structural_hash: str

def compute_structure_fingerprint(html: str) -> HtmlStructureFingerprint:
    """Extract deterministic structural metrics from raw HTML."""
    import hashlib
    soup = BeautifulSoup(html, "html.parser")

    all_tags = soup.find_all(True)
    total_nodes = len(all_tags)

    # Max depth
    def get_depth(elem, curr=0):
        if not hasattr(elem, "children"):
            return curr
        children = [c for c in elem.children if hasattr(c, "children")]
        if not children:
            return curr
        return max(get_depth(c, curr + 1) for c in children)

    max_depth = get_depth(soup) if total_nodes > 0 else 0

    tables = soup.find_all("table")
    cells = soup.find_all(["td", "th"])
    table_count = len(tables)
    cell_count = len(cells)
    table_density = (cell_count / max(1, total_nodes))

    forms = len(soup.find_all("form"))
    frameset = bool(soup.find(["frameset", "frame"]))
    links = len(soup.find_all("a"))
    headings = len(soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]))
    lists = len(soup.find_all(["ul", "ol", "dl"]))
    images = len(soup.find_all("img"))
    scripts = len(soup.find_all("script"))
    stylesheets = len(soup.find_all("link", rel=lambda r: r and "stylesheet" in r))
    inline_styles = len([t for t in all_tags if t.get("style")])

    deprecated_found = []
    for tag in all_tags:
        if tag.name and tag.name.lower() in DEPRECATED_HTML_TAGS:
            if tag.name.lower() not in deprecated_found:
                deprecated_found.append(tag.name.lower())

    struct_repr = (
        f"{total_nodes}|{max_depth}|{table_count}|{cell_count}|{forms}|"
        f"{frameset}|{links}|{headings}|{lists}|{images}|{scripts}|{stylesheets}|{inline_styles}|"
        f"{','.join(sorted(deprecated_found))}"
    )
    s_hash = hashlib.sha256(struct_repr.encode("utf-8")).hexdigest()[:16]

    return HtmlStructureFingerprint(
        total_dom_nodes=total_nodes,
        max_tree_depth=max_depth,
        table_count=table_count,
        table_cell_count=cell_count,
        table_density_ratio=round(table_density, 4),
        form_count=forms,
        frameset_present=frameset,
        link_count=links,
        heading_count=headings,
        list_count=lists,
        image_count=images,
        script_count=scripts,
        stylesheet_count=stylesheets,
        inline_style_count=inline_styles,
        deprecated_tag_count=len(deprecated_found),
        deprecated_tags_found=sorted(deprecated_found),
        structural_hash=s_hash
    )
