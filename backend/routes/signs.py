from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Sign
from backend.schemas import SignCreate, SignUpdate, SignResponse

router = APIRouter(
    prefix="/signs",
    tags=["Signs"]
)


@router.post("/", response_model=SignResponse)
def create_sign(sign: SignCreate, db: Session = Depends(get_db)):
    new_sign = Sign(
        name=sign.name,
        description=sign.description,
        video_path=sign.video_path
    )

    db.add(new_sign)
    db.commit()
    db.refresh(new_sign)

    return new_sign


@router.get("/", response_model=list[SignResponse])
def list_signs(db: Session = Depends(get_db)):
    return db.query(Sign).all()


@router.get("/{sign_id}", response_model=SignResponse)
def get_sign(sign_id: int, db: Session = Depends(get_db)):
    sign = db.query(Sign).filter(Sign.id == sign_id).first()

    if not sign:
        raise HTTPException(
            status_code=404,
            detail="Sinal não encontrado"
        )

    return sign


@router.put("/{sign_id}", response_model=SignResponse)
def update_sign(
    sign_id: int,
    sign_data: SignUpdate,
    db: Session = Depends(get_db)
):
    sign = db.query(Sign).filter(Sign.id == sign_id).first()

    if not sign:
        raise HTTPException(
            status_code=404,
            detail="Sinal não encontrado"
        )

    if sign_data.name is not None:
        sign.name = sign_data.name

    if sign_data.description is not None:
        sign.description = sign_data.description

    if sign_data.video_path is not None:
        sign.video_path = sign_data.video_path

    db.commit()
    db.refresh(sign)

    return sign


@router.delete("/{sign_id}")
def delete_sign(sign_id: int, db: Session = Depends(get_db)):
    sign = db.query(Sign).filter(Sign.id == sign_id).first()

    if not sign:
        raise HTTPException(
            status_code=404,
            detail="Sinal não encontrado"
        )

    db.delete(sign)
    db.commit()

    return {
        "message": "Sinal deletado com sucesso"
    }