from fastapi import APIRouter,Depends
from app.core.security import get_user_id_from_token
from app.schemas.vendedor import (
    AtualizarCatalogoRequest,
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
    updated = vendedor_service.update_vendedor_status(
        user_id, data.status, supabase_client
    )

    return StatusUpdateResponse(
        user_id=updated["vendor_id"],
        status=updated["status"],
        last_seen_at=updated["last_seen_at"],
        message="Status atualizado com sucesso"
    )


@router.post("/location", response_model=LocationResponse)
async def save_location(
    data: LocationRequest,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
    vendedor_service.save_vendedor_location(
        user_id=user_id,
        latitude=data.latitude,
        longitude=data.longitude,
        accuracy=data.accuracy,
        supabase_client=supabase_client
    )

    return LocationResponse(
        user_id=user_id,
        latitude=data.latitude,
        longitude=data.longitude,
        accuracy=data.accuracy,
        message="Localização salva com sucesso"
    )


@router.put("/catalogo")
async def salvar_catalogo(
    data: AtualizarCatalogoRequest,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
    return vendedor_service.salvar_catalogo(
        user_id,
        data.categorias,
        supabase_client
    )



@router.get("/catalogo/categorias")
async def listar_categorias(
    supabase_client = Depends(get_supabase_client)
):
    return vendedor_service.get_categorias(supabase_client)