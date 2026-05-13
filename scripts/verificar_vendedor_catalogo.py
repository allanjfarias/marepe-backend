"""
Script para verificar e criar tabela vendedor_catalogo se não existir
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Variáveis de ambiente não encontradas")
    print("Defina: SUPABASE_URL e SUPABASE_SERVICE_KEY (ou SUPABASE_KEY)")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

print("🔍 Verificando estrutura da tabela vendedor_catalogo...")
print("")

# Testar se a tabela existe
try:
    result = supabase.table("vendedor_catalogo").select("*").limit(1).execute()
    print(f"✅ Tabela vendedor_catalogo existe")
    print(f"   Total de registros: {len(result.data)}")
    if result.data:
        print(f"   Exemplo: {result.data[0]}")
except Exception as e:
    print(f"❌ Erro ao acessar tabela vendedor_catalogo: {e}")
    print("")
    print("📝 SQL para criar a tabela:")
    print("""
CREATE TABLE IF NOT EXISTS vendedor_catalogo (
    id_vendedor UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    id_categoria UUID NOT NULL REFERENCES catalogo(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id_vendedor, id_categoria)
);

-- Habilitar RLS
ALTER TABLE vendedor_catalogo ENABLE ROW LEVEL SECURITY;

-- Política: vendedor pode ler seus próprios registros
CREATE POLICY "Vendedores podem ler seu próprio catálogo"
ON vendedor_catalogo FOR SELECT
USING (auth.uid() = id_vendedor);

-- Política: vendedor pode inserir/atualizar seus próprios registros
CREATE POLICY "Vendedores podem gerenciar seu próprio catálogo"
ON vendedor_catalogo FOR ALL
USING (auth.uid() = id_vendedor);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_vendedor_catalogo_vendedor ON vendedor_catalogo(id_vendedor);
CREATE INDEX IF NOT EXISTS idx_vendedor_catalogo_categoria ON vendedor_catalogo(id_categoria);
    """)
    exit(1)

print("")
print("🔍 Verificando categorias disponíveis...")
try:
    categorias = supabase.table("catalogo").select("id, nome_categoria").eq("status_categoria", True).execute()
    print(f"✅ Total de categorias ativas: {len(categorias.data)}")
    for cat in categorias.data:
        print(f"   - {cat['nome_categoria']}: {cat['id']}")
except Exception as e:
    print(f"❌ Erro ao buscar categorias: {e}")
    exit(1)

print("")
print("🔍 Verificando registros na vendedor_catalogo...")
try:
    registros = supabase.table("vendedor_catalogo").select("*").execute()
    print(f"✅ Total de registros: {len(registros.data)}")

    if registros.data:
        # Agrupar por vendedor
        vendedores = {}
        for reg in registros.data:
            vid = reg['id_vendedor']
            if vid not in vendedores:
                vendedores[vid] = {'ativos': 0, 'inativos': 0}
            if reg['is_active']:
                vendedores[vid]['ativos'] += 1
            else:
                vendedores[vid]['inativos'] += 1

        print("")
        for vid, counts in vendedores.items():
            print(f"   Vendedor {vid[:8]}...")
            print(f"      Categorias ativas: {counts['ativos']}")
            print(f"      Categorias inativas: {counts['inativos']}")
    else:
        print("   ⚠️ Nenhum registro encontrado na tabela")

except Exception as e:
    print(f"❌ Erro ao buscar registros: {e}")
    exit(1)

print("")
print("✅ Verificação completa!")
