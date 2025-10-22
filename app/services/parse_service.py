from app.utils.extractors import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_email,
    extract_phone,
    extract_name
)
import os
from fastapi import UploadFile

async def parse_resume(file: UploadFile):
    contents = await file.read()
    filename = file.filename.lower()

    temp_path = f"temp_{filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)

    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(temp_path)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx(temp_path)
    else:
        return {"error": "Unsupported file format"}

    os.remove(temp_path)

    parsed_data = {
        "filename": filename,
        "email": extract_email(text),
        "phone": extract_phone(text),
        "name": extract_name(text),
        "word_count": len(text.split()),
    }

    return parsed_data
