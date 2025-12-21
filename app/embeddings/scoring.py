def compute_final_score(
    semantic_similarity: float,
    required_skill_match_ratio: float,
    preferred_skill_match_ratio: float = 0.0,
):
    """
    Phase 4.4 scoring function
    Deterministic & tunable
    """

    return round(
        (0.70 * semantic_similarity)
        + (0.25 * required_skill_match_ratio)
        + (0.05 * preferred_skill_match_ratio),
        4
    )
