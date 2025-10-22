from fastapi import APIRouter, UploadFile, File
from app.services.parse_service import parse_resume

router = APIRouter()

@router.post("/")
async def parse_resume_endpoint(file: UploadFile = File(...)):
    result = await parse_resume(file)
    return {"parsed_data": result}
