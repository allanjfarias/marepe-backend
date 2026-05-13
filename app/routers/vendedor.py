from fastapi import APIRouter, Depends
from app.core.security import get_user_id_from_token
from app.schemas.vendedor import (
    StatusUpdateRequest,
    StatusUpdateResponse,
    LocationRequest,
    LocationResponse,
    ToggleCategoriaRequest,
    VitrineResponse,
    CatalogoResponse,
    AtualizarCatalogoRequest
)
from app.services import vendedor_service
from app.core.supabase_client import get_supabase_client

router = APIRouter(tags=["Vendedor"])


@router.put("/status", response_model=StatusUpdateResponse)
async def update_status(
    data: StatusUpdateRequest,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
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
    supabase_client=Depends(get_supabase_client)
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


@router.get("/minhas-categorias", response_model=VitrineResponse)
async def listar(
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    return vendedor_service.listar_catalogo(user_id, supabase_client)


@router.patch("/atualizar-categoria")
async def toggle(
    data: ToggleCategoriaRequest,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    return vendedor_service.toggle_catalogo(user_id, data, supabase_client)


@router.get("/catalogo", response_model=list[CatalogoResponse])
async def obter_meu_catalogo(
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
    """Retorna o catálogo do vendedor logado"""
    from app.services import cliente_service
    return cliente_service.get_catalogo_vendedor(user_id, supabase_client)


@router.put("/catalogo")
async def salvar_catalogo(
    data: AtualizarCatalogoRequest,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    """Atualiza o catálogo do vendedor"""
    from app.services import vendedor_service
    return vendedor_service.atualizar_catalogo(user_id, data, supabase_client)


@router.get("/catalogo/categorias")
async def listar_categorias(
    supabase_client = Depends(get_supabase_client)
):
    """Lista todas as categorias disponíveis"""
    from app.services import cliente_service
    return cliente_service.listar_todas_categorias(supabase_client)
