from fastapi import HTTPException
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


async def signup_user(data: dict,supabase_client, foto=None):
    auth_response = supabase_client.auth.sign_up({
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
            file_bytes = bytes(file_bytes)

            upload_res = supabase_client.storage.from_("perfil").upload(
                file_path,
                file_bytes,
                {
                    "content-type": foto.content_type,
                    "upsert": "true"
                }
            )

            if not upload_res:
                raise UploadError("Falha no upload da imagem")

            foto_url = supabase_client.storage.from_("perfil").get_public_url(file_path)

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

            supabase_client.table("vendedores").insert(vendedor_data).execute()

        except Exception as e:
            raise DatabaseError(f"Erro ao salvar vendedor: {str(e)}")

    return build_response(data["role"], user_id, data, foto_url)


def login_user(email: str, password: str, supabase_client):
    try:
        return supabase_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
    except Exception as e:
        raise HTTPException(
            status_code=401, detail="E-mail ou senha incorretos.")


def check_email_exists(email: str, supabase_client) -> bool:
    logger.info(f"[START] email raw={repr(email)} len={len(email)}")

    email_clean = email.strip().lower()

    logger.info(f"[NORMALIZED] email_clean={repr(email_clean)}")

    query = (
        supabase_client.table("users")
        .select("id")
        .eq("email", email_clean)
        .limit(1)
    )

    logger.info(f"[QUERY BUILT] {query}")

    response = query.execute()

    logger.info(f"[RAW RESPONSE] {response}")

    data = response.data

    logger.info(f"[DATA] {data}")

    exists = bool(data and len(data) > 0)

    logger.info(f"[EXISTS] {exists}")

    return exists

def send_recovery_email(email: str, supabase_client):
    try:
        return supabase_client.auth.reset_password_for_email(email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



def logout(supabase_client):
    try:
        return supabase_client.auth.sign_out()
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Não foi possível sair da conta no momento. Tente novamente. {str(e)}" )


def resend_signup_email(email: str, supabase_client):
    try:
        return supabase_client.auth.resend({
            "type": "signup",
            "email": email
        })
    except Exception as e:
        raise AuthError("Erro ao reenviar email" + str(e))


def verify_signup_code(email: str, token: str, supabase_client):
    try:
        return supabase_client.auth.verify_otp({
            "email": email,
            "token": token,
            "type": "email"
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail= f"Erro ao verificar código de email: {e}")




def verify_recovery_otp(email: str, token: str, supabase_client):
    try:
        res = supabase_client.auth.verify_otp({
            "email": email,
            "token": token,
            "type": "recovery"
        })

        if not res.session:
            raise HTTPException(
                status_code=400,
                detail="Código inválido ou expirado."
            )

        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token
        }

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Código inválido ou expirado."
        )


def update_password(
    access_token: str,
    refresh_token: str,
    new_password: str,
    supabase_client
):
    try:
        supabase_client.auth.set_session(
            access_token,
            refresh_token
        )

        res = supabase_client.auth.update_user({
            "password": new_password
        })

        return {
            "message": "Senha atualizada com sucesso.",
            "user": res.user
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao atualizar senha: {str(e)}"
        )