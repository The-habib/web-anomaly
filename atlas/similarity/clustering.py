"""
Archaeological Clustering Subsystem for Project Atlas.
Groups candidate artifacts and domains into evidence-based archaeological families:
UNIX_USER_SPACES, UNIVERSITY_FACULTY_PAGES, LEGACY_GOVERNMENT_DOCUMENTS,
FORGOTTEN_SOFTWARE_REPOSITORIES, MIRROR_NETWORKS, HISTORICAL_WEB_COMMUNITIES.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field

class ArchaeologicalCluster(BaseModel):
    cluster_id: str
    cluster_name: str  # UNIX_USER_SPACES, UNIVERSITY_FACULTY_PAGES, etc.
    description: str
    member_candidate_ids: List[str] = Field(default_factory=list)
    member_domains: List[str] = Field(default_factory=list)
    common_features: List[str] = Field(default_factory=list)
    exemplar_candidate_id: str

def cluster_archaeological_candidates(
    candidates_data: List[Dict[str, Any]]
) -> List[ArchaeologicalCluster]:
    """Group candidates into evidence-backed clusters based on structural/platform signatures."""
    clusters_map: Dict[str, Dict[str, Any]] = {
        "UNIX_USER_SPACES": {
            "name": "Unix & Tilde Personal Spaces",
            "desc": "Personal home directories with tilde path prefixes and retro markup",
            "candidates": [],
            "domains": set(),
            "features": ["tilde_path", "minimal_css", "personal_bio"]
        },
        "UNIVERSITY_PERSONAL_PAGES": {
            "name": "Academic Faculty & Student Directories",
            "desc": "Institutional academic faculty directories and syllabus repositories",
            "candidates": [],
            "domains": set(),
            "features": ["academic_domain", "table_curriculum", "publications_list"]
        },
        "LEGACY_GOVERNMENT_DOCUMENTS": {
            "name": "Historical Government Archive Repositories",
            "desc": "Public institutional data tables, census archives, and administrative records",
            "candidates": [],
            "domains": set(),
            "features": ["gov_domain", "pre_css_tables", "plaintext_reports"]
        },
        "FORGOTTEN_PROJECT_SITES": {
            "name": "Independent Open-Source Software Sites",
            "desc": "Standalone project documentation and changelog surfaces",
            "candidates": [],
            "domains": set(),
            "features": ["changelog_markup", "source_tarball_links"]
        }
    }

    for c in candidates_data:
        cid = c.get("candidate_id", "")
        url = c.get("url", "")
        path = c.get("path", "")
        dom = c.get("domain", "")
        strat = c.get("source_strategy", "")

        if "~" in path or strat == "USER_SPACE":
            clusters_map["UNIX_USER_SPACES"]["candidates"].append(cid)
            clusters_map["UNIX_USER_SPACES"]["domains"].add(dom)
        elif dom.endswith(".edu") or "university" in dom:
            clusters_map["UNIVERSITY_PERSONAL_PAGES"]["candidates"].append(cid)
            clusters_map["UNIVERSITY_PERSONAL_PAGES"]["domains"].add(dom)
        elif dom.endswith(".gov") or dom.endswith(".cz") or "census" in dom:
            clusters_map["LEGACY_GOVERNMENT_DOCUMENTS"]["candidates"].append(cid)
            clusters_map["LEGACY_GOVERNMENT_DOCUMENTS"]["domains"].add(dom)
        else:
            clusters_map["FORGOTTEN_PROJECT_SITES"]["candidates"].append(cid)
            clusters_map["FORGOTTEN_PROJECT_SITES"]["domains"].add(dom)

    result_clusters = []
    for k, v in clusters_map.items():
        if v["candidates"]:
            result_clusters.append(ArchaeologicalCluster(
                cluster_id=f"CLUS-{k}",
                cluster_name=v["name"],
                description=v["desc"],
                member_candidate_ids=v["candidates"],
                member_domains=sorted(list(v["domains"])),
                common_features=v["features"],
                exemplar_candidate_id=v["candidates"][0]
            ))

    return result_clusters
