from pydantic import BaseModel
from typing import Optional

class CardapioItem(BaseModel):
    id: str
    vendedor_id: str
    nome: str
    preco: float
    disponivel: bool
    descricao: Optional[str] = None
