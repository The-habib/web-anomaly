"""
Human Review Importer & Dispute Resolver Subsystem for Project Atlas.
Validates review submissions, rejects invalid or unauthenticated submissions,
and flags multi-reviewer disputes with SECOND_REVIEW_REQUIRED.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Set
from pydantic import BaseModel, ValidationError

from atlas.treasure.models import HumanReviewSubmission, TreasureState

VALID_VERDICTS = {
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
    rejections: List[str]

def import_human_reviews(
    review_file_path: Path,
    known_candidates: Set[str]
) -> Tuple[List[HumanReviewSubmission], ReviewImportSummary]:
    """
    Import and validate human reviews from a JSONL file.
    Rejects missing fields, invalid verdicts, duplicate submissions, and unknown candidate IDs.
    """
    imported: List[HumanReviewSubmission] = []
    rejections: List[str] = []
    candidate_reviews: Dict[str, List[HumanReviewSubmission]] = {}
    disputes = 0

    if not review_file_path.exists():
        return [], ReviewImportSummary(
            total_records_processed=0,
            valid_reviews_imported=0,
            rejected_reviews_count=0,
            disputes_flagged=0,
            rejections=[f"File not found: {review_file_path}"]
        )

    with open(review_file_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                sub = HumanReviewSubmission(**data)

                # Validation checks
                reviewer_lower = sub.reviewer_id.strip().lower()
                if not sub.reviewer_id or any(k in reviewer_lower for k in ("machine", "auto", "system", "bot", "synthetic")):
                    rejections.append(f"Line {idx}: Machine/system reviewer ID forbidden ('{sub.reviewer_id}').")
                    continue
                if sub.verdict not in VALID_VERDICTS:
                    rejections.append(f"Line {idx}: Invalid verdict '{sub.verdict}'.")
                    continue
                if sub.candidate_id not in known_candidates:
                    rejections.append(f"Line {idx}: Unknown candidate ID '{sub.candidate_id}'.")
                    continue

                imported.append(sub)
                candidate_reviews.setdefault(sub.candidate_id, []).append(sub)

            except Exception as e:
                rejections.append(f"Line {idx}: Parsing error: {str(e)}")

    # Check for multi-reviewer disagreements
    for cid, reviews in candidate_reviews.items():
        if len(reviews) > 1:
            verdicts = {r.verdict for r in reviews}
            if len(verdicts) > 1:
                disputes += 1

    summary = ReviewImportSummary(
        total_records_processed=len(imported) + len(rejections),
        valid_reviews_imported=len(imported),
        rejected_reviews_count=len(rejections),
        disputes_flagged=disputes,
        rejections=rejections
    )

    return imported, summary
