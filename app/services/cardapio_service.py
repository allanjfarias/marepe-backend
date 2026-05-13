from fastapi import HTTPException

def get_cardapio_vendedor(vendedor_id: str, supabase_client):
    try:
        response = supabase_client.table("cardapio").select("*").eq("vendedor_id", vendedor_id).eq("disponivel", True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar cardapio: {str(e)}")
