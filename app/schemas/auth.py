from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


class EmailRequest(BaseModel):
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    token: str


class BaseSignup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8,
                         description="A senha deve ter ao menos 8 caracteres")
    nome: str

class ClienteSignup(BaseSignup):
    role: Literal["CLIENTE"]

class AmbulanteSignup(BaseSignup):
    role: Literal["AMBULANTE"]
    cpf: str
    telefone: str

class BarraqueiroSignup(AmbulanteSignup):
    role: Literal["BARRAQUEIRO"]
    nome_barraca: str

class AmbulanteResponse(BaseModel):
    user_id: str
    nome: str
    email: str
    role: Literal["AMBULANTE"]

    cpf: str
    telefone: str
    foto_url: str | None = None

class BarraqueiroResponse(AmbulanteResponse):
    role: Literal["BARRAQUEIRO"]
    nome_barraca: str

class ClienteResponse(BaseModel):
    user_id: str
    nome: str
    email: str
    role: Literal["CLIENTE"]

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyRecoveryOtpRequest(BaseModel):
    email: EmailStr
    token: str  


class ResetPasswordRequest(BaseModel):
    access_token: str
    refresh_token: str
    new_password: str = Field(..., min_length=8, description="A senha deve ter ao menos 8 caracteres")

class MessageResponse(BaseModel):
    message: str

class AuthError(Exception):
    pass


class UploadError(Exception):
    pass


class DatabaseError(Exception):
    pass