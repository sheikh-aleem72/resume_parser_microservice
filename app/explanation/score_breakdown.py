from typing import Dict
from app.embeddings.scoring import compute_final_score


SCORING_WEIGHTS = {
    "similarity": 0.60,
    "requiredSkills": 0.20,
    "preferredSkills": 0.05,
    "experience": 0.15,
}


def build_score_breakdown(
    semantic_similarity: float,
    required_skill_ratio: float,
    preferred_skill_ratio: float,
    experience_ratio: float,
) -> Dict:
    """
    Phase 5A.3 — Explain how finalScore was formed.
    Uses ONLY signals that actually affected ranking.
    """

    return {
        "components": {
            "similarity": {
                "score": round(semantic_similarity, 4),
                "weight": SCORING_WEIGHTS["similarity"],
            },
            "requiredSkills": {
                "ratio": round(required_skill_ratio, 4),
                "weight": SCORING_WEIGHTS["requiredSkills"],
            },
            "preferredSkills": {
                "ratio": round(preferred_skill_ratio, 4),
                "weight": SCORING_WEIGHTS["preferredSkills"],
            },
            "experience": {
                "ratio": round(experience_ratio, 4),
                "weight": SCORING_WEIGHTS["experience"],
            },
        },
    }
