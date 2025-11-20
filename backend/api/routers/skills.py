from typing import List
from fastapi import APIRouter, Query
from ..schemas import SkillTrend

router = APIRouter()

@router.get("/trending", response_model=List[SkillTrend])
def trending_skills(limit: int = 10):
    return []

@router.get("/search", response_model=List[str])
def search_skills(q: str = Query(...)):
    return []
