from fastapi import HTTPException
from typing import Optional, Dict, Any
from app.core.logger import logger
from app.core.realtime import broadcast_association_closed, broadcast_charge_sent, broadcast_payment_confirmed
from app.core.upload_photo import upload_image


def close_association_with_charge(
    association_id: str,
    vendor_id: str,
    charge_amount: float,
    charge_photo_url: str,
    supabase_client
) -> Dict[str, Any]:
    """Encerra associação com cobrança (MAREPE-295)"""
    try:
        # Verificar se a associação pertence ao vendedor
        association = (
            supabase_client
            .table("customer_associations")
            .select("id, vendor_id, customer_id, status")
            .eq("id", association_id)
            .eq("vendor_id", vendor_id)
            .single()
            .execute()
        )

        if not association.data:
            raise HTTPException(
                status_code=404,
                detail="Associação não encontrada"
            )

        if association.data["status"] == "closed":
            raise HTTPException(
                status_code=400,
                detail="Esta associação já foi encerrada"
            )

        # Gerar chave PIX mock
        pix_key = f"pix_mock_{association_id[:8]}"

        # Atualizar status para pending_payment
        supabase_client.table("customer_associations").update({
            "status": "pending_payment",
            "charge_amount": charge_amount,
            "charge_photo_url": charge_photo_url,
            "pix_key": pix_key
        }).eq("id", association_id).execute()

        # Broadcast charge_sent
        broadcast_charge_sent(supabase_client, association_id, {
            "charge_amount": charge_amount,
            "charge_photo_url": charge_photo_url,
            "pix_key": pix_key
        })

        return {
            "message": "Cobrança enviada ao cliente",
            "status": "pending_payment"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao encerrar associação com cobrança: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar encerramento"
        )


def close_association_no_charge(
    association_id: str,
    vendor_id: str,
    supabase_client
) -> Dict[str, Any]:
    """Encerra associação sem cobrança (MAREPE-296)"""
    try:
        # Verificar se a associação pertence ao vendedor
        association = (
            supabase_client
            .table("customer_associations")
            .select("id, vendor_id, customer_id, status")
            .eq("id", association_id)
            .eq("vendor_id", vendor_id)
            .single()
            .execute()
        )

        if not association.data:
            raise HTTPException(
                status_code=404,
                detail="Associação não encontrada"
            )

        if association.data["status"] == "closed":
            raise HTTPException(
                status_code=400,
                detail="Esta associação já foi encerrada"
            )

        # Atualizar para encerrada sem cobrança
        supabase_client.table("customer_associations").update({
            "status": "closed",
            "active": False,
            "closed_at": "now()"
        }).eq("id", association_id).execute()

        # Broadcast association_closed
        broadcast_association_closed(supabase_client, association_id, {
            "no_charge": True,
            "message": "O barraqueiro encerrou o atendimento. Nenhum valor a pagar."
        })

        return {
            "message": "Associação encerrada com sucesso",
            "status": "closed"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao encerrar associação sem cobrança: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar encerramento"
        )


def request_close_from_customer(
    association_id: str,
    customer_id: str,
    supabase_client
) -> Dict[str, Any]:
    """Cliente solicita encerramento (MAREPE-306)"""
    try:
        # Verificar se a associação pertence ao cliente
        association = (
            supabase_client
            .table("customer_associations")
            .select("id, customer_id, status")
            .eq("id", association_id)
            .eq("customer_id", customer_id)
            .single()
            .execute()
        )

        if not association.data:
            raise HTTPException(
                status_code=404,
                detail="Associação não encontrada"
            )

        if association.data["status"] == "closed":
            raise HTTPException(
                status_code=400,
                detail="Esta associação já foi encerrada"
            )

        # Atualizar para pending_close
        supabase_client.table("customer_associations").update({
            "status": "pending_close"
        }).eq("id", association_id).execute()

        return {
            "message": "Solicitação de encerramento enviada ao estabelecimento",
            "status": "pending_close"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao solicitar encerramento: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar solicitação"
        )


def confirm_payment(
    association_id: str,
    customer_id: str,
    supabase_client
) -> Dict[str, Any]:
    """Cliente confirma pagamento (MAREPE-308)"""
    try:
        # Verificar se a associação pertence ao cliente
        association = (
            supabase_client
            .table("customer_associations")
            .select("id, customer_id, vendor_id, status")
            .eq("id", association_id)
            .eq("customer_id", customer_id)
            .single()
            .execute()
        )

        if not association.data:
            raise HTTPException(
                status_code=404,
                detail="Associação não encontrada"
            )

        if association.data["status"] != "pending_payment":
            raise HTTPException(
                status_code=400,
                detail="Esta associação não está aguardando pagamento"
            )

        # Atualizar para encerrada
        supabase_client.table("customer_associations").update({
            "status": "closed",
            "active": False,
            "closed_at": "now()"
        }).eq("id", association_id).execute()

        # Broadcast payment_confirmed
        broadcast_payment_confirmed(
            supabase_client,
            association_id,
            association.data["vendor_id"]
        )

        return {
            "message": "Pagamento confirmado com sucesso",
            "status": "closed"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao confirmar pagamento: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar confirmação de pagamento"
        )
