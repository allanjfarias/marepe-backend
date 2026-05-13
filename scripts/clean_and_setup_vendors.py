"""
Limpa e recria vendedores de teste
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client
from datetime import datetime, timezone

SUPABASE_URL = "https://ixfpjbrfglpbnhwinrsp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4ZnBqYnJmZ2xwYm5od2lucnNwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDIxMjYxNCwiZXhwIjoyMDg5Nzg4NjE0fQ.4_AHenXqNizOrhsX5gdU0oanohUdUXmNcq3w1thHpnQ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def setup_vendors():
    test_vendors = [
        {
            "email": "ambulante.teste1@marepe.com",
            "nome": "Joao das Cocadas",
            "tipo": "ambulante",
            "cpf": "77777777777",
            "latitude": -8.0540,
            "longitude": -34.9055,
            "status": "online",
            "categorias": ["Castanha", "Milho"]
        },
        {
            "email": "ambulante.teste2@marepe.com",
            "nome": "Maria do Queijo",
            "tipo": "ambulante",
            "cpf": "33333333333",
            "latitude": -8.0535,
            "longitude": -34.9060,
            "status": "paused",
            "categorias": ["Queijo", "Picolé"]
        }
    ]

    print("Configurando vendedores de teste...\n")

    for vendor in test_vendors:
        print(f"[*] {vendor['nome']} ({vendor['tipo']})")

        try:
            # 1. Buscar user_id
            users_response = supabase.auth.admin.list_users()
            user_id = None

            for user in users_response:
                if user.email == vendor["email"]:
                    user_id = user.id
                    break

            if not user_id:
                print(f"  [ERRO] Usuario nao encontrado\n")
                continue

            print(f"  [OK] Usuario: {user_id}")

            # 2. Limpar dados antigos
            supabase.table("vendedor_catalogo").delete().eq("id_vendedor", user_id).execute()
            supabase.table("vendor_locations").delete().eq("vendor_id", user_id).execute()
            supabase.table("vendor_presence").delete().eq("vendor_id", user_id).execute()
            supabase.table("vendedores").delete().eq("user_id", user_id).execute()
            print(f"  [OK] Dados antigos limpos")

            # 3. Inserir vendedor
            vendedor_data = {
                "user_id": user_id,
                "cpf": vendor["cpf"],
                "telefone": "(81) 99999-9999",
                "foto_url": None
            }
            supabase.table("vendedores").insert(vendedor_data).execute()
            print(f"  [OK] Vendedor criado")

            # 4. Status
            supabase.table("vendor_presence").insert({
                "vendor_id": user_id,
                "status": vendor["status"],
                "last_seen_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            print(f"  [OK] Status: {vendor['status']}")

            # 5. Localizacao
            point = f"SRID=4326;POINT({vendor['longitude']} {vendor['latitude']})"
            supabase.table("vendor_locations").insert({
                "vendor_id": user_id,
                "location": point,
                "accuracy": 10.0,
                "latitude": vendor["latitude"],
                "longitude": vendor["longitude"]
            }).execute()
            print(f"  [OK] Localizacao: {vendor['latitude']}, {vendor['longitude']}")

            # 6. Catalogo
            categorias_ids = []
            for cat_nome in vendor["categorias"]:
                response = supabase.table("catalogo").select("id").eq("nome_categoria", cat_nome).execute()
                if response.data:
                    categorias_ids.append(response.data[0]["id"])
                else:
                    print(f"  [AVISO] Categoria '{cat_nome}' nao encontrada no banco")

            if categorias_ids:
                registros = [
                    {"id_vendedor": user_id, "id_categoria": cat_id}
                    for cat_id in categorias_ids
                ]
                supabase.table("vendedor_catalogo").insert(registros).execute()
                print(f"  [OK] Catalogo: {', '.join(vendor['categorias'])}")

            print(f"  [SUCESSO] {vendor['nome']} pronto!\n")

        except Exception as e:
            print(f"  [ERRO] {str(e)}\n")

    print("[CONCLUIDO] Agora abra o app e veja os vendedores no mapa!")


if __name__ == "__main__":
    setup_vendors()
