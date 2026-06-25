from fastapi import FastAPI, Depends

from backend.database import Base, engine
from backend.routes.signs import router as signs_router
from backend.routes.auth import router as auth_router
from backend.routes.history import router as history_router
from backend.routes.health import router as health_router
from backend.security import get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Jarvis Libras API",
    version="1.0.0",
    description="API do projeto Jarvis Libras com autenticação JWT, sinais e histórico."
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(signs_router)
app.include_router(history_router)


@app.get("/metrics", tags=["Metrics"])
def metrics(current_user=Depends(get_current_user)):
    return {
        "message": "Métricas protegidas",
        "user": current_user
    }


@app.get("/metrics")
def metrics(current_user=Depends(get_current_user)):
    if current_user["role"] != "ADMIN":
        return {
            "detail": "Acesso permitido apenas para administradores"
        }

    return get_metrics()