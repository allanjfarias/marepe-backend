"""
Helper para broadcasts via Supabase Realtime
"""
from typing import Dict, Any, List
from supabase import Client


def broadcast_pedido_criado(supabase_client: Client, ambulante_id: str, pedido_data: Dict[str, Any]):
    """
    Envia broadcast para o ambulante informando que recebeu um novo pedido
    """
    try:
        channel = supabase_client.channel(f"ambulante:{ambulante_id}")
        channel.send({
            "type": "broadcast",
            "event": "novo_pedido",
            "payload": pedido_data
        })
    except Exception as e:
        print(f"Erro ao enviar broadcast pedido_criado: {e}")


def broadcast_pedido_aceito(supabase_client: Client, cliente_id: str, pedido_id: str):
    """
    Envia broadcast para o cliente informando que o pedido foi aceito
    """
    try:
        channel = supabase_client.channel(f"cliente:{cliente_id}")
        channel.send({
            "type": "broadcast",
            "event": "pedido_aceito",
            "payload": {"pedido_id": pedido_id}
        })
    except Exception as e:
        print(f"Erro ao enviar broadcast pedido_aceito: {e}")


def broadcast_pedido_negado(supabase_client: Client, cliente_id: str, pedido_id: str, ambulante_nome: str):
    """
    Envia broadcast para o cliente informando que o pedido foi negado
    """
    try:
        channel = supabase_client.channel(f"cliente:{cliente_id}")
        channel.send({
            "type": "broadcast",
            "event": "pedido_negado",
            "payload": {
                "pedido_id": pedido_id,
                "ambulante_nome": ambulante_nome
            }
        })
    except Exception as e:
        print(f"Erro ao enviar broadcast pedido_negado: {e}")


def broadcast_pedido_cancelado(supabase_client: Client, ambulante_id: str, pedido_id: str):
    """
    Envia broadcast para o ambulante informando que o cliente cancelou o pedido
    """
    try:
        channel = supabase_client.channel(f"ambulante:{ambulante_id}")
        channel.send({
            "type": "broadcast",
            "event": "pedido_cancelado",
            "payload": {"pedido_id": pedido_id}
        })
    except Exception as e:
        print(f"Erro ao enviar broadcast pedido_cancelado: {e}")


def broadcast_pedido_expirado(supabase_client: Client, cliente_id: str, pedido_id: str):
    """
    Envia broadcast para o cliente informando que o pedido expirou (60s)
    """
    try:
        channel = supabase_client.channel(f"cliente:{cliente_id}")
        channel.send({
            "type": "broadcast",
            "event": "pedido_expirado",
            "payload": {"pedido_id": pedido_id}
        })
    except Exception as e:
        print(f"Erro ao enviar broadcast pedido_expirado: {e}")


def broadcast_avanco_fila(supabase_client: Client, clientes_ids: List[str], ambulante_nome: str):
    """
    Envia broadcast para todos os clientes na fila informando que o ambulante aceitou outro pedido
    Cancela todos os pedidos pendentes
    """
    try:
        for cliente_id in clientes_ids:
            channel = supabase_client.channel(f"cliente:{cliente_id}")
            channel.send({
                "type": "broadcast",
                "event": "avanco_fila",
                "payload": {"ambulante_nome": ambulante_nome}
            })
    except Exception as e:
        print(f"Erro ao enviar broadcast avanco_fila: {e}")


def broadcast_pin_vermelho(supabase_client: Client, ambulante_id: str, em_atendimento: bool):
    """
    Envia broadcast global para atualizar o pin do ambulante no mapa
    em_atendimento=True → pin vermelho
    em_atendimento=False → pin laranja
    """
    try:
        # Canal global para todos os clientes
        channel = supabase_client.channel("mapa_geral")
        channel.send({
            "type": "broadcast",
            "event": "pin_status_changed",
            "payload": {
                "ambulante_id": ambulante_id,
                "em_atendimento": em_atendimento
            }
        })
    except Exception as e:
        print(f"Erro ao enviar broadcast pin_vermelho: {e}")


def broadcast_nova_associacao(supabase_client: Client, vendor_id: str, customer_data: Dict[str, Any]):
    """
    Envia broadcast para o barraqueiro indicando que um novo cliente se associou
    """
    try:
        channel = supabase_client.channel(f"establishment:{vendor_id}")
        channel.send({
            "type": "broadcast",
            "event": "new_association",
            "payload": customer_data
        })
    except Exception as e:
        print(f"Erro ao enviar broadcast nova_associacao: {e}")


def broadcast_nova_mensagem(supabase_client: Client, association_id: str, message_data: Dict[str, Any]):
    """
    Envia broadcast de nova mensagem para o canal da associação
    """
    try:
        channel = supabase_client.channel(f"association:{association_id}")
        channel.send({
            "type": "broadcast",
            "event": "new_message",
            "payload": message_data
        })
    except Exception as e:
        print(f"Erro ao enviar broadcast nova_mensagem: {e}")


def broadcast_association_closed(supabase_client: Client, association_id: str, closure_data: Dict[str, Any]):
    """
    Envia broadcast quando a associação é encerrada (MAREPE-274, 275)
    """
    try:
        channel = supabase_client.channel(f"association:{association_id}")
        channel.send({
            "type": "broadcast",
            "event": "association_closed",
            "payload": closure_data
        })
    except Exception as e:
        print(f"Erro ao enviar broadcast association_closed: {e}")


def broadcast_charge_sent(supabase_client: Client, association_id: str, charge_data: Dict[str, Any]):
    """
    Envia broadcast quando o barraqueiro envia cobrança (MAREPE-307)
    """
    try:
        channel = supabase_client.channel(f"association:{association_id}")
        channel.send({
            "type": "broadcast",
            "event": "charge_sent",
            "payload": charge_data
        })
    except Exception as e:
        print(f"Erro ao enviar broadcast charge_sent: {e}")


def broadcast_payment_confirmed(supabase_client: Client, association_id: str, vendor_id: str):
    """
    Envia broadcast quando o cliente confirma o pagamento (MAREPE-297)
    """
    try:
        # Para o barraqueiro
        vendor_channel = supabase_client.channel(f"establishment:{vendor_id}")
        vendor_channel.send({
            "type": "broadcast",
            "event": "payment_confirmed",
            "payload": {"association_id": association_id}
        })

        # Para o canal da associação
        assoc_channel = supabase_client.channel(f"association:{association_id}")
        assoc_channel.send({
            "type": "broadcast",
            "event": "payment_confirmed",
            "payload": {"association_id": association_id}
        })
    except Exception as e:
        print(f"Erro ao enviar broadcast payment_confirmed: {e}")