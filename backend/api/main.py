from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import meta, skills, clusters

app = FastAPI(title="Job Skill Trends API")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meta.router, prefix="/meta", tags=["meta"])
app.include_router(skills.router, prefix="/skills", tags=["skills"])
app.include_router(clusters.router, prefix="/clusters", tags=["clusters"])

@app.get("/")
def read_root():
    return {"status": "ok"}
