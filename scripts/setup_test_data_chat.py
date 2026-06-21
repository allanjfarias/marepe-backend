"""
Script para configurar dados de teste para o módulo de chat.
Cria:
- 1 barraqueiro (Maria do Queijo) com fotos de estabelecimento e cardápio
- 1 cliente (João Teste)
- Maria já ativa e online

Execute com: python scripts/setup_test_data_chat.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client
from datetime import datetime, timezone

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ixfpjbrfglpbnhwinrsp.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4ZnBqYnJmZ2xwYm5od2lucnNwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDIxMjYxNCwiZXhwIjoyMDg5Nzg4NjE0fQ.4_AHenXqNizOrhsX5gdU0oanohUdUXmNcq3w1thHpnQ")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def setup_test_data():
    """Configura dados de teste para o chat"""

    print("=" * 60)
    print("CONFIGURANDO DADOS DE TESTE PARA CHAT")
    print("=" * 60)
    print()

    # URLs de fotos de exemplo do Unsplash
    fotos_estabelecimento = [
        "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800",  # Restaurante
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800",  # Interior
    ]

    fotos_cardapio = [
        "https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=800",  # Queijo coalho
        "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=800",  # Tapioca
        "https://images.unsplash.com/photo-1625943553852-781c6dd46faa?w=800",  # Água de coco
    ]

    # Coordenadas próximas (Madalena, Recife)
    # Você pode alterar para testar em outro local
    lat_barraca = -8.0545
    lng_barraca = -34.9050

    # 1. CRIAR BARRAQUEIRO: Maria do Queijo
    print("1. Criando barraqueiro: Maria do Queijo")
    print("-" * 60)

    try:
        # Criar usuário no Auth
        auth_response = supabase.auth.admin.create_user({
            "email": "maria.queijo@marepe.com",
            "password": "teste123",
            "email_confirm": True,
            "user_metadata": {
                "role": "BARRACA",
                "nome": "Maria Santos"
            }
        })

        maria_id = auth_response.user.id
        print(f"✅ Usuário criado: {maria_id}")

        # Inserir na tabela vendedores
        supabase.table("vendedores").insert({
            "user_id": maria_id,
            "cpf": "12345678900",
            "telefone": "(81) 98765-4321",
            "nome_barraca": "Barraca da Maria"
        }).execute()
        print("✅ Vendedor registrado")

        # Criar vendor_stand (localização fixa)
        supabase.table("vendor_stands").insert({
            "vendor_id": maria_id,
            "latitude": lat_barraca,
            "longitude": lng_barraca
        }).execute()
        print(f"✅ Barraca criada em: {lat_barraca}, {lng_barraca}")

        # Adicionar fotos do estabelecimento
        for i, foto_url in enumerate(fotos_estabelecimento):
            supabase.table("vendor_photos").insert({
                "vendor_id": maria_id,
                "photo_type": "establishment",
                "storage_path": foto_url
            }).execute()
        print(f"✅ {len(fotos_estabelecimento)} fotos do estabelecimento adicionadas")

        # Adicionar fotos do cardápio
        for i, foto_url in enumerate(fotos_cardapio):
            supabase.table("vendor_photos").insert({
                "vendor_id": maria_id,
                "photo_type": "menu",
                "storage_path": foto_url
            }).execute()
        print(f"✅ {len(fotos_cardapio)} fotos do cardápio adicionadas")

        # Adicionar categorias (Queijo Coalho, Tapioca)
        categorias = ["Queijo Coalho", "Tapioca", "Água de Coco"]
        for cat_nome in categorias:
            response = supabase.table("catalogo").select("id").eq("nome_categoria", cat_nome).execute()
            if response.data:
                supabase.table("vendedor_catalogo").insert({
                    "id_vendedor": maria_id,
                    "id_categoria": response.data[0]["id"]
                }).execute()
        print(f"✅ Categorias adicionadas: {', '.join(categorias)}")

        print()
        print("OK Maria do Queijo criada com sucesso!")
        print()

    except Exception as e:
        if "User already registered" in str(e):
            print("⚠️ Maria do Queijo já existe!")
            # Buscar ID existente
            user_response = supabase.auth.admin.list_users()
            for user in user_response:
                if user.email == "maria.queijo@marepe.com":
                    maria_id = user.id
                    print(f"   ID encontrado: {maria_id}")
                    break
            print()
        else:
            print(f"❌ Erro: {str(e)}")
            return

    # 2. CRIAR CLIENTE: João Teste
    print("2. Criando cliente: Joao Teste")
    print("-" * 60)

    try:
        # Criar usuário no Auth
        auth_response = supabase.auth.admin.create_user({
            "email": "joao.teste@marepe.com",
            "password": "teste123",
            "email_confirm": True,
            "user_metadata": {
                "role": "CLIENTE",
                "nome": "João Teste"
            }
        })

        joao_id = auth_response.user.id
        print(f"✅ Usuário criado: {joao_id}")
        print()
        print("OK Joao Teste criado com sucesso!")
        print()

    except Exception as e:
        if "User already registered" in str(e):
            print("⚠️ João Teste já existe!")
            user_response = supabase.auth.admin.list_users()
            for user in user_response:
                if user.email == "joao.teste@marepe.com":
                    joao_id = user.id
                    print(f"   ID encontrado: {joao_id}")
                    break
            print()
        else:
            print(f"❌ Erro: {str(e)}")
            return

    # 3. RESUMO FINAL
    print()
    print("=" * 60)
    print("✅ CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print()
    print("📋 CREDENCIAIS PARA TESTE:")
    print("-" * 60)
    print()
    print("🏪 BARRAQUEIRO (Maria do Queijo):")
    print("   Email    : maria.queijo@marepe.com")
    print("   Senha    : teste123")
    print("   Localização: -8.0545, -34.9050")
    print("   Categorias: Queijo Coalho, Tapioca, Água de Coco")
    print(f"   Fotos estabelecimento: {len(fotos_estabelecimento)}")
    print(f"   Fotos cardápio: {len(fotos_cardapio)}")
    print()
    print("👤 CLIENTE (João Teste):")
    print("   Email    : joao.teste@marepe.com")
    print("   Senha    : teste123")
    print()
    print("-" * 60)
    print()
    print("ROTEIRO DE TESTE:")
    print()
    print("1. Abra o app como CLIENTE (joao.teste@marepe.com)")
    print("2. Vá para o mapa e procure a barraca da Maria")
    print("3. Toque na barraca e clique em 'Se associar'")
    print("4. Vá para a aba 'Associar' e clique em 'Abrir Chat'")
    print("5. Teste o chat enviando mensagens")
    print("6. Alterne para 'Cardápio' para ver as fotos")
    print()
    print("7. Abra outro dispositivo/emulador como BARRAQUEIRO (maria.queijo@marepe.com)")
    print("8. Vá para a aba 'Associados'")
    print("9. Toque no João Teste")
    print("10. Envie mensagens e fotos")
    print("11. Teste o encerramento com/sem cobrança")
    print()
    print("=" * 60)


if __name__ == "__main__":
    setup_test_data()
