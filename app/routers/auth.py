from fastapi import APIRouter
from app.schemas.auth import AuthRequest, EmailRequest
from app.services.auth_service import signup_user, login_user, check_email_exists

router = APIRouter()


@router.post("/signup")
def signup(data: AuthRequest):
    return signup_user(data.email, data.password)


@router.post("/login")
def login(data: AuthRequest):
    return login_user(data.email, data.password)


@router.get("/check-email")
def check_email(email: str):
    exists = check_email_exists(email)
    return {"email": email, "exists": exists}
