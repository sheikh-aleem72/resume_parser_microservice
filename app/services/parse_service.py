from fastapi import APIRouter, HTTPException
import requests
import tempfile
import os
from app.utils.extractors import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_email,
    extract_phone,
    extract_name
)

async def parse_resume(data: dict):
    resume_url = data.get("resumeUrl")
    print("parse resume getting called and resume url is: ",resume_url)
    if not resume_url:
        raise HTTPException(status_code=400, detail="resumeUrl is required")

    # Download file from URL
    try:
        response = requests.get(resume_url)
        print("Checkpoint - 1", response)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download file: {e}")

    print("Passing checkpoint 1")
    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name

    print("Checkpoint - 2")
    # Parse file based on extension
    try:
        if resume_url.endswith(".pdf"):
            text = extract_text_from_pdf(tmp_path)
        elif resume_url.endswith(".docx"):
            text = extract_text_from_docx(tmp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
    finally:
        os.remove(tmp_path)


    print("Checkpoint - 3")
    # Extract info
    parsed_data = {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "name": extract_name(text),
        "word_count": len(text.split()),
    }

    return parsed_data
