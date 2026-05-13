"""
Testa se o cardápio está no banco e acessível
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client

SUPABASE_URL = "https://ixfpjbrfglpbnhwinrsp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4ZnBqYnJmZ2xwYm5od2lucnNwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDIxMjYxNCwiZXhwIjoyMDg5Nzg4NjE0fQ.4_AHenXqNizOrhsX5gdU0oanohUdUXmNcq3w1thHpnQ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

joao_id = "b614209b-3259-41a0-8784-fcac674f82d7"

print("Verificando cardápio do João das Cocadas...")
print(f"Vendor ID: {joao_id}\n")

# Buscar cardápio
cardapio = supabase.table("cardapio").select("*").eq("vendedor_id", joao_id).execute()

print(f"Itens encontrados: {len(cardapio.data)}\n")

if cardapio.data:
    for item in cardapio.data:
        print(f"  - {item['nome']}: R$ {item['preco']}")
        print(f"    Disponível: {item['disponivel']}")
        print(f"    Descrição: {item['descricao']}")
        print()
else:
    print("[ERRO] Nenhum item no cardápio!")

# Verificar nome do vendedor na tabela users
print("\nVerificando nome do vendedor...")
# Primeiro verificar se existe tabela auth.users acessível
try:
    # Tentar buscar através do metadata
    users = supabase.auth.admin.list_users()
    for user in users:
        if user.id == joao_id:
            print(f"  Nome no user_metadata: {user.user_metadata.get('nome', 'N/A')}")
            print(f"  Email: {user.email}")
            break
except Exception as e:
    print(f"  [ERRO] {e}")
