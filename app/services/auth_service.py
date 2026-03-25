from fastapi import HTTPException
from app.core.supabase_client import supabase


def signup_user(email: str, password: str):
    try:
        response = supabase.auth.sign_up(
            {"email": email, "password": password})
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def login_user(email: str, password: str):
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password})
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def check_email_exists(email: str) -> bool:
    try:
        response = (
            supabase.table("users_emails")
            .select("email")
            .eq("email", email)
            .limit(1)
            .execute()
        )
        return len(response.data) > 0
    except Exception:
        raise HTTPException(status_code=400, detail="Erro ao verificar email")
