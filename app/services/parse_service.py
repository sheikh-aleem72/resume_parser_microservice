from fastapi import HTTPException
import requests
import tempfile
import os

from app.utils.extractors import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_email,
    extract_phone,
    extract_name,
    extract_education,
    extract_experience,
    extract_skills,
    parse_resume_text,  # your existing rule-based parser (optional)
)
from app.ai.llm_parser import parse_resume_with_gemini  # ✅ New AI integration


async def parse_resume(data: dict):
    """
    Main resume parsing function.
    1️⃣ Downloads file from Cloudinary URL
    2️⃣ Extracts text using pdfminer/docx
    3️⃣ Sends text to Gemini API for intelligent parsing
    4️⃣ Falls back to rule-based extraction if Gemini fails
    """
    resume_url = data.get("resumeUrl")
    if not resume_url:
        raise HTTPException(status_code=400, detail="resumeUrl is required")

    # -------------------------------
    # 📥 1. Download the resume file
    # -------------------------------
    try:
        response = requests.get(resume_url, stream=True)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download file: {e}")

    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name

    try:
        # -------------------------------
        # 📄 2. Extract text from file
        # -------------------------------
        if resume_url.endswith(".pdf"):
            text = extract_text_from_pdf(tmp_path)
        elif resume_url.endswith(".docx"):
            text = extract_text_from_docx(tmp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        if not text.strip():
            raise HTTPException(status_code=400, detail="Failed to extract text from file")

        # -------------------------------
        # 🤖 3. Try Gemini AI parsing
        # -------------------------------
        ai_result = parse_resume_with_gemini(text)

        if ai_result.get("success"):
            parsed_data = ai_result["data"]
        else:
            # Log fallback reason
            print(f"[Gemini Fallback] Reason: {ai_result.get('error')}")
            parsed_data = parse_resume_text(text)

        # -------------------------------
        # 🧩 4. Fill missing basic fields (safety net)
        # -------------------------------
        parsed_data.setdefault("name", extract_name(text))
        parsed_data.setdefault("email", extract_email(text))
        parsed_data.setdefault("phone", extract_phone(text))

        # If Gemini didn’t detect these, use rule-based ones
        if not parsed_data.get("education"):
            parsed_data["education"] = extract_education(text)

        if not parsed_data.get("experience"):
            parsed_data["experience"] = extract_experience(text)

        if not parsed_data.get("skills"):
            parsed_data["skills"] = extract_skills(text)

        parsed_data["word_count"] = len(text.split())

        return parsed_data

    finally:
        # -------------------------------
        # 🧹 5. Cleanup temp file
        # -------------------------------
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
