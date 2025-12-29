from typing import Dict, List


def build_decision_explanation(
    prefilter: Dict,
    skills_explanation: Dict,
    experience_info: dict,
) -> Dict:
    reasons: List[str] = []

    # 1️⃣ Start with preFilter reasons (if rejected)
    if not prefilter.get("passed", False):
        reasons.extend(prefilter.get("reasons", []))

    if experience_info and not experience_info["meetsRequirement"]:
        reasons.append(
            f"Experience below required minimum "
            f"({experience_info['candidateYears']} < {experience_info['requiredYears']} years)"
        )

    return {
        "status": "passed" if prefilter.get("passed") else "rejected",
        "reasons": reasons,
    }


