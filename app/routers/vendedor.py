from fastapi import APIRouter, HTTPException,Depends
from typing import Optional
from app.core.security import get_user_id_from_token

from app.schemas.vendedor import (
    StatusUpdateRequest,
    StatusUpdateResponse,
    LocationRequest,
    LocationResponse
)

from app.services import vendedor_service
from app.core.supabase_client import get_supabase_client

router = APIRouter(tags=["Vendedor"])




@router.put("/status", response_model=StatusUpdateResponse)
async def update_status(
    data: StatusUpdateRequest,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
 
    try:
        vendedor_service.update_vendedor_status(user_id, data.status,supabase_client)

        return StatusUpdateResponse(
            user_id=user_id,
            status=data.status,
            message=f"Status atualizado para {data.status}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar status: {str(e)}"
            )


# @router.post("/location", response_model=LocationResponse)
# async def save_location(
#     data: LocationRequest,
#     user_id: str = Depends(get_user_id_from_token),
#     supabase_client = Depends(get_supabase_client)

# ):

#     try:
#         vendedor_service.save_vendedor_location(
#             user_id=user_id,
#             latitude=data.latitude,
#             longitude=data.longitude,
#             accuracy=data.accuracy,
#             supabase_client=supabase_client)

#         return LocationResponse(
#             user_id=user_id,
#             latitude=data.latitude,
#             longitude=data.longitude,
#             accuracy=data.accuracy,
#             message="Localização salva com sucesso"
#         )
    
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Erro ao salvar localização: {str(e)}"
#         )
