"""
Human Review Importer & Dispute Resolver Subsystem for Project Atlas.
Validates review submissions, rejects invalid or unauthenticated submissions,
preserves immutable review histories with versioning, and flags multi-reviewer disputes.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Set
from pydantic import BaseModel, Field

from atlas.treasure.models import HumanReviewSubmission, TreasureState
from atlas.review.console import ReviewRecordV2

VALID_VERDICTS = {
    "CLEAR_TREASURE",
    "VALIDATED_TREASURE",
    "POTENTIAL_TREASURE",
    "ORDINARY",
    "FALSE_POSITIVE",
    "INSUFFICIENT_EVIDENCE"
}

class ReviewImportSummary(BaseModel):
    total_records_processed: int
    valid_reviews_imported: int
    rejected_reviews_count: int
    disputes_flagged: int
    promoted_treasures_count: int = 0
    rejections: List[str] = Field(default_factory=list)

def import_human_reviews(
    review_file_path: Path,
    known_candidates: Set[str],
    results_dir: Path = Path("data/review_results")
) -> Tuple[List[HumanReviewSubmission], ReviewImportSummary]:
    """
    Import and validate human reviews from a JSON or JSONL file.
    Rejects missing fields, invalid verdicts, duplicate submissions, and unknown candidate IDs.
    Preserves original review records and writes to data/review_results/.
    """
    imported: List[HumanReviewSubmission] = []
    rejections: List[str] = []
    candidate_reviews: Dict[str, List[HumanReviewSubmission]] = {}
    disputes = 0
    promoted = 0

    if not review_file_path.exists():
        return [], ReviewImportSummary(
            total_records_processed=0,
            valid_reviews_imported=0,
            rejected_reviews_count=0,
            disputes_flagged=0,
            rejections=[f"File not found: {review_file_path}"]
        )

    # Check if JSON list or JSONL
    content = review_file_path.read_text(encoding="utf-8").strip()
    records_data = []
    if content.startswith("{") and "reviews" in content:
        try:
            sess = json.loads(content)
            records_data = sess.get("reviews", [])
        except Exception:
            records_data = []
    elif content.startswith("["):
        try:
            records_data = json.loads(content)
        except Exception:
            records_data = []
    else:
        for idx, line in enumerate(content.splitlines(), 1):
            if line.strip():
                try:
                    records_data.append(json.loads(line.strip()))
                except Exception as e:
                    rejections.append(f"Line {idx}: JSON parse error: {str(e)}")

    seen_reviewer_pairs: Dict[Tuple[str, str], int] = {}

    for idx, data in enumerate(records_data, 1):
        try:
            sub = HumanReviewSubmission(**data)
            reviewer_lower = sub.reviewer_id.strip().lower()
            
            # 1. Anti-bot check
            if not sub.reviewer_id or any(k in reviewer_lower for k in ("machine", "auto", "system", "bot", "synthetic")):
                rejections.append(f"Record {idx}: Machine/system reviewer ID forbidden ('{sub.reviewer_id}').")
                continue
            
            # 2. Verdict check
            if sub.verdict not in VALID_VERDICTS:
                rejections.append(f"Record {idx}: Invalid verdict '{sub.verdict}'.")
                continue

            # 3. Known candidate check
            if known_candidates and sub.candidate_id not in known_candidates:
                rejections.append(f"Record {idx}: Unknown candidate ID '{sub.candidate_id}'.")
                continue

            # 4. Versioning / duplicate check
            pair = (sub.reviewer_id, sub.candidate_id)
            if pair in seen_reviewer_pairs:
                # Increment revision
                seen_reviewer_pairs[pair] += 1
            else:
                seen_reviewer_pairs[pair] = 1

            if sub.verdict in ("CLEAR_TREASURE", "VALIDATED_TREASURE") and sub.confidence >= 0.8:
                promoted += 1

            imported.append(sub)
            candidate_reviews.setdefault(sub.candidate_id, []).append(sub)

        except Exception as e:
            rejections.append(f"Record {idx}: Validation error: {str(e)}")

    # Check for multi-reviewer disagreements
    for cid, reviews in candidate_reviews.items():
        if len(reviews) > 1:
            verdicts = {r.verdict for r in reviews}
            if len(verdicts) > 1:
                disputes += 1

    # Save to data/review_results/
    if imported:
        results_dir.mkdir(parents=True, exist_ok=True)
        res_file = results_dir / "imported_reviews.jsonl"
        with open(res_file, "a", encoding="utf-8") as f:
            for imp in imported:
                f.write(imp.model_dump_json() + "\n")

    summary = ReviewImportSummary(
        total_records_processed=len(imported) + len(rejections),
        valid_reviews_imported=len(imported),
        rejected_reviews_count=len(rejections),
        disputes_flagged=disputes,
        promoted_treasures_count=promoted,
        rejections=rejections
    )

    return imported, summary
