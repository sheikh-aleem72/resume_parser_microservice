# embeddings/text_builder.py

MAX_WORDS = 1500


def truncate_text(text: str, max_words: int = MAX_WORDS) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])


def build_embedding_texts(normalized_resume_text: str, normalized_job_text: str):
    """
    Validates and produce input text for embeddings
    """

    resume_text = truncate_text(normalized_resume_text)

    resume_embedding_text = (
        "RESUME PROFILE\n"
        "---------------\n"
        f"{resume_text}"
    )


    job_embedding_text = (
        "JOB REQUIREMENTS\n"
        "----------------\n"
        f"{normalized_job_text}"
    )

    return resume_embedding_text, job_embedding_text
