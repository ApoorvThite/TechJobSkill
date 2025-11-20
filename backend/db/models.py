from sqlalchemy import Column, Integer, String, Text, DateTime
from .session import Base

class JobPosting(Base):
    __tablename__ = "job_postings"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    company = Column(String(255), index=True)
    location = Column(String(255), index=True)
    url = Column(Text)
    posted_at = Column(DateTime)

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
