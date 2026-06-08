
from pydantic import BaseModel
from typing import Optional


class VendedorResponse(BaseModel):
    cpf: str
    telefone: str
    foto_url: str | None = None
    nome_barraca: str | None = None


class ClienteResponse(BaseModel):
    cpf: str | None = None
    telefone: str | None = None
    foto_url: str | None = None


class ProfileResponse(BaseModel):
    id: str
    nome: str
    role: str
    vendedor: Optional[VendedorResponse] = None
    cliente: Optional[ClienteResponse] = None