from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional

from app.schemas.vendedor import (
    StatusUpdateRequest,
    StatusUpdateResponse,
    LocationRequest,
    LocationResponse
)

from app.services import vendedor_service
from app.core.supabase_client import supabase

router = APIRouter(tags=["Vendedor"])


def get_user_id_from_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Extrai o user_id do token JWT no header Authorization
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido"
        )

    try:
        token = authorization.replace("Bearer ", "")
        user = supabase.auth.get_user(token)

        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )

        return user.user.id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falha na autenticação"
        )


@router.put("/status", response_model=StatusUpdateResponse)
async def update_status(
    data: StatusUpdateRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Atualiza o status do vendedor para online ou offline
    """
    user_id = get_user_id_from_token(authorization)

    try:
        result = vendedor_service.update_vendedor_status(user_id, data.status)

        return StatusUpdateResponse(
            user_id=user_id,
            status=data.status,
            message=f"Status atualizado para {data.status}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar status"
        )


@router.post("/location", response_model=LocationResponse)
async def save_location(
    data: LocationRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Salva a localização atual do vendedor
    """
    user_id = get_user_id_from_token(authorization)

    try:
        result = vendedor_service.save_vendedor_location(
            user_id=user_id,
            latitude=data.latitude,
            longitude=data.longitude,
            accuracy=data.accuracy
        )

        return LocationResponse(
            user_id=user_id,
            latitude=data.latitude,
            longitude=data.longitude,
            accuracy=data.accuracy,
            message="Localização salva com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar localização"
        )
