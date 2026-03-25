from fastapi import FastAPI
from app.routers.auth import router as auth_router

def create_app() -> FastAPI:
    app = FastAPI(title="Minha API FastAPI")

    # Rota raiz
    @app.get("/")
    def root():
        return {"msg": "API funcionando"}

    # Incluindo routers
    app.include_router(auth_router, prefix="/auth", tags=["auth"])

    return app

app = create_app()