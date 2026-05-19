from fastapi import FastAPI, Depends

from backend.database import Base, engine
from backend.routes.signs import router as signs_router
from backend.routes.auth import router as auth_router
from backend.middlewares.logging_middleware import logging_middleware
from backend.metrics import get_metrics
from backend.security import get_current_user

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Jarvis Libras API",
    description="API para gerenciamento dos sinais em Libras",
    version="1.0.0"
)

app.middleware("http")(logging_middleware)

app.include_router(signs_router)
app.include_router(auth_router)


@app.get("/")
def home():
    return {
        "message": "Jarvis Libras API funcionando"
    }


@app.get("/metrics")
def metrics(current_user=Depends(get_current_user)):
    if current_user["role"] != "ADMIN":
        return {
            "detail": "Acesso permitido apenas para administradores"
        }

    return get_metrics()