"""
Cria a tabela cardapio e popula com dados de teste
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client

SUPABASE_URL = "https://ixfpjbrfglpbnhwinrsp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4ZnBqYnJmZ2xwYm5od2lucnNwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDIxMjYxNCwiZXhwIjoyMDg5Nzg4NjE0fQ.4_AHenXqNizOrhsX5gdU0oanohUdUXmNcq3w1thHpnQ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_table():
    """Cria a tabela cardapio via SQL"""
    sql = """
    -- Tabela de cardapio dos vendedores
    CREATE TABLE IF NOT EXISTS cardapio (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        vendedor_id UUID NOT NULL REFERENCES vendedores(user_id) ON DELETE CASCADE,
        nome VARCHAR(100) NOT NULL,
        preco DECIMAL(10, 2) NOT NULL CHECK (preco >= 0),
        disponivel BOOLEAN DEFAULT TRUE,
        descricao TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Index para busca rapida por vendedor
    CREATE INDEX IF NOT EXISTS idx_cardapio_vendedor ON cardapio(vendedor_id);
    CREATE INDEX IF NOT EXISTS idx_cardapio_disponivel ON cardapio(disponivel);
    """

    try:
        # Executar via RPC ou query direta
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("[OK] Tabela cardapio criada ou ja existe")
        return True
    except Exception as e:
        # Se RPC nao existir, tentar criar a tabela testando se já existe
        print(f"[INFO] Nao foi possivel executar SQL direto: {e}")
        print("[INFO] Tentando verificar se tabela ja existe...")
        try:
            # Tenta fazer um select vazio para ver se tabela existe
            supabase.table("cardapio").select("id").limit(0).execute()
            print("[OK] Tabela cardapio ja existe")
            return True
        except Exception as e2:
            print(f"[ERRO] Tabela nao existe e nao foi possivel criar: {e2}")
            print("\n[INSTRUCAO] Execute o SQL manualmente no Supabase SQL Editor:")
            print(sql)
            return False

def populate_cardapio():
    """Popula o cardapio dos vendedores de teste"""
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
        return False

    print(f"[OK] Joao: {joao_id}")
    print(f"[OK] Maria: {maria_id}")

    # Limpar cardapios existentes
    try:
        supabase.table("cardapio").delete().eq("vendedor_id", joao_id).execute()
        supabase.table("cardapio").delete().eq("vendedor_id", maria_id).execute()
        print("[OK] Cardapios antigos limpos")
    except:
        print("[INFO] Nenhum cardapio antigo para limpar")

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
    try:
        supabase.table("cardapio").insert(cardapio_joao).execute()
        print(f"[OK] Cardapio do Joao criado ({len(cardapio_joao)} itens)")

        supabase.table("cardapio").insert(cardapio_maria).execute()
        print(f"[OK] Cardapio da Maria criado ({len(cardapio_maria)} itens)")

        return True
    except Exception as e:
        print(f"[ERRO] Falha ao inserir cardapios: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("CRIANDO TABELA E POPULANDO CARDAPIO")
    print("=" * 50)

    if create_table():
        print("\n")
        if populate_cardapio():
            print("\n[CONCLUIDO] Cardapio pronto para uso!")
        else:
            print("\n[FALHA] Erro ao popular cardapio")
    else:
        print("\n[FALHA] Execute o SQL manualmente no Supabase primeiro")
