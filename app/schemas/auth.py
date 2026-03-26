from pydantic import BaseModel, EmailStr
from typing import Optional


class AuthRequest(BaseModel):
    email: str
    password: str

class EmailRequest(BaseModel):
    email: EmailStr

class VerifyEmailRequest(BaseModel):
    email: str
    token: str



class BaseSignup(BaseModel):
    email: EmailStr
    password: str
    nome: str
    role: str

class ClienteSignup(BaseSignup):
    pass

class VendedorSignup(BaseSignup):
    cpf: str
    telefone: str
    
class AmbulanteSignup(VendedorSignup):
    pass

class BarraqueiroSignup(VendedorSignup):
    nome_barraca: str