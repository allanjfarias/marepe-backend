from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import Optional
from app.core.security import get_user_id_from_token
from app.core.supabase_client import get_supabase_client
from app.services import association_service
from app.core.upload_photo import upload_image


router = APIRouter(tags=["Associações"])


@router.patch("/associations/{association_id}/close", status_code=200)
async def close_association(
    association_id: str,
    charge_amount: Optional[float] = Form(None),
    charge_photo: Optional[UploadFile] = File(None),
    no_charge: bool = Form(False),
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    """
    Encerrar associação pelo barraqueiro (MAREPE-295, 296)
    - Com cobrança: charge_amount + charge_photo obrigatórios
    - Sem cobrança: no_charge=True
    """
    if no_charge:
        return association_service.close_association_no_charge(
            association_id=association_id,
            vendor_id=user_id,
            supabase_client=supabase_client
        )
    else:
        if not charge_amount or not charge_photo:
            raise HTTPException(
                status_code=400,
                detail="Para encerrar com cobrança, informe o valor e a foto da comanda"
            )

        # Upload da foto da comanda
        photo_url = await upload_image(
            file=charge_photo,
            vendor_id=user_id,
            folder="charge",
            supabase_client=supabase_client
        )

        return association_service.close_association_with_charge(
            association_id=association_id,
            vendor_id=user_id,
            charge_amount=charge_amount,
            charge_photo_url=photo_url,
            supabase_client=supabase_client
        )


@router.post("/associations/{association_id}/request-close", status_code=200)
async def request_close(
    association_id: str,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    """Cliente solicita encerramento (MAREPE-306)"""
    return association_service.request_close_from_customer(
        association_id=association_id,
        customer_id=user_id,
        supabase_client=supabase_client
    )


@router.post("/associations/{association_id}/confirm-payment", status_code=200)
async def confirm_payment(
    association_id: str,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    """Cliente confirma pagamento (MAREPE-308)"""
    return association_service.confirm_payment(
        association_id=association_id,
        customer_id=user_id,
        supabase_client=supabase_client
    )
