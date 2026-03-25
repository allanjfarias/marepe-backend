from fastapi import APIRouter, HTTPException
from .supabase_client import supabase
from pydantic import BaseModel, EmailStr

router = APIRouter()


class AuthRequest(BaseModel):
    email: str
    password: str


class EmailRequest(BaseModel):
    email: EmailStr


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



@router.post("/check-email")
def check_email(request: EmailRequest):
    try:
        response = (
            supabase
            .table("users_emails")
            .select("email")
            .eq("email", request.email)
            .limit(1)
            .execute()
        )
        exists = len(response.data) > 0
        return {"email": request.email, "exists": exists}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao verificar email:")