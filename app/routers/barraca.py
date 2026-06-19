from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import List, Optional

from app.schemas.barraca import (
    AssociatedCustomersResponse,
    EstablishmentDetailsResponse,
    VendorStandResponse
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
    "/my-associations", 
    response_model=AssociatedCustomersResponse
)
async def list_associated_customers(
    # Renomeei para vendor_id_from_token para clareza
    vendor_id_from_token: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    customers = barraca_service.get_associated_customers(vendor_id_from_token, supabase_client)
    return {"customers": customers}

# 2. Rota dinâmica depois
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



@router.post(
    "/register-stand",
    response_model=VendorStandResponse
)
async def register_vendor_stand(
    latitude: float = Form(...),
    longitude: float = Form(...),

    

    establishment_photos: Optional[List[UploadFile]] = File(None),
    
    menu_photos: Optional[List[UploadFile]] = File(None),

    user=Depends(get_user_id_from_token),

    supabase_client=Depends(get_supabase_client)
):

    return await barraca_service.create_vendor_stand(
        vendor_id=user,
        latitude=latitude,
        longitude=longitude,
        establishment_photos=establishment_photos,
        menu_photos=menu_photos,
        supabase_client=supabase_client
    )