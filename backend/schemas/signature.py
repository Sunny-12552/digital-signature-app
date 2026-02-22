from pydantic import BaseModel
from typing import Optional


# 🔹 Used when creating a signature
class SignatureCreate(BaseModel):
    document_id: int
    x: int
    y: int
    page: int
    signature_text: str 


# 🔹 Used when returning signature data
class SignatureResponse(BaseModel):
    id: int
    document_id: int
    user_id: int
    x: int
    y: int
    page: int
    signature_text: Optional[str] = None
    status: str

    class Config:
        from_attributes = True  # Required for SQLAlchemy ORM compatibility