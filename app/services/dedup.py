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
    resume_processings_collection.update_one(
        {"_id": ObjectId(current_processing_id)},
        {
            "$set": {
                "status": "completed",
                "isDuplicate": True,
                "duplicateOf": source_processing_doc["_id"],
                "parsedResumeId": source_processing_doc.get("parsedResumeId"),
                "resumeAnalysisId": source_processing_doc.get("resumeAnalysisId"),
            }
        }
    )
