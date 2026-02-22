from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from datetime import datetime



class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")
    public_token = Column(String, nullable=True)
    is_public = Column(Boolean, default=False)
    public_expires_at = Column(DateTime, nullable=True)


    owner = relationship("User")
