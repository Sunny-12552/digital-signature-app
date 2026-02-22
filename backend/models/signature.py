from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from database import Base


class Signature(Base):
    __tablename__ = "signatures"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    x = Column(Integer)
    y = Column(Integer)
    page = Column(Integer)

    signature_text = Column(Text, nullable=True)
    status = Column(String, default="pending")

    document = relationship("Document")
    user = relationship("User")
    # signature_text = Column(String, nullable=True)