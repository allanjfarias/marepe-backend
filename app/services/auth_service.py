from fastapi import HTTPException
from app.core.supabase_client import supabase


def signup_user(data: dict):
    try:
        auth_response = supabase.auth.sign_up({
            "email": data["email"],
            "password": data["password"],
            "options": {
                "data": {
                    "nome": data["nome"],
                    "role": data["role"]
                }
            }
        })

        if data["role"] == "CLIENTE":
            return auth_response

        user_id = auth_response.user.id

        vendedor_data = {
            "user_id": user_id,
            "cpf": data["cpf"],
            "telefone": data["telefone"]
        }

        if data["role"] == "BARRAQUEIRO":
            vendedor_data["nome_barraca"] = data["nome_barraca"]

        supabase.table("vendedores").insert(vendedor_data).execute()

        return auth_response

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


def verify_signup_code(email: str, token: str):
    try:
        response = supabase.auth.verify_otp({
            "email": email,
            "token": token,
            "type": "email"
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
