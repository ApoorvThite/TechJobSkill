from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/stats")
def stats():
    return {"jobs": 0, "skills": 0}
