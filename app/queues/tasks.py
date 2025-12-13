import os
from app.services.file_loader import download_resume
from app.services.text_extractor import extract_raw_text
from app.utils.logger import logger
from app.utils.log_context import set_log_context
from app.services.normalize import normalize_text
from app.services.hashing import sha256_hash


def process_resume(job_payload):
    """
    Phase 3 - Step 1:
    Download resume + extract raw text
    """
    file_path = None
    set_log_context(
        jobId=job_payload.get("jobId"),
        batchId=job_payload.get("batchId"),
        resumeId=job_payload.get("resumeId"),
    )

    logger.info("Starting resume processing")

    try:
        resume_url = job_payload["resumeUrl"]

        # 1️⃣ Download
        logger.info("Downloading resume")
        file_path, mime = download_resume(resume_url)

        # 2️⃣ Extract text
        logger.info("Extracting text")
        raw_text = extract_raw_text(file_path, mime)
        
        logger.info("Text extraction completed")

        if not raw_text.strip():
            raise Exception("Extracted text is empty")
        
        logger.info("Normalizing text")
        normalized_resume_text = normalize_text(raw_text)

        logger.info(
            f"Normalized resume text length={len(normalized_resume_text)}"
        )

        # ---- HASHING ----
        resume_hash = sha256_hash(normalized_resume_text)

        # Job text should already be stored in DB or payload
        job_text = job_payload.get("jobText", "")
        normalized_job_text = normalize_text(job_text)
        job_hash = sha256_hash(normalized_job_text)

        logger.info("Hashes computed successfully")        

        # Next steps:
        # normalize → hash → dedup (Phase-3 Step-2,3,4)


        return {
            "status": "textExtracted",
            "rawTextLength": len(raw_text)
        }

    except Exception as e:
        logger.exception(f"process_resume failed: {e}")
        raise

    finally:
        # 🧹 cleanup temp file
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
