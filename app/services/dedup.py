from app.utils.mongo import resume_processings_collection
from bson.objectid import ObjectId


def find_duplicate(resume_hash: str, job_hash: str):
    """
    Find an already COMPLETED ResumeProcessing
    with same resumeHash + jobHash
    """
    return resume_processings_collection.find_one({
        "resumeHash": resume_hash,
        "jobHash": job_hash,
        "status": "completed"
    })


def mark_as_duplicate(
    current_processing_id,
    source_processing_doc
):
    """
    Mark current ResumeProcessing as duplicate
    and reuse cached results
    """
    copy_fields = {
        # ---- Phase 3 ----
        "parsedResume": source_processing_doc.get("parsedResume"),
        "analysis": source_processing_doc.get("analysis"),

        # ---- Phase 4.2 ----
        "resumeEmbedding": source_processing_doc.get("resumeEmbedding"),
        "jobEmbedding": source_processing_doc.get("jobEmbedding"),
        "embeddingStatus": source_processing_doc.get("embeddingStatus"),
        "embeddingModel": source_processing_doc.get("embeddingModel"),

        # ---- Phase 4.3 ----
        "preFilter": source_processing_doc.get("preFilter"),

        # ---- Phase 4.4 ----
        "finalScore": source_processing_doc.get("finalScore"),
        "rank": source_processing_doc.get("rank"),
        "rankingStatus": source_processing_doc.get("rankingStatus"),

        # ---- Hashes ----
        "resumeHash": source_processing_doc.get("resumeHash"),
        "jobHash": source_processing_doc.get("jobHash"),
    }

    resume_processings_collection.update_one(
        {"_id": ObjectId(current_processing_id)},
        {
            "$set": {
                **copy_fields,
                "status": "completed",
                "isDuplicate": True,
                "duplicateOf": source_processing_doc["_id"],
            }
        }
    )
