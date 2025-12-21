from bson import ObjectId
from app.utils.mongo import resume_processings_collection
from app.embeddings.scoring import compute_final_score
from app.embeddings.skill_match import compute_skill_match_ratio


def rank_resumes_in_batch(
    batch_id: str,
    job_description_id: str,
    required_skills: list[str],
    preferred_skills: list[str],
):
    """
    Phase 4.4 — Rank all PASSED resumes in a batch
    """

    cursor = resume_processings_collection.find(
        {
            "batchId": batch_id,
            "jobDescriptionId": ObjectId(job_description_id),
            "preFilter.passed": True,
        }
    )

    resumes = list(cursor)

    if not resumes:
        return

    scored = []

    for doc in resumes:
        semantic = doc["preFilter"]["similarityScore"]

        required_ratio = compute_skill_match_ratio(
            doc.get("normalizedResumeText", ""),
            required_skills
        )

        preferred_ratio = compute_skill_match_ratio(
            doc.get("normalizedResumeText", ""),
            preferred_skills
        )

        final_score = compute_final_score(
            semantic_similarity=semantic,
            required_skill_match_ratio=required_ratio,
            preferred_skill_match_ratio=preferred_ratio,
        )

        scored.append((doc["_id"], final_score))

    # Sort by score DESC
    scored.sort(key=lambda x: x[1], reverse=True)

    # Assign ranks
    for rank, (resume_id, score) in enumerate(scored, start=1):
        resume_processings_collection.update_one(
            {"_id": resume_id},
            {
                "$set": {
                    "finalScore": score,
                    "rank": rank,
                    "rankingStatus": "completed",
                }
            }
        )
