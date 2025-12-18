from pdfminer.high_level import extract_text
from docx import Document

def extract_text_from_pdf(file_path: str) -> str:
    return extract_text(file_path)

def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_raw_text(file_path: str, mime_type: str) -> str:
    """
    Extracts raw text using only PDF/DOCX extractors.
    No parsing, no section handling — Phase 3 ONLY needs plain text.
    """
    if mime_type == "application/pdf":
        return extract_text_from_pdf(file_path)

    if mime_type in [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ]:
        return extract_text_from_docx(file_path)

    raise ValueError(f"Unsupported resume format: {mime_type}")
