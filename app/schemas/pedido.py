from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime

# Status do pedido
PedidoStatus = Literal["pendente", "aceito", "negado", "cancelado", "expirado", "em_preparo", "pronto", "entregue"]


class ItemPedido(BaseModel):
    """Item do cardapio no pedido"""
    item_id: str
    nome: str
    quantidade: int
    preco_unitario: float


class PedidoCreateRequest(BaseModel):
    """Request para criar um novo pedido"""
    ambulante_id: str = Field(..., description="ID do ambulante que receberá o pedido")
    categorias: List[str] = Field(default=[], description="Lista de IDs de categorias solicitadas")
    itens: Optional[List[ItemPedido]] = Field(None, description="Itens do cardapio selecionados")


class PedidoResponse(BaseModel):
    """Response com dados do pedido"""
    id: str
    ambulante_id: str
    cliente_id: str
    categorias: List[str]
    status: PedidoStatus
    created_at: datetime
    posicao_fila: Optional[int] = None
    itens: Optional[List[ItemPedido]] = None
    valor_total: Optional[float] = None
    ambulante_nome: Optional[str] = None


class PedidoFilaResponse(BaseModel):
    """Response com dados do pedido na fila (visão do ambulante)"""
    id: str
    cliente_id: str
    cliente_nome: Optional[str] = None
    cliente_foto: Optional[str] = None
    categorias: List[str]
    categorias_nomes: Optional[List[str]] = None
    distancia_metros: Optional[float] = None
    created_at: datetime
    tempo_restante_segundos: int
    posicao: int  # Posição na fila (1, 2, 3...)


class AceitarPedidoResponse(BaseModel):
    """Response ao aceitar pedido"""
    pedido_id: str
    message: str
    status: str  # "em_atendimento"


class NegarPedidoResponse(BaseModel):
    """Response ao negar pedido"""
    pedido_id: str
    message: str
    proximo_pedido: Optional[PedidoFilaResponse] = None


class UpdateStatusRequest(BaseModel):
    """Request para atualizar status do pedido"""
    status: Literal["em_preparo", "pronto", "entregue"] = Field(..., description="Novo status do pedido")
