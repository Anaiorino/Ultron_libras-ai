from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import TranslationHistory, User
from backend.schemas import TranslationCreate
from backend.security import get_current_user

router = APIRouter(
    prefix="/history",
    tags=["Translation History"]
)


@router.post("/")
def create_history(
    data: TranslationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != data.user_id and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Você não pode salvar histórico para outro usuário"
        )

    history = TranslationHistory(
        user_id=data.user_id,
        input_text=data.input_text,
        output_text=data.output_text,
        translation_type=data.translation_type,
        confidence=data.confidence
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return {
        "id": history.id,
        "user_id": history.user_id,
        "input_text": history.input_text,
        "output_text": history.output_text,
        "translation_type": history.translation_type,
        "confidence": history.confidence,
        "created_at": history.created_at
    }


@router.get("/")
def list_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = (
        db.query(TranslationHistory, User)
        .join(User, TranslationHistory.user_id == User.id)
    )

    if current_user.role != "ADMIN":
        query = query.filter(TranslationHistory.user_id == current_user.id)

    results = query.all()

    history_list = []

    for history, user in results:
        history_list.append({
            "id": history.id,
            "user_id": history.user_id,
            "user_name": user.name,
            "user_email": user.email,
            "input_text": history.input_text,
            "output_text": history.output_text,
            "translation_type": history.translation_type,
            "confidence": history.confidence,
            "created_at": history.created_at
        })

    return history_list


@router.delete("/{history_id}")
def delete_history(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = db.query(TranslationHistory).filter(
        TranslationHistory.id == history_id
    ).first()

    if not history:
        raise HTTPException(
            status_code=404,
            detail="Histórico não encontrado"
        )

    if current_user.role != "ADMIN" and history.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Você não pode apagar este histórico"
        )

    db.delete(history)
    db.commit()

    return {"message": "Histórico deletado com sucesso"}