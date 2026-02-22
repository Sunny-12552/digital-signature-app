from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.audit import AuditLog
from utils.dependencies import get_current_user

router = APIRouter(prefix="/api/audit", tags=["Audit"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{doc_id}")
def get_audit_logs(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(AuditLog).filter(
        AuditLog.document_id == doc_id,
        AuditLog.user_id == current_user.id
    ).all()