import re
from typing import Optional


EXPERIENCE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:\+?\s*)?(?:years?|yrs?)",
    re.IGNORECASE
)


def extract_experience_years(normalized_resume_text: str) -> float:
    """
    Deterministic experience extractor.
    Returns max years found or 0.0
    """
    matches = EXPERIENCE_PATTERN.findall(normalized_resume_text)

    if not matches:
        return 0.0

    return max(float(m) for m in matches)


def compute_experience_match_ratio(
    extracted_years: float,
    required_years: Optional[float],
) -> float:
    """
    Returns value in [0, 1]
    """
    if not required_years or required_years <= 0:
        return 1.0  # neutral

    return min(extracted_years / required_years, 1.0)
