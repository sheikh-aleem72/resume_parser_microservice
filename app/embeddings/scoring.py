def compute_final_score(
    semantic_similarity: float,
    required_skill_match_ratio: float,
    preferred_skill_match_ratio: float,
    experience_match_ratio: float,
):
    """
    Phase 4.4 + 4.5 scoring
    Deterministic & tunable
    """

    return round(
        (0.60 * semantic_similarity)
        + (0.20 * required_skill_match_ratio)
        + (0.05 * preferred_skill_match_ratio)
        + (0.15 * experience_match_ratio),
        4
    )
