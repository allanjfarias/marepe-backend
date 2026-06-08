
from fastapi import APIRouter,Depends, HTTPException, Query
from app.core.security import get_user_id_from_token
from app.core.supabase_client import get_supabase_client
from app.schemas.vendedor import CatalogoResponse, NearbyVendorSchema, NearbyVendorSchema
from app.schemas.cardapio import CardapioItem
from app.services import cliente_service, cardapio_service


router = APIRouter(tags=["Cliente"])




@router.get("/vendedores/{vendor_id}/catalogo", response_model=list[CatalogoResponse])
async def get_catalogo_vendedor(
    vendor_id: str,
    supabase_client = Depends(get_supabase_client)
):
    return cliente_service.get_vitrine_vendedor(
        vendor_id,
        supabase_client
    )


@router.get(
    "/vendedor-location",
    response_model=list[NearbyVendorSchema]
)
async def get_nearby_vendors(
    supabase_client = Depends(get_supabase_client),

    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius: int = Query(1000, gt=0),
):
    return cliente_service.get_vendedores_proximos(
        supabase_client,
        lat,
        lng,
        radius
    )


@router.get("/ambulante/{ambulante_id}/cardapio", response_model=list[CardapioItem])
async def get_cardapio(
    ambulante_id: str,
    supabase_client = Depends(get_supabase_client)
):
    return cardapio_service.get_cardapio_vendedor(ambulante_id, supabase_client)



@router.post("/associations", status_code=201)
async def create_association_endpoint(
    vendor_id: str, # Recebido no body ou query param, conforme seu design
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    try:
        return cliente_service.create_association(
            customer_id=user_id,
            vendor_id=vendor_id,
            supabase_client=supabase_client
        )
    except HTTPException as e:
        # Repassa o erro 409 caso a regra de negócio falhe
        raise e
    except Exception as e:
        # EX01: Tratamento de exceção genérica
        print(f"Erro ao criar associação: {e}")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível se associar no momento. Tente novamente."
        )