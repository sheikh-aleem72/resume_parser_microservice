import json

def build_prompt(resume_text: str, job_text: str, explanation: dict) -> str:
    return f"""
You are a deterministic information extraction and evaluation engine.

Your responsibilities:
1. Extract factual, structured data from the resume.
2. Evaluate candidate fit against the job description.
3. Stay strictly aligned with the provided Phase 5A evidence.

====================
NON-NEGOTIABLE RULES
====================
- Return ONLY valid JSON. No markdown. No explanations.
- Be concise and factual. Avoid verbosity.
- Do NOT repeat resume text verbatim.
- Do NOT contradict Phase 5A evidence.
- Do NOT invent skills, experience, or education.
- If information is missing or unclear, use null or empty arrays.
- Avoid repeating the same reasoning across multiple fields.

====================
RESUME TEXT
====================
<<<
{resume_text}
>>>

====================
JOB DESCRIPTION
====================
<<<
{job_text}
>>>

====================
PHASE 5A EVIDENCE (AUTHORITATIVE)
DO NOT CONTRADICT THIS
====================
<<<
{json.dumps(explanation)}
>>>

====================
OUTPUT CONSTRAINTS
====================

parsed_resume.skills:
- Extract ONLY hard technical skills.
- Exclude soft skills, management traits, and generic competencies.
- Maximum 15 skills.

analysis lists:
- matchedSkills: max 5 items
- missingSkills: max 5 items
- strengths: max 4 items
- concerns: max 4 items
- Each item must be a short phrase or one short sentence.

Dates & experience:
- If dates appear implausible or span multiple decades, extract them as-is.
- Do NOT infer seniority or experience level solely from long durations.

Text fields:
- experienceAssessment: max 2 sentences
- summary: max 3 sentences
- recommendation: max 2 sentences

Fit evaluation:
- overallFit must be one of: "Strong", "Moderate", "Weak"
- If overallFit is "Weak", frame recommendations constructively (e.g., suggest better-suited roles).


====================
OUTPUT FORMAT (STRICT)
====================

Return a JSON object with EXACTLY this structure:

{{
  "parsed_resume": {{
    "name": string | null,
    "email": string | null,
    "phone": string | null,

    "education": [
      {{
        "institution": string | null,
        "degree": string | null,
        "fieldOfStudy": string | null,
        "startDate": string | null,
        "endDate": string | null
      }}
    ],

    "experience": [
      {{
        "company": string | null,
        "role": string | null,
        "startDate": string | null,
        "endDate": string | null,
        "description": string | null
      }}
    ],

    "skills": string[]
  }},

  "analysis": {{
    "matchedSkills": string[],        // max 5
    "missingSkills": string[],        // max 5
    "strengths": string[],            // max 4
    "concerns": string[],             // max 4
    "experienceAssessment": string,   // max 2 sentences
    "overallFit": "Strong" | "Moderate" | "Weak",
    "summary": string,                // max 3 sentences
    "recommendation": string          // max 2 sentences
  }}
}}


Return ONLY the JSON object. Nothing else.
"""

