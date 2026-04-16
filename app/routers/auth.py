from fastapi import APIRouter, HTTPException, status, Form, File, UploadFile
from typing import Optional,Union,Literal

from app.schemas.auth import (
    AuthError, AuthRequest, DatabaseError, EmailRequest, ForgotPasswordRequest, MessageResponse, ResetPasswordRequest, UploadError, ClienteResponse,AmbulanteResponse,BarraqueiroResponse, VerifyEmailRequest
)

from app.services import auth_service

router = APIRouter(tags=["Auth"])

@router.post(
    "/signup",
    response_model=Union[
        ClienteResponse,
        AmbulanteResponse,
        BarraqueiroResponse
    ],
    status_code=status.HTTP_201_CREATED
)
async def signup(
    email: str = Form(...),
    password: str = Form(...),
    nome: str = Form(...),
    role: Literal["CLIENTE", "AMBULANTE", "BARRAQUEIRO"] = Form(...),

    cpf: Optional[str] = Form(None),
    telefone: Optional[str] = Form(None),
    nome_barraca: Optional[str] = Form(None),

    foto: Optional[UploadFile] = File(None)
):
    if role == "CLIENTE":
        if cpf or telefone or nome_barraca:
            raise HTTPException(400, "Cliente não deve enviar cpf, telefone ou nome_barraca")

    if role == "AMBULANTE":
        if not cpf or not telefone:
            raise HTTPException(400, "Ambulante deve enviar cpf e telefone")

    if role == "BARRAQUEIRO":
        if not cpf or not telefone or not nome_barraca:
            raise HTTPException(400, "Barraqueiro deve enviar cpf, telefone e nome_barraca")

    data = {
        "email": email,
        "password": password,
        "nome": nome,
        "role": role,
        "cpf": cpf,
        "telefone": telefone,
        "nome_barraca": nome_barraca,
    }

    try:
        return await auth_service.signup_user(data, foto)

    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except UploadError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Erro inesperado no servidor")


@router.post("/signup-otp", response_model=MessageResponse)
async def verify_email_otp(data: VerifyEmailRequest):
    try:
        auth_service.verify_signup_code(data.email, data.token)
        return {"message": "E-mail verificado com sucesso!"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Código de verificação inválido ou expirado.")


@router.post("/login")
async def login(data: AuthRequest):
    try:
        return auth_service.login_user(data.email, data.password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )


@router.post("/check-email")
async def check_email(data: EmailRequest):
    exists = auth_service.check_email_exists(data.email)
    return {"email": data.email, "exists": exists}


@router.post("/logout", response_model=MessageResponse)
async def logout_endpoint():
    try:
        auth_service.logout()
        return {"message": "Sessão encerrada com sucesso."}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Não foi possível sair da conta no momento. Tente novamente.")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPasswordRequest):
    try:
        auth_service.send_recovery_email(data.email)
        return {"message": "Código de recuperação enviado para o seu e-mail."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPasswordRequest):
    try:
        auth_service.reset_password_with_otp(
            email=data.email,
            token=data.token,
            new_password=data.new_password
        )
        return {"message": "Senha redefinida com sucesso!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível redefinir a senha. O código pode estar incorreto ou expirado."
        )


@router.post("/resend-signup")
async def resend_signup(data: EmailRequest):
    try:
        auth_service.resend_signup_email(data.email)
        return {"message": "Código reenviado"}
    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
