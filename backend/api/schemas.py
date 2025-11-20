from pydantic import BaseModel

class SkillTrend(BaseModel):
    skill: str
    count: int
    pct_change_4w: float
