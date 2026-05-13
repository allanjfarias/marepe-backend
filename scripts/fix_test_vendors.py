"""
Script para completar dados dos vendedores de teste ja criados
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


def fix_vendors():
    test_vendors = [
        {
            "email": "ambulante.teste1@marepe.com",
            "nome": "Joao das Cocadas",
            "tipo": "ambulante",
            "cpf": "11111111111",
            "latitude": -8.0540,
            "longitude": -34.9055,
            "status": "online",
            "categorias": ["Cocada", "Tapioca"]
        },
        {
            "email": "barraca.teste1@marepe.com",
            "nome": "Barraca da Praia",
            "tipo": "barraca",
            "cpf": "22222222222",
            "latitude": -8.0545,
            "longitude": -34.9050,
            "status": "online",
            "categorias": ["Agua de Coco", "Camarao"]
        },
        {
            "email": "ambulante.teste2@marepe.com",
            "nome": "Maria do Queijo",
            "tipo": "ambulante",
            "cpf": "33333333333",
            "latitude": -8.0535,
            "longitude": -34.9060,
            "status": "paused",
            "categorias": ["Queijo Coalho"]
        }
    ]

    print("Atualizando vendedores de teste...\n")

    for vendor in test_vendors:
        print(f"[*] {vendor['nome']} ({vendor['tipo']})")

        try:
            # 1. Buscar user_id do Supabase Auth
            users_response = supabase.auth.admin.list_users()
            user_id = None

            for user in users_response:
                if user.email == vendor["email"]:
                    user_id = user.id
                    break

            if not user_id:
                print(f"  [ERRO] Usuario nao encontrado no auth")
                continue

            print(f"  [OK] Usuario encontrado: {user_id}")

            # 2. Inserir na tabela vendedores (se nao existir)
            vendedor_check = supabase.table("vendedores").select("user_id").eq("user_id", user_id).execute()

            if not vendedor_check.data:
                vendedor_data = {
                    "user_id": user_id,
                    "cpf": vendor["cpf"],
                    "telefone": "(81) 99999-9999",
                    "foto_url": None
                }
                if vendor["tipo"] == "barraca":
                    vendedor_data["nome_barraca"] = vendor["nome"]

                supabase.table("vendedores").insert(vendedor_data).execute()
                print(f"  [OK] Vendedor inserido na tabela vendedores")
            else:
                print(f"  [OK] Ja existe na tabela vendedores")

            # 3. Atualizar status
            supabase.table("vendor_presence").upsert({
                "vendor_id": user_id,
                "status": vendor["status"],
                "last_seen_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            print(f"  [OK] Status atualizado: {vendor['status']}")

            # 4. Salvar localizacao
            point = f"SRID=4326;POINT({vendor['longitude']} {vendor['latitude']})"
            supabase.table("vendor_locations").insert({
                "vendor_id": user_id,
                "location": point,
                "accuracy": 10.0,
                "latitude": vendor["latitude"],
                "longitude": vendor["longitude"]
            }).execute()
            print(f"  [OK] Localizacao salva: {vendor['latitude']}, {vendor['longitude']}")

            # 5. Buscar e salvar catalogo
            categorias_ids = []
            for cat_nome in vendor["categorias"]:
                response = supabase.table("catalogo").select("id").eq("nome_categoria", cat_nome).execute()
                if response.data:
                    categorias_ids.append(response.data[0]["id"])

            if categorias_ids:
                # Limpar catalogo existente
                supabase.table("vendedor_catalogo").delete().eq("id_vendedor", user_id).execute()

                # Inserir novo catalogo
                registros = [
                    {"id_vendedor": user_id, "id_categoria": cat_id}
                    for cat_id in categorias_ids
                ]
                supabase.table("vendedor_catalogo").insert(registros).execute()
                print(f"  [OK] Catalogo atualizado: {', '.join(vendor['categorias'])}")

            print(f"  [SUCESSO] {vendor['nome']} configurado!\n")

        except Exception as e:
            print(f"  [ERRO] {str(e)}\n")

    print("[CONCLUIDO] Vendedores prontos para uso!")


if __name__ == "__main__":
    fix_vendors()
