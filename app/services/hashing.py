import hashlib

def sha256_hash(text: str) -> str:
    """
    Compute SHA-256 hash of normalized text.
    """
    if not text:
        return ""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()
