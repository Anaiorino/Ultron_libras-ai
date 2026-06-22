from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import hashlib
import os
from jose import jwt
from datetime import datetime, timedelta

from dotenv import load_dotenv

from backend.database import get_db
from backend.models import User
from backend.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    LoginResponse
)

# ==========================================
# ENV
# ==========================================

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
TOKEN_EXPIRE_MINUTES = int(
    os.getenv("TOKEN_EXPIRE_MINUTES", 60)
)

ADMIN_EMAIL = os.getenv(
    "ADMIN_EMAIL",
    "admin@jarvis.com"
)

# ==========================================
# ROUTER
# ==========================================

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# ==========================================
# PASSWORD
# ==========================================

def hash_password(password: str):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def verify_password(
    password: str,
    hashed_password: str
):
    return (
        hash_password(password)
        == hashed_password
    )


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# ==========================================
# REGISTER
# ==========================================

@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="E-mail já cadastrado"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role="ADMIN"
        if user.email.lower() == ADMIN_EMAIL.lower()
        else "USER"
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user

# ==========================================
# LOGIN
# ==========================================

@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    db_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha inválidos"
        )

    if not verify_password(
        user.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha inválidos"
        )

    token = create_access_token(
    {
        "sub": db_user.email,
        "id": db_user.id,
        "name": db_user.name,
        "role": db_user.role
    }
)

    return {
        "user": db_user,
        "access_token": token,
        "token_type": "bearer"
    }