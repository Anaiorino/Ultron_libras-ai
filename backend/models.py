from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from backend.database import Base


class Sign(Base):
    __tablename__ = "signs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    video_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)


class TranslationHistory(Base):
    __tablename__ = "translation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    input_text = Column(String, nullable=False)
    output_text = Column(String, nullable=False)
    translation_type = Column(String, nullable=False)
    confidence = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)