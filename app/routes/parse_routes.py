from fastapi import APIRouter, HTTPException, Body
from app.services.parse_service import parse_resume


router = APIRouter()

@router.post("/")
async def parse_resume_endpoint(data: dict = Body(...)):
    """
    Expects: { "resumeUrl": "<cloudinary_url>" }
    """
    try:
        result = await parse_resume(data)
        return {"parsed_data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
