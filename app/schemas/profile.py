
from pydantic import BaseModel
from typing import Optional


class VendedorResponse(BaseModel):
    cpf: str
    telefone: str
    foto_url: str
    nome_barraca: str


class ProfileResponse(BaseModel):
    id: str
    nome: str
    role: str
    vendedor: Optional[VendedorResponse] = None