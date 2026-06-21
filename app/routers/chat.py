from fastapi import APIRouter, Depends, UploadFile, File
from app.core.security import get_user_id_from_token
from app.core.supabase_client import get_supabase_client
from app.schemas.chat import (
    MessageCreate,
    MessageResponse,
    MessagesHistoryResponse
)
from app.services import chat_service
from app.core.upload_photo import upload_image


router = APIRouter(tags=["Chat"])


@router.get(
    "/associations/{association_id}/messages",
    response_model=MessagesHistoryResponse
)
async def get_messages(
    association_id: str,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    """Retorna o histórico completo de mensagens de uma associação (MAREPE-272)"""
    messages = chat_service.get_association_messages(association_id, supabase_client)
    return {"messages": messages}


@router.post(
    "/associations/{association_id}/messages",
    response_model=MessageResponse,
    status_code=201
)
async def send_message(
    association_id: str,
    message: MessageCreate,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    """Envia uma mensagem de texto no chat (MAREPE-273)"""
    result = chat_service.send_text_message(
        association_id=association_id,
        sender_id=user_id,
        content=message.content,
        supabase_client=supabase_client
    )
    return result


@router.post(
    "/associations/{association_id}/messages/photo",
    response_model=MessageResponse,
    status_code=201
)
async def send_photo(
    association_id: str,
    photo: UploadFile = File(...),
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    """Envia uma foto como mensagem no chat (MAREPE-287)"""
    # Upload da foto para o storage
    photo_url = await upload_image(
        file=photo,
        vendor_id=user_id,
        folder="chat",
        supabase_client=supabase_client
    )

    # Criar mensagem com a URL da foto
    result = chat_service.send_photo_message(
        association_id=association_id,
        sender_id=user_id,
        photo_url=photo_url,
        supabase_client=supabase_client
    )
    return result
