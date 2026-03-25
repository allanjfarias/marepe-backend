import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Testando a conexão
try:
    response = supabase.table("test").select("*").limit(1).execute()
    print("Conectado com sucesso:", response.data)
except Exception as e:
    print("Erro:", e)