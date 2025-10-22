import re
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(file_path: str) -> str:
    from pdfminer.high_level import extract_text
    return extract_text(file_path)

def extract_text_from_docx(file_path: str) -> str:
    from docx import Document
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_email(text: str) -> str | None:
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else None

def extract_phone(text: str) -> str | None:
    match = re.search(r'(\+?\d[\d -]{8,}\d)', text)
    return match.group(0) if match else None

def extract_name(text: str) -> str | None:
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None
