from fastapi import APIRouter, HTTPException, status, Form, File, UploadFile, Depends
from app.core.supabase_client import get_supabase_client
from app.core.security import get_token
from typing import Optional,Union,Literal

from app.schemas.auth import (
    AuthError, AuthRequest, DatabaseError, EmailRequest, ForgotPasswordRequest, MessageResponse, ResetPasswordRequest, UploadError, ClienteResponse,AmbulanteResponse,BarraqueiroResponse, VerifyEmailRequest, VerifyRecoveryOtpRequest
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

    foto: Optional[UploadFile] = File(None),
    supabase_client  =Depends(get_supabase_client)
    
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
        return await auth_service.signup_user(data,supabase_client,foto)

    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except UploadError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Erro inesperado no servidor")


@router.post("/signup-otp", response_model=MessageResponse)
def verify_email_otp(data: VerifyEmailRequest, supabase_client=Depends(get_supabase_client)):
    try:
        auth_service.verify_signup_code(data.email, data.token, supabase_client)
        return {"message": "E-mail verificado com sucesso!"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Código de verificação inválido ou expirado.")


@router.post("/login")
def login(data: AuthRequest, supabase_client=Depends(get_supabase_client)):
    try:
        return auth_service.login_user(data.email, data.password, supabase_client)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )




@router.post("/check-email")
def check_email(data: EmailRequest, supabase_client=Depends(get_supabase_client)):
    exists = auth_service.check_email_exists(data.email, supabase_client)
    return {"email": data.email, "exists": exists}


@router.post("/logout", response_model=MessageResponse)
def logout_endpoint(
    supabase_client=Depends(get_supabase_client)
    ):
    try:
        auth_service.logout(supabase_client)
        
        return {"message": "Sessão encerrada com sucesso."}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Não foi possível sair da conta no momento. Tente novamente.")


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(data: ForgotPasswordRequest, supabase_client=Depends(get_supabase_client)):
    try:
        auth_service.send_recovery_email(data.email, supabase_client)
        return {"message": "Código de recuperação enviado para o seu e-mail."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-recovery-otp")
def verify_recovery_otp(data: VerifyRecoveryOtpRequest, supabase_client=Depends(get_supabase_client)):
    try:
        tokens = auth_service.verify_recovery_otp(data.email, data.token, supabase_client)
        return tokens
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Código inválido ou expirado."
        )


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, supabase_client=Depends(get_supabase_client)):
    try:
        auth_service.update_password(data.access_token, data.refresh_token, data.new_password, supabase_client)
        return {"message": "Senha atualizada com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)
                            )


@router.post("/resend-signup")
def resend_signup(data: EmailRequest, supabase_client=Depends(get_supabase_client)):
    try:
        auth_service.resend_signup_email(data.email, supabase_client)
        return {"message": "Código reenviado"}
    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
