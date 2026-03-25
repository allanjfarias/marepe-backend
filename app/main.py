from fastapi import FastAPI
from .auth import router as auth_router

app = FastAPI()

@app.get("/")
def root():
    return {"msg": "API funcionando"}

app.include_router(auth_router, prefix="/auth")