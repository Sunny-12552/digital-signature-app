
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal

from models.signature import Signature
from models.document import Document
from models.audit import AuditLog
from schemas.signature import SignatureCreate, SignatureResponse
from utils.dependencies import get_current_user

import fitz
import os
import base64
from io import BytesIO
from PIL import Image

router = APIRouter(prefix="/api/signatures", tags=["Signatures"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 CREATE PRIVATE SIGNATURE
@router.post("/", response_model=SignatureResponse)
def create_signature(
    data: SignatureCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = db.query(Document).filter(
        Document.id == data.document_id,
        Document.owner_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.status == "signed":
        raise HTTPException(status_code=400, detail="Document already signed")

    signature = Signature(
        document_id=data.document_id,
        user_id=current_user.id,
        x=data.x,
        y=data.y,
        page=data.page,
        signature_text=data.signature_text,   # ✅ FIXED
        status="pending"
    )

    db.add(signature)

    log = AuditLog(
        user_id=current_user.id,
        document_id=data.document_id,
        action="Placed signature"
    )

    db.add(log)
    db.commit()
    db.refresh(signature)

    return signature


# 🔹 GET PRIVATE SIGNATURES
@router.get("/{doc_id}")
def get_signatures(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Signature).filter(
        Signature.document_id == doc_id
    ).all()


# 🔥 FINALIZE & EMBED REAL SIGNATURES
@router.post("/finalize/{doc_id}")
def finalize_signature(
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

    if document.status == "signed":
        raise HTTPException(status_code=400, detail="Document already finalized")

    signatures = db.query(Signature).filter(
        Signature.document_id == doc_id
    ).all()

    if not signatures:
        raise HTTPException(status_code=400, detail="No signatures found")

    original_path = document.file_path
    signed_filename = f"signed_{document.filename}"
    signed_path = os.path.join("uploads", signed_filename)

    pdf = fitz.open(original_path)

    for sig in signatures:
        page = pdf[sig.page - 1]

        if sig.signature_text:

            # 🔥 DRAW MODE (base64 image)
            if sig.signature_text.startswith("data:image"):

                header, encoded = sig.signature_text.split(",", 1)
                image_bytes = base64.b64decode(encoded)

                image = Image.open(BytesIO(image_bytes))
                image_path = f"temp_signature_{sig.id}.png"
                image.save(image_path)

                rect = fitz.Rect(sig.x, sig.y, sig.x + 200, sig.y + 100)
                page.insert_image(rect, filename=image_path)

                os.remove(image_path)

            # 🔥 TYPE MODE
            else:
                page.insert_text(
                    (sig.x, sig.y),
                    sig.signature_text,
                    fontsize=20,
                    color=(0, 0, 0)
                )

        sig.status = "signed"

    document.status = "signed"

    log = AuditLog(
        user_id=current_user.id,
        document_id=doc_id,
        action="Finalized document"
    )

    db.add(log)

    pdf.save(signed_path)
    pdf.close()

    db.commit()

    return {
        "message": "Document signed successfully",
        "signed_file": f"uploads/{signed_filename}"
    }
@router.post("/finalize/{doc_id}")
def finalize_signature(
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

    if document.status == "signed":
        raise HTTPException(status_code=400, detail="Document already finalized")

    signatures = db.query(Signature).filter(
        Signature.document_id == doc_id
    ).all()

    if not signatures:
        raise HTTPException(status_code=400, detail="No signatures found")

    original_path = document.file_path
    signed_filename = f"signed_{document.filename}"
    signed_path = os.path.join("uploads", signed_filename)

    pdf = fitz.open(original_path)

    for sig in signatures:
        page = pdf[sig.page - 1]

        # 🔥 Convert base64 to image
        image_data = sig.signature_text.split(",")[1]
        image_bytes = base64.b64decode(image_data)

        rect = fitz.Rect(
            sig.x,
            sig.y,
            sig.x + 200,   # width
            sig.y + 100    # height
        )

        page.insert_image(rect, stream=image_bytes)

        sig.status = "signed"

    document.status = "signed"

    pdf.save(signed_path)
    pdf.close()

    db.commit()

    return {
        "message": "Document signed successfully",
        "signed_file": f"uploads/{signed_filename}"
    }