"""
Explanation Sanity Validator Subsystem for Project Atlas.
Enforces strict anti-exaggeration and evidence-linkage rules on all generated narratives.
Blocks unproven superlative claims ("the oldest", "nobody knows", "completely unchanged").
"""

from typing import List, Tuple

FORBIDDEN_SUPERLATIVES = [
    "the oldest",
    "the last",
    "nobody knows",
    "the only surviving",
    "the world's first",
    "never discovered",
    "completely unchanged",
    "guaranteed ancient",
    "definitive proof"
]

def validate_explanation(explanation_text: str) -> Tuple[bool, List[str]]:
    """
    Validate that an explanation adheres to scientific modesty and lacks unproven superlatives.
    Returns (is_valid, list_of_violations).
    """
    violations: List[str] = []
    text_lower = explanation_text.lower()

    for superlative in FORBIDDEN_SUPERLATIVES:
        if superlative in text_lower:
            violations.append(f"Forbidden superlative or unproven claim detected: '{superlative}'")

    return len(violations) == 0, violations
