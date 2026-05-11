from supabase_auth import Any, Dict, List
from app.schemas.vendedor import CatalogoResponse
from fastapi import HTTPException


def get_catalogo_vendedor(
    vendor_id,
    supabase_client
) ->  List[CatalogoResponse]:
    try:

        response = (
            supabase_client
            .table("vendedor_catalogo")
            .select("""
                catalogo!inner (
                    id,
                    nome_categoria
                )
            """)
            .eq("id_vendedor", vendor_id)
            .eq("catalogo.status_categoria", True)
            .execute()
        )

        return [
            item["catalogo"]
            for item in response.data
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    

def get_vendedores_proximos(
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