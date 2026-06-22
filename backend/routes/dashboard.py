from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from backend.database import get_db
from backend.models import User, TranslationHistory
from backend.security import require_admin

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    total_users = db.query(User).count()

    total_translations = db.query(TranslationHistory).count()

    today = date.today()

    translations_today = db.query(TranslationHistory).filter(
        func.date(TranslationHistory.created_at) == today
    ).count()

    last_translation = db.query(TranslationHistory).order_by(
        TranslationHistory.created_at.desc()
    ).first()

    translations_by_type_query = db.query(
        TranslationHistory.translation_type,
        func.count(TranslationHistory.id)
    ).group_by(
        TranslationHistory.translation_type
    ).all()

    translations_by_type = [
        {
            "type": item[0],
            "total": item[1]
        }
        for item in translations_by_type_query
    ]

    translations_by_day_query = db.query(
        func.date(TranslationHistory.created_at),
        func.count(TranslationHistory.id)
    ).group_by(
        func.date(TranslationHistory.created_at)
    ).order_by(
        func.date(TranslationHistory.created_at)
    ).all()

    translations_by_day = [
        {
            "date": str(item[0]),
            "total": item[1]
        }
        for item in translations_by_day_query
    ]

    return {
        "total_users": total_users,
        "total_translations": total_translations,
        "translations_today": translations_today,
        "last_translation": (
            last_translation.created_at.strftime("%d/%m/%Y %H:%M")
            if last_translation else "Nenhuma"
        ),
        "translations_by_type": translations_by_type,
        "translations_by_day": translations_by_day
    }