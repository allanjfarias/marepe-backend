#!/usr/bin/env python3
"""
Script para aplicar a migração add_categoria_to_cardapio.sql
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Carregar variáveis de ambiente
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def main():
    print("🔧 Aplicando migração: add_categoria_to_cardapio")

    # Conectar ao Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Ler o SQL da migração
    migration_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "migrations",
        "add_categoria_to_cardapio.sql"
    )

    with open(migration_path, "r", encoding="utf-8") as f:
        sql = f.read()

    print(f"\n📄 SQL a ser executado:\n{sql}\n")

    try:
        # Executar SQL via RPC (Supabase não tem método direto de exec SQL)
        # Alternativa: executar diretamente no Supabase Dashboard
        print("⚠️  ATENÇÃO: Execute este SQL manualmente no Supabase Dashboard:")
        print("   1. Vá em https://supabase.com/dashboard")
        print("   2. Selecione seu projeto")
        print("   3. SQL Editor")
        print("   4. Cole e execute o SQL acima")
        print("\nOu execute via psql:")
        print(f"   psql {os.getenv('DATABASE_URL')} < migrations/add_categoria_to_cardapio.sql")

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Migração preparada! Execute manualmente no Supabase.")
    else:
        print("\n❌ Erro ao preparar migração.")
