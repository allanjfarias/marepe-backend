"""
Verifica status dos vendedores de teste
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client

SUPABASE_URL = "https://ixfpjbrfglpbnhwinrsp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4ZnBqYnJmZ2xwYm5od2lucnNwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDIxMjYxNCwiZXhwIjoyMDg5Nzg4NjE0fQ.4_AHenXqNizOrhsX5gdU0oanohUdUXmNcq3w1thHpnQ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# IDs dos vendedores de teste
joao_id = "b614209b-3259-41a0-8784-fcac674f82d7"
maria_id = "98faf772-f477-4f67-b286-75c091e57f1d"

print("=" * 60)
print("STATUS DOS VENDEDORES DE TESTE")
print("=" * 60)

for vendor_id, nome in [(joao_id, "Joao das Cocadas"), (maria_id, "Maria do Queijo")]:
    print(f"\n{nome}:")
    print("-" * 60)

    # Verificar presence
    presence = supabase.table("vendor_presence").select("*").eq("vendor_id", vendor_id).execute()
    if presence.data:
        p = presence.data[0]
        print(f"  Status: {p['status']}")
        print(f"  Last seen: {p.get('last_seen_at', 'N/A')}")
    else:
        print("  [ERRO] Nao encontrado em vendor_presence")

    # Verificar location
    location = supabase.table("vendor_locations").select("*").eq("vendor_id", vendor_id).order("created_at", desc=True).limit(1).execute()
    if location.data:
        l = location.data[0]
        print(f"  Latitude: {l['latitude']}")
        print(f"  Longitude: {l['longitude']}")
        print(f"  Accuracy: {l['accuracy']}")
    else:
        print("  [ERRO] Nao encontrado em vendor_locations")

    # Verificar catalogo
    catalogo = supabase.table("vendedor_catalogo").select("id_categoria, catalogo(nome_categoria)").eq("id_vendedor", vendor_id).execute()
    if catalogo.data:
        cats = [c['catalogo']['nome_categoria'] for c in catalogo.data if c.get('catalogo')]
        print(f"  Categorias: {', '.join(cats)}")
    else:
        print("  [AVISO] Sem categorias cadastradas")

print("\n" + "=" * 60)
print("Testando busca proxima...")
print("=" * 60)

# Testar busca nearby
result = supabase.rpc("nearby_vendors", {
    "lat": -8.0519,
    "lng": -34.9106,
    "radius": 2000
}).execute()

print(f"\nVendedores encontrados: {len(result.data)}")
for v in result.data:
    print(f"  - {v['vendor_id']}: status={v['status']}")
