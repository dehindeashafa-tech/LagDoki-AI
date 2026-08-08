import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Force Python to include the directory containing main.py in its search path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Import triage module
try:
    from routers import triage
except ModuleNotFoundError:
    import routers.triage as triage

app = FastAPI(
    title="LagDoki-AI",
    description="Multilingual Clinical Safety & Voice Triage Engine",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(triage.router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "LagDoki-AI Engine"}