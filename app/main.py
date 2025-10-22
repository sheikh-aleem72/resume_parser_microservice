from fastapi import FastAPI
from app.routes.parse_routes import router as parse_router

app = FastAPI(title="AI Resume Parser Service")

app.include_router(parse_router, prefix="/api/parse", tags=["Resume Parsing"])

@app.get("/")
def root():
    return {"message": "Resume Parser is running 🚀"}
