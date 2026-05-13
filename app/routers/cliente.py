
from fastapi import APIRouter,Depends, Query
from app.core.supabase_client import get_supabase_client
from app.schemas.vendedor import CatalogoResponse, NearbyVendorSchema, NearbyVendorSchema
from app.services import cliente_service  


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