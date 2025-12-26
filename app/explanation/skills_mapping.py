from typing import List, Dict
import re


def normalize_skill(skill: str) -> str:
    return re.sub(r"[^a-z0-9+.#]", "", skill.lower().strip())


def build_skill_explanation(
    required_skills: List[str],
    preferred_skills: List[str],
    normalized_resume_text: str,
) -> Dict:
    matched_required = []
    missing_required = []

    for skill in required_skills:
        if normalize_skill(skill) in normalized_resume_text:
            matched_required.append(skill)
        else:
            missing_required.append(skill)

    matched_preferred = [
        skill
        for skill in preferred_skills
        if normalize_skill(skill) in normalized_resume_text
    ]

    return {
        "required": required_skills,
        "matched": matched_required,
        "missing": missing_required,
        "optionalMatched": matched_preferred,
    }
