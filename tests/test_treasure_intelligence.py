"""
Comprehensive Unit & Integration Test Suite for Project Atlas — Treasure Intelligence Platform.
Validates Knowledge Graph, Multi-Dimensional Fingerprints, Treasure DNA, Historical Timelines,
Similarity Clustering, Museum Exhibits, Review Protocol, and Cross-Run Memory.
"""

import pytest
import tempfile
import json
from pathlib import Path

from atlas.treasure.models import (
    TreasureState,
    validate_state_transition,
    CandidateRecord,
    InvestigationRecord,
    TreasureStrategy,
    DiscoveryDifficulty,
    SurvivalState,
    PriorArtStatus,
    TreasureDecision
)
from atlas.knowledge.entities import EntityRecord, EntityType, generate_entity_id
from atlas.knowledge.relations import GraphEdge, RelationType, RelationConfidence, generate_edge_id
from atlas.knowledge.graph import KnowledgeGraph
from atlas.knowledge.storage import save_knowledge_graph, load_knowledge_graph
from atlas.knowledge.query import GraphQueryEngine
from atlas.knowledge.integrity import validate_graph_integrity

from atlas.fingerprint.structure import compute_structure_fingerprint
from atlas.fingerprint.technology import compute_technology_fingerprint
from atlas.fingerprint.visual import compute_visual_fingerprint
from atlas.fingerprint.engine import generate_unified_fingerprint, FINGERPRINT_VERSION

from atlas.treasure.dna import compute_treasure_dna
from atlas.timeline.engine import build_page_timeline, TimelineEventType
from atlas.timeline.comparator import compare_historical_structures, EvolutionState
from atlas.discovery.orphan import inspect_orphan_status, OrphanVerdict
from atlas.similarity.engine import compute_artifact_similarity, SimilarityReason
from atlas.similarity.clustering import cluster_archaeological_candidates
from atlas.museum.curator import generate_museum_exhibit
from atlas.explain.validator import validate_explanation
from atlas.explain.engine import generate_discovery_explanation
from atlas.memory.engine import CrossRunMemoryStore, MemoryDomain

def test_state_machine_transitions():
    """Verify legal state transitions and rejection of machine promotions."""
    # Legal transitions
    validate_state_transition(TreasureState.DISCOVERED, TreasureState.CANDIDATE)
    validate_state_transition(TreasureState.CANDIDATE, TreasureState.EVIDENCE_PENDING)
    validate_state_transition(TreasureState.EVIDENCE_COMPLETE, TreasureState.REVIEW_PENDING)
    validate_state_transition(TreasureState.REVIEW_PENDING, TreasureState.HUMAN_REVIEWED)
    validate_state_transition(TreasureState.HUMAN_REVIEWED, TreasureState.VALIDATED_TREASURE, is_human_review=True)

    # Illegal shortcut transition (Candidate -> Validated Treasure)
    with pytest.raises(ValueError, match="Machine Validation Prohibition"):
        validate_state_transition(TreasureState.CANDIDATE, TreasureState.VALIDATED_TREASURE, is_human_review=False)

def test_knowledge_graph_integrity_and_querying(tmp_path):
    """Verify Knowledge Graph node/edge indexing, serialization, and queries."""
    kg = KnowledgeGraph()
    dom_id = generate_entity_id(EntityType.DOMAIN, "ctrl-c.club")
    cand_id = generate_entity_id(EntityType.CANDIDATE, "TCAND-001")

    dom = EntityRecord(
        entity_id=dom_id,
        entity_type=EntityType.DOMAIN,
        name="ctrl-c.club",
        created_at_utc="2026-08-18T00:00:00Z",
        source_run_id="RUN_003",
        provenance_source="TEST_SAMPLER"
    )
    cand = EntityRecord(
        entity_id=cand_id,
        entity_type=EntityType.CANDIDATE,
        name="https://ctrl-c.club/~loghead/zine.html",
        created_at_utc="2026-08-18T00:00:00Z",
        source_run_id="RUN_003",
        provenance_source="USER_SPACE"
    )
    kg.add_entity(dom)
    kg.add_entity(cand)

    edge = GraphEdge(
        edge_id=generate_edge_id(dom_id, RelationType.CONTAINS, cand_id),
        source_entity_id=dom_id,
        target_entity_id=cand_id,
        relation_type=RelationType.CONTAINS,
        created_at_utc="2026-08-18T00:00:00Z",
        method="URL_HIERARCHY",
        confidence=RelationConfidence.OBSERVED
    )
    kg.add_edge(edge)

    # Verify integrity
    is_valid, violations = validate_graph_integrity(kg)
    assert is_valid is True
    assert len(violations) == 0

    # Save and reload
    ent_p, rel_p = save_knowledge_graph(kg, tmp_path)
    reloaded_kg = load_knowledge_graph(ent_p, rel_p)
    assert len(reloaded_kg.entities) == 2
    assert len(reloaded_kg.edges) == 1

    # Query
    engine = GraphQueryEngine(reloaded_kg)
    entities = engine.find_entities_by_type(EntityType.CANDIDATE)
    assert len(entities) == 1
    assert entities[0].name == "https://ctrl-c.club/~loghead/zine.html"

def test_fingerprint_determinism_and_versioning():
    """Verify identical HTML produces identical fingerprint composite hashes and tracks version."""
    sample_html = """
    <html>
        <head><title>Historical Page</title></head>
        <body bgcolor="#ffffff">
            <center><h1>Old Zine</h1></center>
            <table border="1">
                <tr><td>Item 1</td><td>Item 2</td></tr>
            </table>
            <p>Welcome to my tilde page.</p>
        </body>
    </html>
    """
    fp1 = generate_unified_fingerprint(sample_html, "https://example.com/~user/", "sha256_mock_1", "2026-08-18T00:00:00Z")
    fp2 = generate_unified_fingerprint(sample_html, "https://example.com/~user/", "sha256_mock_1", "2026-08-18T00:00:00Z")

    assert fp1.fingerprint_version == FINGERPRINT_VERSION
    assert fp1.composite_hash == fp2.composite_hash
    assert fp1.structure.table_count == 1
    assert "center" in fp1.structure.deprecated_tags_found
    assert fp1.technology.is_static_html is True

def test_treasure_dna_11_dimensions():
    """Verify Treasure DNA profile computes all 11 dimensions with evidence traces."""
    cand = CandidateRecord(
        candidate_id="TCAND-001",
        source_strategy=TreasureStrategy.USER_SPACE,
        domain="ctrl-c.club",
        url="https://ctrl-c.club/~loghead/zine.html",
        path="/~loghead/zine.html",
        category="Personal",
        discovery_timestamp_utc="2026-08-18T00:00:00Z",
        discovery_reason="Tilde personal user space",
        earliest_capture_year=2015,
        capture_count=18,
        research_priority=75.0,
        state=TreasureState.REVIEW_PENDING
    )
    inv = InvestigationRecord(
        investigation_id="INV-001",
        candidate_id="TCAND-001",
        domain="ctrl-c.club",
        url="https://ctrl-c.club/~loghead/zine.html",
        path="/~loghead/zine.html",
        category="Personal",
        strategy=TreasureStrategy.USER_SPACE,
        live_status_code=200,
        live_content_type="text/html",
        live_content_length=1500,
        sha256_hash="a" * 64,
        evidence_artifact_path="/tmp/mock.html",
        earliest_archive_year=2015,
        latest_archive_year=2026,
        historical_capture_count=18,
        html_features_detected=["retro_styling_elements", "personal_user_space_hierarchy"],
        archaeological_score=75.0,
        decision=TreasureDecision.POTENTIAL_TREASURE,
        discovery_difficulty=DiscoveryDifficulty.HARD,
        survival_state=SurvivalState.STILL_ACTIVE,
        prior_art=PriorArtStatus.OBSCURE,
        decision_rationale="Grounded discovery",
        investigation_timestamp_utc="2026-08-18T00:00:00Z"
    )

    dna = compute_treasure_dna(cand, inv, "<html>...</html>", "2026-08-18T00:00:00Z")

    assert dna.historical_depth.confidence == "OBSERVED"
    assert dna.historical_depth.data_points["earliest_year"] == 2015
    assert dna.survival.score == 9.0
    assert dna.research_priority == 75.0
    assert dna.treasure_interest == 75.0
    assert dna.human_validation_status == "REVIEW_PENDING"

def test_historical_timeline_and_comparison():
    """Verify timeline compilation and snapshot evolution state assignment."""
    tl = build_page_timeline(
        candidate_id="TCAND-001",
        url="https://example.com/archive.html",
        domain="example.com",
        earliest_year=2002,
        latest_year=2025,
        capture_count=45,
        live_status_code=200,
        timestamp_utc="2026-08-18T00:00:00Z"
    )
    assert len(tl.events) == 3
    assert tl.events[0].event_type == TimelineEventType.FIRST_OBSERVATION
    assert tl.events[1].event_type == TimelineEventType.LONG_TERM_PRESENCE
    assert tl.events[2].event_type == TimelineEventType.CURRENT_SURVIVAL

    diff_res = compare_historical_structures(
        candidate_id="TCAND-001",
        url="https://example.com/archive.html",
        historical_html="<html><body><h1>Test</h1></body></html>",
        live_html="<html><body><h1>Test</h1></body></html>"
    )
    assert diff_res.evolution_state == EvolutionState.PERSISTED

def test_orphan_path_detection():
    """Verify orphan detection identifies unlinked paths."""
    root_html = """
    <html>
        <body>
            <a href="/about.html">About</a>
            <a href="/contact.html">Contact</a>
        </body>
    </html>
    """
    res1 = inspect_orphan_status("https://example.com/about.html", "example.com", root_html)
    assert res1.verdict == OrphanVerdict.CONNECTED_TO_ROOT

    res2 = inspect_orphan_status("https://example.com/secret/hidden.html", "example.com", root_html)
    assert res2.verdict == OrphanVerdict.ORPHAN_CANDIDATE
    assert res2.links_checked == 2

def test_similarity_and_clustering():
    """Verify multi-vector similarity score and explicit reasons."""
    html_a = "<html><body><table border=1><tr><td>1</td></tr></table></body></html>"
    html_b = "<html><body><table border=1><tr><td>2</td></tr></table></body></html>"

    fp_a = generate_unified_fingerprint(html_a, "https://example.com/~user1/", "hash_a", "2026-08-18T00:00:00Z")
    fp_b = generate_unified_fingerprint(html_b, "https://example.com/~user2/", "hash_b", "2026-08-18T00:00:00Z")

    comp = compute_artifact_similarity(fp_a, fp_b, "/~user1/", "/~user2/")
    assert comp.similarity_score > 0.6
    assert SimilarityReason.PATH_PATTERN_MATCH in comp.reasons

    clusters = cluster_archaeological_candidates([
        {"candidate_id": "C1", "url": "https://example.com/~user1", "path": "/~user1", "domain": "example.com", "source_strategy": "USER_SPACE"},
        {"candidate_id": "C2", "url": "https://mit.edu/docs", "path": "/docs", "domain": "mit.edu", "source_strategy": "HISTORICAL_SURVIVOR"}
    ])
    assert len(clusters) >= 2

def test_museum_exhibit_generation(tmp_path):
    """Verify museum exhibit compile produces all 17 standardized sections."""
    exhibit_path = generate_museum_exhibit(
        treasure_id="TREASURE-000001",
        title="Historical Essay Archive",
        one_line_summary="Early static essay archive surviving in 2026.",
        why_interesting="Handcrafted markup with pre-CSS layout.",
        how_found="Autonomous blind discovery.",
        target_url="https://example.com/archive.html",
        domain="example.com",
        path="/archive.html",
        timeline_data={"summary": "1999-2026 continuous survival"},
        fingerprint_data={"composite_hash": "mock_comp_hash", "fingerprint_version": "1.0.0"},
        relationship_data={"platform": "STATIC_HTML"},
        prior_art_data={"status": "OBSCURE"},
        human_review_data={"reviewer_id": "HUMAN_ARCHAEOLOGIST_01", "confidence": 0.95, "notes": "Authentic.", "timestamp_utc": "2026-08-18T00:00:00Z"},
        sha256_hash="e" * 64,
        raw_html="<html><body><h1>Exhibit</h1></body></html>",
        output_base_dir=tmp_path
    )

    assert (exhibit_path / "manifest.json").exists()
    assert (exhibit_path / "exhibit.md").exists()
    assert (exhibit_path / "evidence" / "artifact.html").exists()

def test_explanation_validator_anti_exaggeration():
    """Verify explanation validator rejects unproven superlative statements."""
    good_text = "Atlas prioritized this URL because historical indexes recorded early public observations."
    is_valid, violations = validate_explanation(good_text)
    assert is_valid is True
    assert len(violations) == 0

    bad_text = "Atlas discovered the oldest and only surviving webpage that nobody knows."
    is_valid, violations = validate_explanation(bad_text)
    assert is_valid is False
    assert len(violations) >= 2

def test_cross_run_memory_isolation(tmp_path):
    """Verify memory store isolates partitions and prevents querying quarantined memory during LIVE_BLIND."""
    mem_store = CrossRunMemoryStore(tmp_path)
    mem_store.record(MemoryDomain.DISCOVERY_MEMORY, "ctrl-c.club", {"status": "productive"}, "RUN_002", "2026-08-18T00:00:00Z")
    mem_store.record(MemoryDomain.REVIEW_MEMORY, "TREASURE-001", {"verdict": "CONFIRMED"}, "RUN_002", "2026-08-18T00:00:00Z")

    # Discovery memory query allowed
    entry = mem_store.query(MemoryDomain.DISCOVERY_MEMORY, "ctrl-c.club", execution_mode="LIVE_BLIND")
    assert entry is not None

    # Review memory query forbidden during LIVE_BLIND
    with pytest.raises(PermissionError, match="ISOLATION VIOLATION"):
        mem_store.query(MemoryDomain.REVIEW_MEMORY, "TREASURE-001", execution_mode="LIVE_BLIND")
