from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_user_id_from_token
from app.core.supabase_client import get_supabase_client
from app.schemas.pedido import (
    PedidoCreateRequest,
    PedidoResponse,
    PedidoFilaResponse,
    AceitarPedidoResponse,
    NegarPedidoResponse
)
from app.services import pedido_service
from typing import List

router = APIRouter(tags=["Pedidos"])


@router.post("/pedidos", response_model=PedidoResponse)
async def criar_pedido(
    data: PedidoCreateRequest,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
    """
    Cria uma nova solicitação de pedido

    Validações:
    - Cliente não pode ter pedido ativo com o mesmo ambulante (ALT01)
    - Ambulante não pode estar em atendimento (AC05 - auto-negação)

    Raises:
    - 400: Se validações falharem
    - 500: Se houver erro ao criar pedido (EX01)
    """
    pedido = pedido_service.criar_pedido(
        cliente_id=user_id,
        ambulante_id=data.ambulante_id,
        categorias=data.categorias,
        supabase_client=supabase_client
    )

    return PedidoResponse(**pedido)


@router.get("/ambulante/pedidos/fila", response_model=List[PedidoFilaResponse])
async def listar_fila(
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
    """
    Lista todos os pedidos pendentes na fila do ambulante
    Ordenados por FIFO (created_at ASC)

    Retorna:
    - Lista de pedidos com posição, timer, dados do cliente
    """
    fila = pedido_service.listar_fila_ambulante(
        ambulante_id=user_id,
        supabase_client=supabase_client
    )

    return [PedidoFilaResponse(**pedido) for pedido in fila]


@router.patch("/pedidos/{pedido_id}/aceitar", response_model=AceitarPedidoResponse)
async def aceitar_pedido(
    pedido_id: str,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
    """
    Aceita um pedido (AC04)

    Ações:
    1. Atualiza status do pedido para "aceito"
    2. Muda status do ambulante para "em_atendimento"
    3. Pin fica vermelho no mapa (broadcast)
    4. Cancela todos os outros pedidos pendentes na fila
    5. Notifica clientes cancelados (avanço de fila)
    6. Notifica cliente aceito

    Raises:
    - 404: Pedido não encontrado
    - 400: Pedido não está pendente
    - 500: Erro ao aceitar (EX01)
    """
    resultado = pedido_service.aceitar_pedido(
        pedido_id=pedido_id,
        ambulante_id=user_id,
        supabase_client=supabase_client
    )

    return AceitarPedidoResponse(**resultado)


@router.patch("/pedidos/{pedido_id}/negar", response_model=NegarPedidoResponse)
async def negar_pedido(
    pedido_id: str,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
    """
    Nega um pedido manualmente (AC03)

    Ações:
    1. Atualiza status para "negado"
    2. Notifica cliente
    3. Retorna próximo pedido da fila (se houver)

    Raises:
    - 404: Pedido não encontrado
    - 400: Pedido não está pendente
    """
    resultado = pedido_service.negar_pedido(
        pedido_id=pedido_id,
        ambulante_id=user_id,
        supabase_client=supabase_client
    )

    return NegarPedidoResponse(**resultado)


@router.delete("/pedidos/{pedido_id}")
async def cancelar_pedido(
    pedido_id: str,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
    """
    Cancela um pedido pelo cliente (AC05)

    Ações:
    1. Atualiza status para "cancelado"
    2. Remove da fila
    3. Notifica ambulante

    Raises:
    - 404: Pedido não encontrado
    - 400: Pedido não pode ser cancelado
    """
    resultado = pedido_service.cancelar_pedido(
        pedido_id=pedido_id,
        cliente_id=user_id,
        supabase_client=supabase_client
    )

    return resultado
