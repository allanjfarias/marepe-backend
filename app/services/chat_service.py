from fastapi import HTTPException
from typing import List, Dict, Any
from app.core.logger import logger
from app.core.realtime import broadcast_nova_mensagem


def get_association_messages(association_id: str, supabase_client) -> List[Dict[str, Any]]:
    """Retorna o histórico completo de mensagens de uma associação (MAREPE-272)"""
    try:
        response = (
            supabase_client
            .table("association_messages")
            .select("*")
            .eq("association_id", association_id)
            .order("created_at", desc=False)
            .execute()
        )

        return response.data or []

    except Exception as e:
        logger.error(f"Erro ao buscar histórico de mensagens: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro ao carregar o histórico de mensagens"
        )


def send_text_message(
    association_id: str,
    sender_id: str,
    content: str,
    supabase_client
) -> Dict[str, Any]:
    """Envia uma mensagem de texto no chat (MAREPE-273)"""
    try:
        # Verificar se a associação existe e está ativa
        association = (
            supabase_client
            .table("customer_associations")
            .select("id, status")
            .eq("id", association_id)
            .single()
            .execute()
        )

        if not association.data:
            raise HTTPException(
                status_code=404,
                detail="Associação não encontrada"
            )

        if association.data.get("status") == "closed":
            raise HTTPException(
                status_code=400,
                detail="Não é possível enviar mensagens em uma associação encerrada"
            )

        # Inserir mensagem
        message = (
            supabase_client
            .table("association_messages")
            .insert({
                "association_id": association_id,
                "sender_id": sender_id,
                "message_type": "text",
                "content": content
            })
            .execute()
        )

        result = message.data[0] if message.data else {}

        # Broadcast da nova mensagem
        if result:
            broadcast_nova_mensagem(supabase_client, association_id, result)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro ao enviar mensagem"
        )


def send_photo_message(
    association_id: str,
    sender_id: str,
    photo_url: str,
    supabase_client
) -> Dict[str, Any]:
    """Envia uma foto como mensagem no chat (MAREPE-287)"""
    try:
        # Verificar se a associação existe e está ativa
        association = (
            supabase_client
            .table("customer_associations")
            .select("id, status")
            .eq("id", association_id)
            .single()
            .execute()
        )

        if not association.data:
            raise HTTPException(
                status_code=404,
                detail="Associação não encontrada"
            )

        if association.data.get("status") == "closed":
            raise HTTPException(
                status_code=400,
                detail="Não é possível enviar mensagens em uma associação encerrada"
            )

        # Inserir mensagem com foto
        message = (
            supabase_client
            .table("association_messages")
            .insert({
                "association_id": association_id,
                "sender_id": sender_id,
                "message_type": "photo",
                "content": photo_url
            })
            .execute()
        )

        result = message.data[0] if message.data else {}

        # Broadcast da nova mensagem
        if result:
            broadcast_nova_mensagem(supabase_client, association_id, result)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao enviar foto: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro ao enviar foto"
        )
