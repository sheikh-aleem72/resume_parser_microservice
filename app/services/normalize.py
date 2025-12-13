import re

def normalize_text(text: str) -> str:
    """
    Normalize resume/job text so hashing is deterministic.
    SAME input → SAME output → SAME hash
    """
    if not text:
        return ""

    # 1. Lowercase
    text = text.lower()

    # 2. Remove non-alphanumeric chars (keep spaces)
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # 3. Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # 4. Trim
    return text.strip()
