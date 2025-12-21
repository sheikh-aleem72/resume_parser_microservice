def prefilter_resume(
    similarity_score: float,
    normalized_resume_text: str,
    required_skills: list[str],
    similarity_threshold: float = 0.30,
):
    """
    Phase 4.3 — Pre-filter decision
    """

    reasons = []

    # 1️⃣ Semantic similarity check
    if similarity_score < similarity_threshold:
        reasons.append("Low semantic similarity")

    # 2️⃣ Required skills presence check (cheap string match)
    missing_skills = [
        skill
        for skill in required_skills
        if skill.lower() not in normalized_resume_text
    ]

    if required_skills and len(missing_skills) >= max(1, len(required_skills) // 2):
        reasons.append(
            f"Missing required skills: {', '.join(missing_skills)}"
        )

    passed = len(reasons) == 0

    return {
        "passed": passed,
        "similarityScore": round(similarity_score, 4),
        "reasons": reasons,
    }
