from pydantic import BaseModel, EmailStr, Field
from typing import Optional


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
    password: str = Field(..., min_length=8, description="A senha deve ter ao menos 8 caracteres")
    nome: str
    role: str # 'CLIENTE', 'AMBULANTE' ou 'BARRAQUEIRO'

class ClienteSignup(BaseSignup):
    pass

class VendedorSignup(BaseSignup):
    cpf: str
    telefone: str
    
class AmbulanteSignup(VendedorSignup):
    pass

class BarraqueiroSignup(VendedorSignup):
    nome_barraca: str

# --- Fluxo de Recuperação de Senha ---

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    token: str = Field(..., description="Código OTP enviado por e-mail")
    new_password: str = Field(..., min_length=8, description="A nova senha deve ter ao menos 8 caracteres")


class MessageResponse(BaseModel):
    message: str

class AuthError(Exception):
    pass