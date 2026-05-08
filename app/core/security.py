from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase_client import get_supabase_client
from app.core.logger import logger


security = HTTPBearer()


def get_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials
    logger.info(f"Token recebido")

    if not token:
        raise HTTPException(status_code=401, detail="Token ausente")

    return token


def get_supabase_user(
    token: str = Depends(get_token),
    supabase=Depends(get_supabase_client)
):
    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            raise HTTPException(status_code=401, detail="Usuário inválido")

        return user

    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        raise HTTPException(status_code=401, detail="Falha na autenticação")


def get_user_id_from_token(
    user=Depends(get_supabase_user)
) -> str:
    return user.id
