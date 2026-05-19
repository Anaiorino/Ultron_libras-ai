from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import hashlib
import secrets

from backend.database import get_db
from backend.models import User
from backend.schemas import UserCreate, UserLogin, UserResponse, LoginResponse

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

active_tokens = {}


def hash_password(password: str):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, hashed_password: str):
    return hash_password(password) == hashed_password


def create_token(user: User):
    token = secrets.token_hex(32)

    active_tokens[token] = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }

    return token


def get_user_by_token(token: str):
    return active_tokens.get(token)


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="E-mail já cadastrado"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role="USER"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=LoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha inválidos"
        )

    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha inválidos"
        )

    token = create_token(db_user)

    return {
        "user": db_user,
        "access_token": token,
        "token_type": "bearer"
    }