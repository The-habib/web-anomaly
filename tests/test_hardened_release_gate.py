"""
Comprehensive Unit & Adversarial Tests for the 15-Point Hardened Release Gate.
Verifies that all 15 release checks execute real property tests and correctly reject
10 deliberate adversarial attacks (tampering, fake reviewers, score injection, memory breach).
"""

import pytest
import json
import tempfile
import hashlib
from pathlib import Path

from atlas.treasure.release_gate import run_treasure_release_gate
from atlas.treasure.models import validate_state_transition, TreasureState
from atlas.review.packet_v2 import validate_packet_v2_neutrality
from atlas.review.importer import import_human_reviews
from atlas.memory.engine import CrossRunMemoryStore, MemoryDomain
from atlas.knowledge.entities import EntityRecord, EntityType
from atlas.knowledge.relations import GraphEdge, RelationType, RelationConfidence
from atlas.knowledge.graph import ArchaeologicalKnowledgeGraph
from atlas.knowledge.integrity import validate_graph_integrity

def test_full_15_point_release_gate_passes_cleanly():
    """Verify that the un-tampered Run #003 passes all 15 release gates."""
    res = run_treasure_release_gate(run_id="TREASURE_RUN_0003")
    assert res["total_checks"] == 15
    assert res["checks_passed"] == 15
    assert res["all_passed"] is True
    assert res["release_status"] == "APPROVED_FOR_TREASURE_DISCOVERY"

# 10 Adversarial Attack Tests

def test_adversarial_attack_1_insert_score_into_packet():
    bad_packet = {
        "review_packet_id": "REV_ATTACK_01",
        "candidate_id": "TCAND_0001",
        "source_url": "https://example.com/page.html",
        "anomaly_score": 99.9
    }
    is_valid, viols = validate_packet_v2_neutrality(bad_packet)
    assert is_valid is False
    assert any("anomaly_score" in v for v in viols)

def test_adversarial_attack_2_insert_strategy_into_packet():
    bad_packet = {
        "review_packet_id": "REV_ATTACK_02",
        "candidate_id": "TCAND_0001",
        "strategy": "USER_SPACE"
    }
    is_valid, viols = validate_packet_v2_neutrality(bad_packet)
    assert is_valid is False
    assert any("strategy" in v for v in viols)

def test_adversarial_attack_3_insert_prohibited_phrase_into_packet():
    bad_packet = {
        "review_packet_id": "REV_ATTACK_03",
        "candidate_id": "TCAND_0001",
        "text": "This page shows long-term survival from 1998."
    }
    is_valid, viols = validate_packet_v2_neutrality(bad_packet)
    assert is_valid is False
    assert any("long-term survival" in v for v in viols)

def test_adversarial_attack_4_fake_bot_review_injection():
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_file = Path(tmpdir) / "fake_reviews.jsonl"
        with open(fake_file, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "review_id": "REV_001",
                "reviewer_id": "AUTOMATED_LLM_REVIEWER",
                "candidate_id": "TCAND_0001",
                "verdict": "CLEAR_TREASURE",
                "confidence": 1.0,
                "notes": "Auto validated."
            }) + "\n")
        imported, summary = import_human_reviews(fake_file, known_candidates={"TCAND_0001"})
        assert summary.valid_reviews_imported == 0
        assert summary.rejected_reviews_count == 1
        assert any("Machine/system reviewer ID forbidden" in r for r in summary.rejections)

def test_adversarial_attack_5_unreviewed_promotion_attempt():
    with pytest.raises(ValueError):
        validate_state_transition(
            TreasureState.CANDIDATE,
            TreasureState.VALIDATED_TREASURE,
            is_human_review=False
        )

def test_adversarial_attack_6_artifact_tampering_detected():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        inv_f = tmp_path / "investigations.jsonl"
        art_dir = tmp_path / "evidence" / "raw_artifacts"
        art_dir.mkdir(parents=True, exist_ok=True)

        fake_art = art_dir / "test.html"
        fake_art.write_text("Modified content", encoding="utf-8")
        
        with open(inv_f, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "candidate_id": "TCAND_0001",
                "domain": "test.com",
                "url": "https://test.com",
                "evidence_artifact_path": str(fake_art),
                "sha256_hash": "0000000000000000000000000000000000000000000000000000000000000000"
            }) + "\n")

        res = run_treasure_release_gate(data_dir=tmp_path)
        assert res["checks"]["EVIDENCE_INTEGRITY"]["passed"] is False

def test_adversarial_attack_7_checkpoint_tampering_detected():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        manifest_f = tmp_path / "run_manifest.json"
        manifest_f.write_text(json.dumps({"run_id": "WRONG_ID"}), encoding="utf-8")
        
        res = run_treasure_release_gate(data_dir=tmp_path, run_id="TREASURE_RUN_0003")
        assert res["checks"]["CHECKPOINT_INTEGRITY"]["passed"] is False

def test_adversarial_attack_8_memory_leakage_rejected():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = CrossRunMemoryStore(Path(tmpdir))
        with pytest.raises(PermissionError):
            store.query(MemoryDomain.REVIEW_MEMORY, "TEST_KEY", execution_mode="LIVE_BLIND")

def test_adversarial_attack_9_dangling_graph_relationship_detected():
    kg = ArchaeologicalKnowledgeGraph()
    e1 = EntityRecord(
        entity_id="DOM_01",
        entity_type=EntityType.DOMAIN,
        name="domain1.com",
        created_at_utc="2026-08-18T00:00:00Z",
        source_run_id="TEST",
        provenance_source="TEST"
    )
    kg.add_entity(e1)
    
    # In kg.edges, directly inject dangling edge pointing to non-existent target DOM_02
    rel = GraphEdge(
        edge_id="EDGE_01",
        source_entity_id="DOM_01",
        target_entity_id="DOM_02",  # Missing target entity
        relation_type=RelationType.HOSTS,
        confidence=RelationConfidence.OBSERVED,
        created_at_utc="2026-08-18T00:00:00Z",
        source_run_id="TEST"
    )
    kg.edges[rel.edge_id] = rel
    
    is_valid, violations = validate_graph_integrity(kg)
    assert is_valid is False
    assert any("has non-existent target 'DOM_02'" in v for v in violations)

def test_adversarial_attack_10_multi_candidate_cluster_collapsing():
    from atlas.similarity.clustering import cluster_archaeological_candidates
    candidates = [
        {"candidate_id": "C1", "domain": "cosmic.voyage", "url": "https://cosmic.voyage/sub1.html", "path": "/sub1.html"},
        {"candidate_id": "C2", "domain": "cosmic.voyage", "url": "https://cosmic.voyage/sub2.html", "path": "/sub2.html"},
        {"candidate_id": "C3", "domain": "cosmic.voyage", "url": "https://cosmic.voyage/sub3.html", "path": "/sub3.html"}
    ]
    clusters = cluster_archaeological_candidates(candidates)
    vintage_cluster = next((c for c in clusters if c.cluster_id == "CLUS-VINTAGE_WEB_COMMUNITIES"), None)
    assert vintage_cluster is not None
    assert len(vintage_cluster.site_clusters) == 1
    sc = vintage_cluster.site_clusters[0]
    assert sc.domain == "cosmic.voyage"
    assert sc.is_multi_candidate_site is True
    assert len(sc.candidate_ids) == 3
    assert sc.exhibit_collapsing_policy == "COLLAPSE_TO_SINGLE_EXHIBIT_UNLESS_INDEPENDENT"
