"""
Archaeological Clustering & Site Collapsing Subsystem for Project Atlas.
Groups candidate artifacts and domains into evidence-based archaeological families:
UNIX_USER_SPACES, UNIVERSITY_PERSONAL_PAGES, LEGACY_GOVERNMENT_DOCUMENTS,
FORGOTTEN_PROJECT_SITES, VINTAGE_WEB_COMMUNITIES.

Enforces Site-Cluster Collapsing:
Multiple candidate URLs belonging to the same domain or archaeological platform
(e.g., cosmic.voyage subpages) are grouped into a single SiteCluster so that
a domain cluster does not automatically spawn multiple separate museum exhibits.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from pathlib import Path
import json

class ClusterConfidence(str):
    OBSERVED = "OBSERVED"
    INFERRED = "INFERRED"
    POSSIBLE = "POSSIBLE"

class SiteCluster(BaseModel):
    """
    Represents DOMAIN -> ARCHAEOLOGICAL_CLUSTER -> MULTIPLE_CANDIDATE_PAGES.
    Prevents single-site URL proliferation from distorting exhibit counts.
    """
    site_cluster_id: str
    domain: str
    archetype: str
    candidate_urls: List[str] = Field(default_factory=list)
    candidate_ids: List[str] = Field(default_factory=list)
    confidence: str = "OBSERVED"
    exhibit_collapsing_policy: str = "COLLAPSE_TO_SINGLE_EXHIBIT_UNLESS_INDEPENDENT"
    is_multi_candidate_site: bool = False
    notes: str = ""

class ArchaeologicalCluster(BaseModel):
    cluster_id: str
    cluster_name: str
    description: str
    member_candidate_ids: List[str] = Field(default_factory=list)
    member_domains: List[str] = Field(default_factory=list)
    common_features: List[str] = Field(default_factory=list)
    exemplar_candidate_id: str
    site_clusters: List[SiteCluster] = Field(default_factory=list)

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
        },
        "VINTAGE_WEB_COMMUNITIES": {
            "name": "Vintage Web Communities & Fiction Archives",
            "desc": "Serialized zines, retro fiction logs, and community portals",
            "candidates": [],
            "domains": set(),
            "features": ["retro_fiction_markup", "handcrafted_html", "vintage_log"]
        }
    }

    # Group by domain for SiteCluster collapsing
    domain_to_cands: Dict[str, List[Dict[str, Any]]] = {}
    for c in candidates_data:
        dom = c.get("domain", "")
        if dom:
            domain_to_cands.setdefault(dom, []).append(c)

    for c in candidates_data:
        cid = c.get("candidate_id", "")
        url = c.get("url", "")
        path = c.get("path", "")
        dom = c.get("domain", "")
        strat = c.get("source_strategy", "")

        if "cosmic.voyage" in dom or "theoldnet.com" in dom:
            clusters_map["VINTAGE_WEB_COMMUNITIES"]["candidates"].append(cid)
            clusters_map["VINTAGE_WEB_COMMUNITIES"]["domains"].add(dom)
        elif "~" in path or strat == "USER_SPACE":
            clusters_map["UNIX_USER_SPACES"]["candidates"].append(cid)
            clusters_map["UNIX_USER_SPACES"]["domains"].add(dom)
        elif dom.endswith(".edu") or "university" in dom:
            clusters_map["UNIVERSITY_PERSONAL_PAGES"]["candidates"].append(cid)
            clusters_map["UNIVERSITY_PERSONAL_PAGES"]["domains"].add(dom)
        elif dom.endswith(".gov") or dom.endswith(".cz") or "census" in dom or "senate" in dom:
            clusters_map["LEGACY_GOVERNMENT_DOCUMENTS"]["candidates"].append(cid)
            clusters_map["LEGACY_GOVERNMENT_DOCUMENTS"]["domains"].add(dom)
        else:
            clusters_map["FORGOTTEN_PROJECT_SITES"]["candidates"].append(cid)
            clusters_map["FORGOTTEN_PROJECT_SITES"]["domains"].add(dom)

    result_clusters = []
    for k, v in clusters_map.items():
        if v["candidates"]:
            # Build site clusters for this archetype
            site_clusters: List[SiteCluster] = []
            for d in sorted(list(v["domains"])):
                d_cands = domain_to_cands.get(d, [])
                c_urls = [dc.get("url", "") for dc in d_cands]
                c_ids = [dc.get("candidate_id", "") for dc in d_cands]
                is_multi = len(c_ids) > 1
                site_clusters.append(SiteCluster(
                    site_cluster_id=f"SITE-{d.replace('.', '-')}",
                    domain=d,
                    archetype=v["name"],
                    candidate_urls=c_urls,
                    candidate_ids=c_ids,
                    confidence="OBSERVED" if is_multi else "INFERRED",
                    is_multi_candidate_site=is_multi,
                    notes=f"Contains {len(c_ids)} subpage candidate(s)."
                ))

            result_clusters.append(ArchaeologicalCluster(
                cluster_id=f"CLUS-{k}",
                cluster_name=v["name"],
                description=v["desc"],
                member_candidate_ids=v["candidates"],
                member_domains=sorted(list(v["domains"])),
                common_features=v["features"],
                exemplar_candidate_id=v["candidates"][0],
                site_clusters=site_clusters
            ))

    return result_clusters

def generate_cluster_audit(
    clusters: List[ArchaeologicalCluster],
    output_file: Path = Path("data/treasure_intelligence/audit/cluster_audit.json")
) -> Dict[str, Any]:
    """Generate comprehensive site cluster audit."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    total_sites = sum(len(c.site_clusters) for c in clusters)
    multi_sites = [sc for c in clusters for sc in c.site_clusters if sc.is_multi_candidate_site]

    audit_data = {
        "total_archetype_clusters": len(clusters),
        "total_site_clusters": total_sites,
        "multi_candidate_site_clusters": len(multi_sites),
        "collapsed_multi_candidate_sites": [
            {
                "domain": ms.domain,
                "candidate_count": len(ms.candidate_ids),
                "policy": ms.exhibit_collapsing_policy
            }
            for ms in multi_sites
        ],
        "clusters_summary": [
            {
                "cluster_id": c.cluster_id,
                "name": c.cluster_name,
                "candidate_count": len(c.member_candidate_ids),
                "domain_count": len(c.member_domains)
            }
            for c in clusters
        ]
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)

    return audit_data
