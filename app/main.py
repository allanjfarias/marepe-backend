from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router
from app.routers.vendedor import router as vendedor_router

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
    app.include_router(vendedor_router, prefix="/vendedor")

    return app



app = create_app()
