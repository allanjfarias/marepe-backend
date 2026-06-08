
from fastapi import APIRouter, Depends, Header, Form, File, UploadFile
from app.core.security import get_supabase_user
from app.core.supabase_client import get_supabase_client
from app.schemas.profile import ProfileResponse
from app.services import profile_service


router = APIRouter(tags=["Profile"])

@router.get("/my-profile", response_model=ProfileResponse)
def my_profile(
    supabase_client=Depends(get_supabase_client),
    supabase_user=Depends(get_supabase_user)
):

    return profile_service.get_my_profile(supabase_client, supabase_user.id)


@router.put("/my-profile")
async def update_profile(
    nome: str = Form(None),
    telefone: str = Form(None),
    nome_barraca: str = Form(None),
    foto: UploadFile = File(None),
    supabase_client=Depends(get_supabase_client),
    supabase_user=Depends(get_supabase_user)
):
    """Atualiza o perfil do usuário logado"""
    return await profile_service.update_my_profile(
        supabase_client=supabase_client,
        user_id=supabase_user.id,
        nome=nome,
        telefone=telefone,
        nome_barraca=nome_barraca,
        foto=foto
    )
