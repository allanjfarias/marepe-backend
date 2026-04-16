from fastapi import HTTPException
from app.core.supabase_client import supabase
from app.schemas.auth import AuthError, DatabaseError, UploadError, AmbulanteResponse, ClienteResponse, BarraqueiroResponse
from app.core.logger import logger


def build_response(role: str, user_id: str, data: dict, foto_url: str | None):
    response_map = {
        "CLIENTE": lambda: ClienteResponse(
            user_id=user_id,
            nome=data["nome"],
            email=data["email"],
            role="CLIENTE"
        ),

        "AMBULANTE": lambda: AmbulanteResponse(
            user_id=user_id,
            nome=data["nome"],
            email=data["email"],
            role="AMBULANTE",
            cpf=data["cpf"],
            telefone=data["telefone"],
            foto_url=foto_url
        ),

        "BARRAQUEIRO": lambda: BarraqueiroResponse(
            user_id=user_id,
            nome=data["nome"],
            email=data["email"],
            role="BARRAQUEIRO",
            cpf=data["cpf"],
            telefone=data["telefone"],
            nome_barraca=data["nome_barraca"],
            foto_url=foto_url
        ),
    }

    try:
        return response_map[role]()
    except KeyError:
        raise AuthError(f"Role inválido: {role}")


async def signup_user(data: dict, foto=None):

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

    foto_url = None

    if foto:
        try:
            file_ext = foto.filename.split(".")[-1]
            file_path = f"{user_id}/profile.{file_ext}"

            file_bytes = await foto.read()

            upload_res = supabase.storage.from_("perfil").upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": foto.content_type},
            )

            if not upload_res:
                raise UploadError("Falha no upload da imagem")

            foto_url = supabase.storage.from_(
                "perfil").get_public_url(file_path)

        except Exception as e:
            raise UploadError(f"Erro ao enviar imagem: {str(e)}")

    if data["role"] != "CLIENTE":
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

    return build_response(data["role"], user_id, data, foto_url)


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


def verify_signup_code(email: str, token: str):
    try:
        return supabase.auth.verify_otp({
            "email": email,
            "token": token,
            "type": "email"
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
