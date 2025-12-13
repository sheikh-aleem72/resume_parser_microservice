import os
import json
import re
from google import genai
from dotenv import load_dotenv

# load_dotenv()
env = os.getenv("ENV", "development")
load_dotenv(f".env.{env}")

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment")

client = genai.Client(api_key=API_KEY)

# list models
models = client.models.list()   # returns model metadata

def build_resume_prompt(text: str) -> str:
    return f"""
You are a professional resume parsing AI. 
Your ONLY task is to convert the provided resume text into a strictly formatted JSON object.

### Instructions:
- Read the resume carefully.
- Identify and extract relevant information only.
- Always follow the exact JSON structure shown below — DO NOT add, remove, or rename any fields.
- Every key must be quoted.
- Every string value must be enclosed in double quotes.
- Use an empty array [] or empty string "" if data is not found.
- Do NOT include comments, markdown, or explanations — return pure JSON only.

### JSON Structure to Follow:
{{
  "name": "",
  "email": "",
  "phone": "",
  "location": "",
  "summary": "",
  "education": [
    {{
      "degree": "",
      "institution": "",
      "fieldOfStudy": "",
      "description": "",
      "startDate": "",
      "endDate": ""
    }}
  ],
  "experience": [
    {{
      "role": "",
      "company": "",
      "startDate": "",
      "endDate": "",
      "description": ""
    }}
  ],
  "skills": [],
  "projects": [
    {{
      "name": "",
      "description": "",
      "techStack": [],
      "link": ""
    }}
  ],
  "certifications": [
    {{
      "title": "",
      "issuer": "",
      "date": "",
      "description": ""
    }}
  ],
  "achievements": [
    {{
      "title": "",
      "description": ""
    }}
  ]
}}

Return only a valid JSON object that matches the structure above exactly.

### Resume Text
<<<RESUME>>>
{text}
<<<END>>>
"""


def _extract_json_from_text(raw: str) -> dict | None:
    """
    Try to pull JSON object from model text. Models sometimes wrap text, so we attempt a robust parse.
    """
    raw = raw.strip()
    # direct parse attempt
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # try to extract first {...} block
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                return None
        return None

def parse_resume_with_gemini(text: str, model_id: str = "models/gemini-2.5-flash") -> dict:
    """
    Send resume text to Gemini 2.5 model and return parsed JSON or error info.
    model_id should be the exact model name you got from list() (e.g. "models/gemini-2.5-flash").
    """
    prompt = build_resume_prompt(text)

    try:
        response = client.models.generate_content(
            model=model_id,
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            # you can add max output tokens, temperature etc. in "config" if needed
        )
        # new SDK returns content under response.candidates[0].content.parts[0].text
        raw_output = None
        if getattr(response, "candidates", None):
            # response.candidates is a list; each candidate has content.parts
            candidate = response.candidates[0]
            raw_output = "".join(p.text for p in candidate.content.parts if hasattr(p, "text"))
        else:
            # fallback to response.text if present
            raw_output = getattr(response, "text", None)

        if not raw_output:
            return {"success": False, "error": "Empty response from Gemini", "raw": None}

        parsed = _extract_json_from_text(raw_output)
        if parsed is None:
            return {"success": False, "error": "Failed to parse JSON from Gemini output", "raw": raw_output}

        return {"success": True, "source": model_id, "data": parsed}

    except Exception as e:
        return {"success": False, "error": f"Gemini call failed: {e}"}
