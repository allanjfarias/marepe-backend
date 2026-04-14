from fastapi import HTTPException
from app.core.supabase_client import supabase
from app.schemas.auth import AuthError, DatabaseError, UploadError
from app.core.logger import logger


async def signup_user(data: dict, foto=None):

    # 1. cria usuário no Supabase Auth
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

    user = auth_response.user

    if not user:
        raise AuthError("Falha ao criar usuário")

    user_id = user.id

    # 2. upload da foto
    foto_url = None

    if foto:
        try:
            file_ext = foto.filename.split(".")[-1]
            file_path = f"{user_id}/profile.{file_ext}"

            file_bytes = await foto.read()

            upload_res = supabase.storage.from_("perfil").upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": foto.content_type},)

            if not upload_res:
                raise UploadError("Falha no upload da imagem")

            foto_url = supabase.storage.from_(
                "perfil").get_public_url(file_path)

        except Exception as e:
            raise UploadError(f"Erro ao enviar imagem: {str(e)}")

    # 3. se cliente, não grava na tabela vendedores
    if data["role"] == "CLIENTE":
        return {
            "user_id": user_id,
            "nome": data["nome"],
            "email": data["email"],
            "role": data["role"],
            "foto_url": foto_url
        }

    # 4. monta vendedor
    try:
        vendedor_data = {
            "user_id": user_id,
            "cpf": data["cpf"],
            "telefone": data["telefone"],
            "foto_url": foto_url
        }

        if data["role"] == "BARRAQUEIRO":
            vendedor_data["nome_barraca"] = data["nome_barraca"]

        supabase.table("vendedores").insert(vendedor_data).execute()

    except Exception as e:
        raise DatabaseError(f"Erro ao salvar vendedor: {str(e)}")

    # 5. response final
    return {
        "user_id": user_id,
        "nome": data["nome"],
        "email": data["email"],
        "role": data["role"],
        "cpf": data["cpf"],
        "telefone": data["telefone"],
        "nome_barraca": data.get("nome_barraca"),
        "foto_url": foto_url
    }


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
        logger.info(f"[check_email_exists] email recebido: {email}")

        response = (
            supabase.table("users")
            .select("id")
            .eq("email", email)
            .limit(1)
            .execute()
        )

        data = response.data if response else None

        logger.info(f"[check_email_exists] response.data: {data}")

        exists = bool(data)

        logger.info(f"[check_email_exists] exists: {exists}")

        return exists

    except Exception as e:
        logger.error(f"[check_email_exists] ERROR: {str(e)}")
        return False


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
        raise HTTPException(
            status_code=400, detail="Não foi possível sair da conta no momento. Tente novamente.")


def resend_signup_email(email: str):
    try:
        return supabase.auth.resend({
            "type": "signup",
            "email": email
        })
    except Exception:
        raise AuthError("Erro ao reenviar email")
