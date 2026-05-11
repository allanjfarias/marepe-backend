from fastapi import HTTPException
from datetime import datetime, timezone

from supabase_auth import Any, Dict, List


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
    



def get_vendedor_location(
    supabase_client,
    latitude: float,
    longitude: float,
    radius: int
) -> List[Dict[str, Any]]:

    result = supabase_client.rpc(
        "nearby_vendors",
        {
            "lat": latitude,
            "lng": longitude,
            "radius": radius
        }
    ).execute()

    rows = result.data or []

    vendors = []

    for row in rows:
        location = row.get("location")

        if location and "coordinates" in location:
            lng_val, lat_val = location["coordinates"]

            vendors.append({
                "vendor_id": row["vendor_id"],
                "status": row["status"],
                "latitude": lat_val,
                "longitude": lng_val,
                "last_seen_at": row.get("last_seen_at"),
                "created_at": row.get("created_at"),
            })

    return vendors

CATEGORIAS_DISPONIVEIS = [
    "Camarão",
    "Milho",
    "Queijo",
    "Picolé",
    "Castanha",
    "Peixes"
]

def listar_categorias():
    return CATEGORIAS_DISPONIVEIS

def get_catalogo(user_id, supabase_client):
    response = (
        supabase_client.table("vendor_catalog")
        .select("*")
        .eq("vendor_id", user_id)
        .execute()
    )

    return response.data

def salvar_catalogo(user_id, categorias, supabase_client):
    try:
        supabase_client.table("vendor_catalog")\
            .delete()\
            .eq("vendor_id", user_id)\
            .execute()

        novos_registros = [
            {
                "vendor_id": user_id,
                "categoria": categoria
            }
            for categoria in categorias
        ]

        if novos_registros:
            supabase_client.table("vendor_catalog")\
                .insert(novos_registros)\
                .execute()

        return {
            "message": "Catálogo atualizado com sucesso"
        }

    except Exception as e:
        raise HTTPException(500, str(e))