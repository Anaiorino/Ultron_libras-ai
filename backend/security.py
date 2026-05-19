from fastapi import Header, HTTPException
from backend.routes.auth import get_user_by_token


def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Token não informado"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

    token = authorization.replace("Bearer ", "")

    user = get_user_by_token(token)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Sessão inválida"
        )

    return user


def require_admin(current_user=Header(None)):
    user = get_current_user(current_user)

    if user["role"] != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Acesso permitido apenas para administradores"
        )

    return user