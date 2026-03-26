from fastapi import APIRouter
from typing import Union
from app.schemas.auth import (
    BarraqueiroSignup, AmbulanteSignup, ClienteSignup, AuthRequest, EmailRequest, VerifyEmailRequest
)
from app.services.auth_service import signup_user, login_user, verify_signup_code, check_email_exists

router = APIRouter()


@router.post("/signup")
def signup(data: Union[BarraqueiroSignup, AmbulanteSignup, ClienteSignup]):
    return signup_user(data.model_dump())


@router.post("/login")
def login(data: AuthRequest):
    return login_user(data.email, data.password)


@router.post("/check-email")
def check_email(data: EmailRequest):
    exists = check_email_exists(data.email)
    return {"email": data.email, "exists": exists}


@router.post("/signup-otp")
def verify_email_otp(data: VerifyEmailRequest):
    return verify_signup_code(data.email, data.token)
