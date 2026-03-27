from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router


def create_app() -> FastAPI:
    app = FastAPI(title="Minha API FastAPI")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root():
        return {"msg": "API funcionando"}

    app.include_router(auth_router, prefix="/auth")

    return app


app = create_app()
