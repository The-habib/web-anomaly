"""
Unit and Integration Tests for Human Review Console, Session Management, and Importer.
"""

import pytest
import tempfile
import json
from pathlib import Path
from atlas.review.console import (
    load_review_packets_v2,
    get_review_status,
    render_packet_console,
    submit_human_review,
    export_review_session,
    ReviewRecordV2
)
from atlas.review.importer import import_human_reviews

def test_load_and_render_review_packets():
    rev_dir = Path("data/treasure_runs/TREASURE_RUN_0003/review_v2")
    if not rev_dir.exists():
        pytest.skip("Review V2 dir missing")
    packets = load_review_packets_v2(rev_dir)
    assert len(packets) == 51

    rendered = render_packet_console(packets[0], 0, len(packets))
    assert "PROJECT ATLAS — EVIDENCE REVIEW CONSOLE (1/51)" in rendered
    assert "VERDICT CONTROLS" in rendered
    assert "Score" not in rendered
    assert "Strategy" not in rendered

def test_submit_human_review_and_reject_bot():
    rev_dir = Path("data/treasure_runs/TREASURE_RUN_0003/review_v2")
    if not rev_dir.exists():
        pytest.skip("Review V2 dir missing")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_rev = Path(tmpdir)
        # Copy packets
        (tmp_rev / "review_packets_v2.jsonl").write_bytes((rev_dir / "review_packets_v2.jsonl").read_bytes())
        (tmp_rev / "review_session_state.json").write_text(json.dumps({"total_packets": 51, "reviewed_count": 0}))

        # Valid submission
        rec = submit_human_review(
            packet_id="REV_PKT_V2_001",
            reviewer_id="HUMAN_ARCHAEOLOGIST_01",
            verdict="POTENTIAL_TREASURE",
            confidence=0.85,
            notes="Authentic personal log format.",
            review_v2_dir=tmp_rev
        )
        assert rec.verdict == "POTENTIAL_TREASURE"
        assert rec.confidence == 0.85

        # Bot submission rejected
        with pytest.raises(PermissionError):
            submit_human_review(
                packet_id="REV_PKT_V2_002",
                reviewer_id="AUTO_BOT_01",
                verdict="CLEAR_TREASURE",
                confidence=1.0,
                notes="Automated review.",
                review_v2_dir=tmp_rev
            )

        # Invalid verdict rejected
        with pytest.raises(ValueError):
            submit_human_review(
                packet_id="REV_PKT_V2_002",
                reviewer_id="HUMAN_ARCHAEOLOGIST_01",
                verdict="INVALID_VERDICT_NAME",
                confidence=1.0,
                notes="Invalid verdict.",
                review_v2_dir=tmp_rev
            )

def test_review_session_export_and_import():
    rev_dir = Path("data/treasure_runs/TREASURE_RUN_0003/review_v2")
    if not rev_dir.exists():
        pytest.skip("Review V2 dir missing")

    with tempfile.TemporaryDirectory() as tmpdir:
        export_f = Path(tmpdir) / "test_session.json"
        export_review_session(export_f, reviewer_id="HUMAN_ARCHAEOLOGIST_01", review_v2_dir=rev_dir)
        assert export_f.exists()

        data = json.loads(export_f.read_text(encoding="utf-8"))
        assert data["total_packets"] == 51
        assert "session_sha256" in data

        # Import review file
        sample_reviews = Path(tmpdir) / "reviews_to_import.jsonl"
        with open(sample_reviews, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "review_id": "REV_001",
                "reviewer_id": "HUMAN_ARCHAEOLOGIST_01",
                "candidate_id": "TCAND_0106",
                "packet_id": "REV_PKT_V2_001",
                "verdict": "CLEAR_TREASURE",
                "confidence": 0.95,
                "notes": "Verified authentic."
            }) + "\n")

        imported, summary = import_human_reviews(sample_reviews, known_candidates={"TCAND_0106"})
        assert summary.valid_reviews_imported == 1
        assert summary.promoted_treasures_count == 1
        assert summary.disputes_flagged == 0
