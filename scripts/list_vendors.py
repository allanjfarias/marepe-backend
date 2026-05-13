"""
Lista todos vendedores no banco
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client

SUPABASE_URL = "https://ixfpjbrfglpbnhwinrsp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml4ZnBqYnJmZ2xwYm5od2lucnNwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDIxMjYxNCwiZXhwIjoyMDg5Nzg4NjE0fQ.4_AHenXqNizOrhsX5gdU0oanohUdUXmNcq3w1thHpnQ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

vendedores = supabase.table("vendedores").select("*").execute()

print(f"\nTotal de vendedores: {len(vendedores.data)}\n")

for v in vendedores.data:
    print(f"user_id: {v['user_id']}")
    print(f"cpf: {v['cpf']}")
    print(f"telefone: {v['telefone']}")
    print(f"nome_barraca: {v.get('nome_barraca', 'N/A')}")
    print("-" * 50)
