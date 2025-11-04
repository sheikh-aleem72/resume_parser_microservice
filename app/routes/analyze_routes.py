from fastapi import APIRouter, HTTPException
from app.ai.analyzer import analyze_resume_with_gemini


router = APIRouter()

@router.post("/")
async def analyze_resume_match(payload: dict):
    try:
        parsed_resume = payload.get("parsed_resume")
        job_desc = payload.get("job_description")

        if not parsed_resume or not job_desc:
            raise HTTPException(status_code=400, detail="Both parsed_resume and job_description are required")

        result = analyze_resume_with_gemini(parsed_resume, job_desc)

        return {"success": True, "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
