from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router
from app.routers.vendedor import router as vendedor_router
from app.routers.cliente import router as cliente_router
from app.routers.profile import router as profile_router
from app.routers.pedido import router as pedido_router
from app.routers.barraca import router as barraca_router
from app.core.scheduler import start_scheduler

def create_app() -> FastAPI:
    app = FastAPI(title="Minha API FastAPI")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Iniciar scheduler para jobs periódicos
    start_scheduler()

    @app.get("/")
    def root():
        return {"msg": "API funcionando"}

    app.include_router(auth_router, prefix="/auth")
    app.include_router(vendedor_router, prefix="/vendedor")
    app.include_router(cliente_router, prefix="/cliente")
    app.include_router(profile_router, prefix="/profile")
    app.include_router(pedido_router, prefix="/api")
    app.include_router(barraca_router, prefix="/barraca")


    return app



app = create_app()
