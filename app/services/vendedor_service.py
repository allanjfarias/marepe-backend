from fastapi import HTTPException
from datetime import datetime, timezone


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
                "accuracy": accuracy
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