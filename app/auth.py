from fastapi import APIRouter, HTTPException
from .supabase_client import supabase
from pydantic import BaseModel

router = APIRouter()

class AuthRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
def signup(data: AuthRequest):
    try:
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(data: AuthRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))