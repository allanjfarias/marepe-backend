from fastapi import APIRouter, Depends

from app.schemas.barraca import (
    AssociatedCustomersResponse,
    EstablishmentDetailsResponse
)

from app.services import barraca_service

from app.core.security import (
    get_user_id_from_token
)

from app.core.supabase_client import (
    get_supabase_client
)

router = APIRouter(
    tags=["Estabelecimentos"]
)


@router.get(
    "/{vendor_id}",
    response_model=EstablishmentDetailsResponse
)
async def get_establishment_details(
    vendor_id: str,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    establishment = (
        barraca_service.get_establishment_details(
            vendor_id=vendor_id,
            customer_id=user_id,
            supabase_client=supabase_client
        )
    )

    return EstablishmentDetailsResponse(**establishment)


@router.get(
    "/my-associations", 
    response_model=AssociatedCustomersResponse
)
async def list_associated_customers(
    vendor_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    customers = barraca_service.get_associated_customers(vendor_id, supabase_client)
    return {"customers": customers}