from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CardapioItem(BaseModel):
    id: str
    vendedor_id: str
    nome: str
    preco: float
    disponivel: bool
    descricao: Optional[str] = None
    categoria_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=255, description="Nome do produto")
    preco: float = Field(..., gt=0, description="Preço do produto (maior que 0)")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição opcional")
    categoria_id: Optional[str] = Field(None, description="ID da categoria (opcional)")


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=255)
    preco: Optional[float] = Field(None, gt=0)
    descricao: Optional[str] = Field(None, max_length=1000)
    categoria_id: Optional[str] = None
