
from fastapi import HTTPException
from datetime import datetime, timezone
from app.schemas.vendedor import (CatalogoResponse)

from supabase_auth import Dict, List


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def update_vendedor_status(user_id, status, supabase_client):
    try:
        response = (
            supabase_client.table("vendor_presence")
            .update({
                "status": status,
                "last_seen_at": now_utc()
            })
            .eq("vendor_id", user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(404, "Vendedor não encontrado")

        return {
            "vendor_id": user_id,
            "status": status,
            "last_seen_at": now_utc()
        }

    except Exception as e:
        raise HTTPException(500, str(e))


def save_vendedor_location(user_id, latitude, longitude, accuracy, supabase_client):
    try:
        point = f"SRID=4326;POINT({longitude} {latitude})"

        response = (
            supabase_client.table("vendor_locations")
            .insert({
                "vendor_id": user_id,
                "location": point,
                "accuracy": accuracy,
                "latitude": latitude,
                "longitude": longitude
            })
            .execute()
        )

        if not response.data:
            raise HTTPException(500, "Falha ao salvar localização")

        supabase_client.table("vendor_presence").upsert({
            "vendor_id": user_id,
            "status": "online",
            "last_seen_at": now_utc()
        }).execute()

        return response.data[0]

    except Exception as e:
        raise HTTPException(500, str(e))
    



def salvar_catalogo(user_id, categorias, supabase_client) -> Dict[str, str]:
    try:
        response = (
            supabase_client
            .table("vendedor_catalogo")
            .select("id_categoria")
            .eq("id_vendedor", user_id)
            .execute()
        )

        categorias_atuais = {
            item["id_categoria"]
            for item in response.data
        }

        categorias_novas = {
            str(categoria)
            for categoria in categorias
        }

   
        categorias_para_inserir = (
            categorias_novas - categorias_atuais
        )

        categorias_para_remover = (
            categorias_atuais - categorias_novas
        )

        if categorias_para_remover:

            (
                supabase_client
                .table("vendedor_catalogo")
                .delete()
                .eq("id_vendedor", user_id)
                .in_(
                    "id_categoria",
                    list(categorias_para_remover)
                )
                .execute()
            )

        if categorias_para_inserir:

            registros = [
                {
                    "id_vendedor": user_id,
                    "id_categoria": categoria_id
                }
                for categoria_id in categorias_para_inserir
            ]

            (
                supabase_client
                .table("vendedor_catalogo")
                .insert(registros)
                .execute()
            )

        return {
            "message": "Catálogo atualizado com sucesso"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    


def get_categorias(supabase_client) -> List[CatalogoResponse]:
    try:
        response = (
            supabase_client
            .table("catalogo")
            .select("id, nome_categoria")
            .eq("status_categoria", True)
            .order("nome_categoria")
            .execute()
        )    
        return response.data
   
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )