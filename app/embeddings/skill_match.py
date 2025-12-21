def compute_skill_match_ratio(
    normalized_resume_text: str,
    skills: list[str]
) -> float:
    if not skills:
        return 1.0

    matched = [
        skill
        for skill in skills
        if skill.lower() in normalized_resume_text
    ]

    return len(matched) / len(skills)
