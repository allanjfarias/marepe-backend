"""
Script para adicionar vendedores de teste no banco de dados.
Execute com: python scripts/add_test_vendors.py
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


def add_test_vendors():
    """
    Adiciona 3 vendedores de teste próximos à Rua Doutor João Coimbra 222, Madalena, Recife
    - 1 ambulante online
    - 1 barraca online
    - 1 ambulante em pausa
    """

    # Coordenadas próximas à Rua Doutor João Coimbra, Madalena, Recife
    test_vendors = [
        {
            "email": "ambulante.teste1@marepe.com",
            "password": "teste123",
            "nome": "João das Cocadas",
            "tipo": "ambulante",
            "latitude": -8.0540,
            "longitude": -34.9055,
            "status": "online",
            "categorias": ["Cocada", "Tapioca"]
        },
        {
            "email": "barraca.teste1@marepe.com",
            "password": "teste123",
            "nome": "Barraca da Praia",
            "tipo": "barraca",
            "latitude": -8.0545,
            "longitude": -34.9050,
            "status": "online",
            "categorias": ["Água de Coco", "Camarão"]
        },
        {
            "email": "ambulante.teste2@marepe.com",
            "password": "teste123",
            "nome": "Maria do Queijo",
            "tipo": "ambulante",
            "latitude": -8.0535,
            "longitude": -34.9060,
            "status": "paused",
            "categorias": ["Queijo Coalho"]
        }
    ]

    print("Criando vendedores de teste...\n")

    for vendor in test_vendors:
        print(f"[*] {vendor['nome']} ({vendor['tipo']}) - {vendor['status']}")

        try:
            # 1. Criar usuário no Supabase Auth
            auth_response = supabase.auth.admin.create_user({
                "email": vendor["email"],
                "password": vendor["password"],
                "email_confirm": True,
                "user_metadata": {
                    "role": vendor["tipo"].upper(),
                    "nome": vendor["nome"]
                }
            })

            user_id = auth_response.user.id
            print(f"  [OK] Usuario criado: {user_id}")

            # 2. Inserir na tabela vendedores (obrigatório para foreign key)
            vendedor_data = {
                "user_id": user_id,
                "cpf": "00000000000",
                "telefone": "(81) 99999-9999",
                "foto_url": None
            }
            if vendor["tipo"] == "barraca":
                vendedor_data["nome_barraca"] = vendor["nome"]

            supabase.table("vendedores").insert(vendedor_data).execute()
            print(f"  [OK] Vendedor registrado na tabela vendedores")

            # 3. Criar registro em vendor_presence
            supabase.table("vendor_presence").upsert({
                "vendor_id": user_id,
                "status": vendor["status"],
                "last_seen_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            print(f"  [OK] Status definido: {vendor['status']}")

            # 4. Salvar localização inicial
            point = f"SRID=4326;POINT({vendor['longitude']} {vendor['latitude']})"
            supabase.table("vendor_locations").insert({
                "vendor_id": user_id,
                "location": point,
                "accuracy": 10.0,
                "latitude": vendor["latitude"],
                "longitude": vendor["longitude"]
            }).execute()
            print(f"  [OK] Localizacao salva: {vendor['latitude']}, {vendor['longitude']}")

            # 5. Buscar IDs das categorias e salvar catálogo
            categorias_ids = []
            for cat_nome in vendor["categorias"]:
                response = supabase.table("catalogo").select("id").eq("nome_categoria", cat_nome).execute()
                if response.data:
                    categorias_ids.append(response.data[0]["id"])

            if categorias_ids:
                registros = [
                    {"id_vendedor": user_id, "id_categoria": cat_id}
                    for cat_id in categorias_ids
                ]
                supabase.table("vendedor_catalogo").insert(registros).execute()
                print(f"  [OK] Catálogo criado: {', '.join(vendor['categorias'])}")

            print(f"  [SUCESSO] {vendor['nome']} criado com sucesso!\n")

        except Exception as e:
            if "User already registered" in str(e):
                print(f"  [AVISO]  Email já existe: {vendor['email']}\n")
            else:
                print(f"  [ERRO] Erro: {str(e)}\n")

    print("[CONCLUIDO] Script finalizado!")
    print("\nCredenciais para login:")
    for vendor in test_vendors:
        print(f"  {vendor['email']} / teste123")


if __name__ == "__main__":
    add_test_vendors()
