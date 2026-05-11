
from fastapi import APIRouter, Depends, Header
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

    