def validate_analysis_output(data: dict):
    if "parsed_resume" not in data or "analysis" not in data:
        raise ValueError("Invalid analysis structure")

    required_analysis_keys = [
        "matchedSkills",
        "missingSkills",
        "strengths",
        "concerns",
        "experienceAssessment",
        "overallFit",
        "summary",
        "recommendation",
    ]

    for key in required_analysis_keys:
        if key not in data["analysis"]:
            raise ValueError(f"Missing analysis field: {key}")

    if data["analysis"]["overallFit"] not in ["Strong", "Moderate", "Weak"]:
        raise ValueError("Invalid overallFit value")
