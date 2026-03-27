from fastapi import HTTPException
from app.core.supabase_client import supabase

# --- Fluxo de Cadastro e Verificação ---


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


def verify_signup_code(email: str, token: str):
    try:
        # O tipo 'email' é usado para confirmação de cadastro (Signup OTP)
        return supabase.auth.verify_otp({
            "email": email,
            "token": token,
            "type": "email"
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Fluxo de Login e Checagem ---


def login_user(email: str, password: str):
    try:
        return supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
    except Exception as e:
        raise HTTPException(
            status_code=401, detail="E-mail ou senha incorretos.")


def check_email_exists(email: str) -> bool:
    try:
        response = (
            supabase.table("users")
            .select("email")
            .eq("email", email)
            .limit(1)
            .execute()
        )
        return len(response.data) > 0
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Recuperação de Senha e Logout ---


def send_recovery_email(email: str):
    try:
        return supabase.auth.reset_password_for_email(email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def reset_password_with_otp(email: str, token: str, new_password: str):
    try:
        verify_res = supabase.auth.verify_otp({
            "email": email,
            "token": token,
            "type": "recovery"
        })

        if verify_res.session:
            return supabase.auth.update_user({
                "password": new_password
            })

        raise HTTPException(
            status_code=400, detail="Token de recuperação inválido.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def logout():
    try:
        return supabase.auth.sign_out()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Erro ao deslogar.")
