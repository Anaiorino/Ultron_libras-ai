from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class SignCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)
    video_path: Optional[str] = Field(default=None, max_length=255)


class SignUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)
    video_path: Optional[str] = Field(default=None, max_length=255)


class SignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    video_path: Optional[str]
    created_at: datetime


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=6, max_length=100)


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    created_at: datetime


class LoginResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


class TranslationCreate(BaseModel):
    user_id: int
    input_text: str = Field(min_length=1, max_length=500)
    output_text: str = Field(min_length=1, max_length=500)
    translation_type: str = Field(min_length=2, max_length=50)
    confidence: Optional[str] = None


class TranslationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    input_text: str
    output_text: str
    translation_type: str
    confidence: Optional[str]
    created_at: datetime