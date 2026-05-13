"""
Cria cardapio para os vendedores de teste
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client

SUPABASE_URL = "https://ixfpjbrfglpbnhwinrsp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4ZnBqYnJmZ2xwYm5od2lucnNwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDIxMjYxNCwiZXhwIjoyMDg5Nzg4NjE0fQ.4_AHenXqNizOrhsX5gdU0oanohUdUXmNcq3w1thHpnQ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def setup_cardapio():
    # Buscar vendedores de teste
    users_response = supabase.auth.admin.list_users()

    joao_id = None
    maria_id = None

    for user in users_response:
        if user.email == "ambulante.teste1@marepe.com":
            joao_id = user.id
        elif user.email == "ambulante.teste2@marepe.com":
            maria_id = user.id

    if not joao_id or not maria_id:
        print("[ERRO] Vendedores de teste nao encontrados")
        return

    print(f"[OK] Joao: {joao_id}")
    print(f"[OK] Maria: {maria_id}")

    # Limpar cardapios existentes
    supabase.table("cardapio").delete().eq("vendedor_id", joao_id).execute()
    supabase.table("cardapio").delete().eq("vendedor_id", maria_id).execute()
    print("[OK] Cardapios antigos limpos")

    # Cardapio do Joao das Cocadas (Castanha, Milho)
    cardapio_joao = [
        {"vendedor_id": joao_id, "nome": "Castanha torrada", "preco": 5.00, "disponivel": True, "descricao": "Castanha torrada na hora"},
        {"vendedor_id": joao_id, "nome": "Milho cozido", "preco": 8.00, "disponivel": True, "descricao": "Milho verde cozido"},
        {"vendedor_id": joao_id, "nome": "Pamonha", "preco": 6.00, "disponivel": True, "descricao": "Pamonha doce"},
        {"vendedor_id": joao_id, "nome": "Canjica", "preco": 7.00, "disponivel": True, "descricao": "Canjica cremosa"},
    ]

    # Cardapio da Maria do Queijo (Queijo, Picole)
    cardapio_maria = [
        {"vendedor_id": maria_id, "nome": "Queijo coalho", "preco": 10.00, "disponivel": True, "descricao": "Queijo coalho grelhado"},
        {"vendedor_id": maria_id, "nome": "Espetinho de queijo", "preco": 8.00, "disponivel": True, "descricao": "Espetinho com queijo e oregano"},
        {"vendedor_id": maria_id, "nome": "Picole de frutas", "preco": 4.00, "disponivel": True, "descricao": "Diversos sabores"},
        {"vendedor_id": maria_id, "nome": "Picole de chocolate", "preco": 5.00, "disponivel": True, "descricao": "Chocolate cremoso"},
    ]

    # Inserir cardapios
    supabase.table("cardapio").insert(cardapio_joao).execute()
    print(f"[OK] Cardapio do Joao criado ({len(cardapio_joao)} itens)")

    supabase.table("cardapio").insert(cardapio_maria).execute()
    print(f"[OK] Cardapio da Maria criado ({len(cardapio_maria)} itens)")

    print("\n[CONCLUIDO] Cardapios prontos!")

if __name__ == "__main__":
    setup_cardapio()
