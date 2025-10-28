import re
import spacy

nlp = spacy.load("en_core_web_sm")

# ---------------------------
# 1️⃣ BASIC FILE EXTRACTORS
# ---------------------------
def extract_text_from_pdf(file_path: str) -> str:
    from pdfminer.high_level import extract_text
    return extract_text(file_path)

def extract_text_from_docx(file_path: str) -> str:
    from docx import Document
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


# ---------------------------
# 2️⃣ SECTION SPLITTER
# ---------------------------
def split_into_sections(text: str) -> dict[str, str]:
    """
    Split the resume text into sections based on keywords like Education, Experience, Skills, etc.
    """
    section_headers = [
        "education", "experience", "work experience", "work history",
        "skills", "projects", "certifications", "summary", "achievements"
    ]
    sections = {}
    current_section = "general"
    sections[current_section] = []

    for line in text.splitlines():
        header_match = next((h for h in section_headers if re.search(rf"\b{h}\b", line, re.IGNORECASE)), None)
        if header_match:
            current_section = header_match.lower()
            sections[current_section] = []
        else:
            sections[current_section].append(line.strip())

    return {k: "\n".join(v).strip() for k, v in sections.items()}


# ---------------------------
# 3️⃣ BASIC FIELD EXTRACTORS
# ---------------------------
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


# ---------------------------
# 4️⃣ EDUCATION, EXPERIENCE, SKILLS
# ---------------------------
def extract_education(section_text: str) -> list[str]:
    """
    Extract education lines from Education section or general text.
    """
    edu_keywords = [
        "bachelor", "master", "phd", "mba", "bsc", "msc", "university",
        "college", "degree", "diploma", "school"
    ]
    lines = section_text.split("\n")
    filtered = [line for line in lines if any(k in line.lower() for k in edu_keywords)]
    return list(set(filtered))[:5]  # limit to 5 entries


def extract_experience(section_text: str) -> list[str]:
    """
    Extract professional experience lines from Experience section.
    """
    exp_keywords = [
        "developer", "engineer", "manager", "intern", "analyst",
        "designer", "consultant", "project", "experience"
    ]
    lines = section_text.split("\n")
    filtered = [line for line in lines if any(k in line.lower() for k in exp_keywords)]
    return list(set(filtered))[:5]


SKILL_KEYWORDS = [
    # Technical
    "python", "javascript", "react", "node", "express", "mongodb", "sql", "aws", "docker", "java", "c++", "html", "css",
    # Soft
    "leadership", "communication", "problem solving", "teamwork", "management",
    "creativity", "adaptability", "organization", "critical thinking"
]

def extract_skills(section_text: str) -> list[str]:
    """
    Extract technical and soft skills.
    """
    found = []
    for skill in SKILL_KEYWORDS:
        if re.search(rf"\b{skill}\b", section_text, re.IGNORECASE):
            found.append(skill.capitalize())
    return list(set(found))


# ---------------------------
# 5️⃣ MAIN PARSING FUNCTION
# ---------------------------
def parse_resume_text(text: str) -> dict:
    """
    Main function to extract all details from resume text.
    """
    sections = split_into_sections(text)

    # Extract from whole text
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)

    # Section-aware extraction
    education = extract_education(sections.get("education", ""))
    experience = extract_experience(sections.get("experience", sections.get("work experience", "")))
    skills = extract_skills(sections.get("skills", text))  # fallback to whole text

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "education": education,
        "experience": experience,
        "skills": skills
    }
