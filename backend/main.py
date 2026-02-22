import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Database
from database import Base, engine

# Routers (IMPORTANT: folder name is routers, not routes)
from routers.auth import router as auth_router
from routers.documents import router as documents_router
from routers.signatures import router as signatures_router
from routers.audit import router as audit_router



app = FastAPI(title="Digital Signature API")

# Create DB tables
Base.metadata.create_all(bind=engine)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173"],
    #   # React frontend
    allow_origins=["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uploads folder setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount uploads folder
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(auth_router)

app.include_router(signatures_router)
app.include_router(audit_router)
app.include_router(documents_router)


@app.get("/")
def root():
    return {"status": "Digital Signature API running 🚀"}