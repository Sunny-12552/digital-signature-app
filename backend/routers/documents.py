import os
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.document import Document
from utils.dependencies import get_current_user


router = APIRouter(prefix="/api/docs", tags=["Documents"])


# 🔹 DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 Correct upload directory (inside backend)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================================================
# 🔹 Upload Document
# =========================================================
@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    # Save file physically
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    # Save relative path to DB
    new_doc = Document(
        filename=file.filename,
        file_path=f"uploads/{file.filename}",
        owner_id=current_user.id,
        status="pending",
    )

    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return {
        "message": "File uploaded successfully",
        "document_id": new_doc.id
    }


# =========================================================
# 🔹 List User Documents
# =========================================================
@router.get("/")
def list_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    documents = db.query(Document).filter(
        Document.owner_id == current_user.id
    ).all()

    return documents


# =========================================================
# 🔹 Generate Public Link (24hr Expiry)
# =========================================================
@router.post("/generate-link/{doc_id}")
def generate_public_link(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = db.query(Document).filter(
        Document.id == doc_id,
        Document.owner_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    token = secrets.token_urlsafe(16)

    document.public_token = token
    document.is_public = True
    document.public_expires_at = datetime.utcnow() + timedelta(hours=24)

    db.commit()

    return {
        "public_link": f"http://localhost:5173/public/{token}",
        "expires_at": document.public_expires_at
    }


# =========================================================
# 🔹 Get Public Document (Check Expiry)
# =========================================================
@router.get("/public/{token}")
def get_public_document(
    token: str,
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.public_token == token,
        Document.is_public == True
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Invalid link")

    if (
        document.public_expires_at
        and document.public_expires_at < datetime.utcnow()
    ):
        raise HTTPException(status_code=400, detail="Public link expired")

    return document