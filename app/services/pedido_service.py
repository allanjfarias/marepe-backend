"""
Service para gerenciamento de pedidos
"""
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from app.core.realtime import (
    broadcast_pedido_criado,
    broadcast_pedido_aceito,
    broadcast_pedido_negado,
    broadcast_pedido_cancelado,
    broadcast_avanco_fila,
    broadcast_pin_vermelho
)


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def criar_pedido(
    cliente_id: str,
    ambulante_id: str,
    categorias: List[str],
    supabase_client
) -> Dict[str, Any]:
    """
    Cria um novo pedido e adiciona na fila do ambulante
    Validações:
    - Cliente não pode ter pedido ativo com o mesmo ambulante
    - Ambulante não pode estar em atendimento (AC05)
    """
    try:
        # Verificar se ambulante está em atendimento
        presenca = (
            supabase_client
            .table("vendor_presence")
            .select("status")
            .eq("vendor_id", ambulante_id)
            .single()
            .execute()
        )

        if presenca.data and presenca.data.get("status") == "em_atendimento":
            raise HTTPException(
                status_code=400,
                detail="Ambulante está em atendimento no momento. Tente mais tarde."
            )

        # Verificar se cliente já tem pedido ativo com este ambulante
        pedido_ativo = (
            supabase_client
            .table("pedidos")
            .select("id")
            .eq("cliente_id", cliente_id)
            .eq("ambulante_id", ambulante_id)
            .in_("status", ["pendente", "aceito"])
            .execute()
        )

        if pedido_ativo.data:
            raise HTTPException(
                status_code=400,
                detail="Você já possui uma solicitação ativa com este ambulante."
            )

        # Criar pedido
        novo_pedido = {
            "cliente_id": cliente_id,
            "ambulante_id": ambulante_id,
            "categorias": categorias,
            "status": "pendente",
            "created_at": now_utc()
        }

        response = (
            supabase_client
            .table("pedidos")
            .insert(novo_pedido)
            .execute()
        )

        if not response.data:
            raise HTTPException(500, "Falha ao criar pedido")

        pedido = response.data[0]

        # Calcular posição na fila
        posicao = calcular_posicao_fila(ambulante_id, pedido["id"], supabase_client)
        pedido["posicao_fila"] = posicao

        # Broadcast para o ambulante
        broadcast_pedido_criado(supabase_client, ambulante_id, pedido)

        return pedido

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


def calcular_posicao_fila(ambulante_id: str, pedido_id: str, supabase_client) -> int:
    """
    Calcula a posição do pedido na fila (ordem FIFO por created_at)
    """
    try:
        fila = (
            supabase_client
            .table("pedidos")
            .select("id, created_at")
            .eq("ambulante_id", ambulante_id)
            .eq("status", "pendente")
            .order("created_at", desc=False)
            .execute()
        )

        for idx, pedido in enumerate(fila.data, start=1):
            if pedido["id"] == pedido_id:
                return idx

        return 1

    except Exception:
        return 1


def listar_fila_ambulante(ambulante_id: str, supabase_client) -> List[Dict[str, Any]]:
    """
    Lista todos os pedidos pendentes do ambulante em ordem FIFO
    """
    try:
        # Buscar pedidos pendentes
        response = (
            supabase_client
            .table("pedidos")
            .select("*")
            .eq("ambulante_id", ambulante_id)
            .eq("status", "pendente")
            .order("created_at", desc=False)
            .execute()
        )

        pedidos = response.data or []
        fila_formatada = []

        for idx, pedido in enumerate(pedidos, start=1):
            # Calcular tempo restante (60s - tempo decorrido)
            created_at = datetime.fromisoformat(pedido["created_at"].replace("Z", "+00:00"))
            agora = datetime.now(timezone.utc)
            tempo_decorrido = (agora - created_at).total_seconds()
            tempo_restante = max(0, 60 - int(tempo_decorrido))

            # Buscar dados do cliente
            cliente = (
                supabase_client
                .table("profiles")
                .select("name, avatar_url")
                .eq("id", pedido["cliente_id"])
                .single()
                .execute()
            )

            # Buscar nomes das categorias
            categorias_nomes = []
            if pedido.get("categorias"):
                cats = (
                    supabase_client
                    .table("catalogo")
                    .select("nome_categoria")
                    .in_("id", pedido["categorias"])
                    .execute()
                )
                categorias_nomes = [c["nome_categoria"] for c in cats.data]

            fila_formatada.append({
                "id": pedido["id"],
                "cliente_id": pedido["cliente_id"],
                "cliente_nome": cliente.data.get("name") if cliente.data else None,
                "cliente_foto": cliente.data.get("avatar_url") if cliente.data else None,
                "categorias": pedido["categorias"],
                "categorias_nomes": categorias_nomes,
                "distancia_metros": None,  # TODO: calcular distância real
                "created_at": pedido["created_at"],
                "tempo_restante_segundos": tempo_restante,
                "posicao": idx
            })

        return fila_formatada

    except Exception as e:
        raise HTTPException(500, str(e))


def aceitar_pedido(pedido_id: str, ambulante_id: str, supabase_client) -> Dict[str, Any]:
    """
    Aceita um pedido:
    1. Atualiza status para "aceito"
    2. Muda status do ambulante para "em_atendimento"
    3. Cancela todos os outros pedidos pendentes deste ambulante
    4. Envia broadcasts
    """
    try:
        # Buscar pedido
        pedido = (
            supabase_client
            .table("pedidos")
            .select("*")
            .eq("id", pedido_id)
            .eq("ambulante_id", ambulante_id)
            .single()
            .execute()
        )

        if not pedido.data:
            raise HTTPException(404, "Pedido não encontrado")

        if pedido.data["status"] != "pendente":
            raise HTTPException(400, "Pedido não está pendente")

        # Atualizar pedido para aceito
        (
            supabase_client
            .table("pedidos")
            .update({"status": "aceito"})
            .eq("id", pedido_id)
            .execute()
        )

        # Atualizar status do ambulante
        (
            supabase_client
            .table("vendor_presence")
            .update({"status": "em_atendimento"})
            .eq("vendor_id", ambulante_id)
            .execute()
        )

        # Buscar todos os outros pedidos pendentes
        outros_pedidos = (
            supabase_client
            .table("pedidos")
            .select("id, cliente_id")
            .eq("ambulante_id", ambulante_id)
            .eq("status", "pendente")
            .execute()
        )

        # Cancelar outros pedidos e coletar IDs dos clientes
        clientes_ids = []
        for p in outros_pedidos.data:
            (
                supabase_client
                .table("pedidos")
                .update({"status": "cancelado"})
                .eq("id", p["id"])
                .execute()
            )
            clientes_ids.append(p["cliente_id"])

        # Buscar nome do ambulante
        ambulante = (
            supabase_client
            .table("profiles")
            .select("name")
            .eq("id", ambulante_id)
            .single()
            .execute()
        )
        ambulante_nome = ambulante.data.get("name", "Ambulante") if ambulante.data else "Ambulante"

        # Broadcasts
        broadcast_pedido_aceito(supabase_client, pedido.data["cliente_id"], pedido_id)
        broadcast_pin_vermelho(supabase_client, ambulante_id, True)

        if clientes_ids:
            broadcast_avanco_fila(supabase_client, clientes_ids, ambulante_nome)

        return {
            "pedido_id": pedido_id,
            "message": "Pedido aceito com sucesso",
            "status": "em_atendimento"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


def negar_pedido(pedido_id: str, ambulante_id: str, supabase_client) -> Dict[str, Any]:
    """
    Nega um pedido manualmente:
    1. Atualiza status para "negado"
    2. Envia broadcast para o cliente
    3. Retorna o próximo pedido da fila (se houver)
    """
    try:
        # Buscar pedido
        pedido = (
            supabase_client
            .table("pedidos")
            .select("*")
            .eq("id", pedido_id)
            .eq("ambulante_id", ambulante_id)
            .single()
            .execute()
        )

        if not pedido.data:
            raise HTTPException(404, "Pedido não encontrado")

        if pedido.data["status"] != "pendente":
            raise HTTPException(400, "Pedido não está pendente")

        # Atualizar pedido para negado
        (
            supabase_client
            .table("pedidos")
            .update({"status": "negado"})
            .eq("id", pedido_id)
            .execute()
        )

        # Buscar nome do ambulante
        ambulante = (
            supabase_client
            .table("profiles")
            .select("name")
            .eq("id", ambulante_id)
            .single()
            .execute()
        )
        ambulante_nome = ambulante.data.get("name", "Ambulante") if ambulante.data else "Ambulante"

        # Broadcast para o cliente
        broadcast_pedido_negado(supabase_client, pedido.data["cliente_id"], pedido_id, ambulante_nome)

        # Buscar próximo pedido da fila
        fila = listar_fila_ambulante(ambulante_id, supabase_client)
        proximo_pedido = fila[0] if fila else None

        return {
            "pedido_id": pedido_id,
            "message": "Pedido negado",
            "proximo_pedido": proximo_pedido
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


def cancelar_pedido(pedido_id: str, cliente_id: str, supabase_client) -> Dict[str, Any]:
    """
    Cancela um pedido pelo cliente:
    1. Atualiza status para "cancelado"
    2. Envia broadcast para o ambulante
    """
    try:
        # Buscar pedido
        pedido = (
            supabase_client
            .table("pedidos")
            .select("*")
            .eq("id", pedido_id)
            .eq("cliente_id", cliente_id)
            .single()
            .execute()
        )

        if not pedido.data:
            raise HTTPException(404, "Pedido não encontrado")

        if pedido.data["status"] != "pendente":
            raise HTTPException(400, "Pedido não pode ser cancelado")

        # Atualizar pedido
        (
            supabase_client
            .table("pedidos")
            .update({"status": "cancelado"})
            .eq("id", pedido_id)
            .execute()
        )

        # Broadcast para o ambulante
        broadcast_pedido_cancelado(supabase_client, pedido.data["ambulante_id"], pedido_id)

        return {
            "pedido_id": pedido_id,
            "message": "Pedido cancelado com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


def expirar_pedidos_antigos(supabase_client) -> int:
    """
    Job que verifica pedidos pendentes com mais de 60s e os expira
    Retorna o número de pedidos expirados
    """
    try:
        # Buscar pedidos pendentes com mais de 60s
        limite_tempo = (datetime.now(timezone.utc) - timedelta(seconds=60)).isoformat()

        response = (
            supabase_client
            .table("pedidos")
            .select("id, cliente_id")
            .eq("status", "pendente")
            .lt("created_at", limite_tempo)
            .execute()
        )

        pedidos_expirados = response.data or []

        for pedido in pedidos_expirados:
            # Atualizar status
            (
                supabase_client
                .table("pedidos")
                .update({"status": "expirado"})
                .eq("id", pedido["id"])
                .execute()
            )

            # Broadcast para o cliente
            from app.core.realtime import broadcast_pedido_expirado
            broadcast_pedido_expirado(supabase_client, pedido["cliente_id"], pedido["id"])

        return len(pedidos_expirados)

    except Exception as e:
        print(f"Erro ao expirar pedidos: {e}")
        return 0
