from supabase_auth import Any, Dict, List
from fastapi import HTTPException
from app.core.logger import logger



def get_vitrine_vendedor(vendor_id: str, supabase_client):
    try:
        logger.info(f"Buscando vitrine para o vendedor: {vendor_id}")
        
        result = (
            supabase_client.table("catalogo")
            .select("id, nome_categoria, vendedor_catalogo(is_active)")
            .eq("status_categoria", True)
            .eq("vendedor_catalogo.id_vendedor", vendor_id)
            .execute()
        )

        vitrine = []

        for item in result.data:
            vinculo = item.get("vendedor_catalogo", [])
            is_active = False
            
            if vinculo and len(vinculo) > 0:
                is_active = vinculo[0].get("is_active", False)


            vitrine.append({
                "id": item["id"],
                "nome_categoria": item["nome_categoria"],
                "is_active": is_active
            })

        return vitrine

    except Exception as e:
        logger.error(f"Erro ao buscar vitrine: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao carregar a vitrine do vendedor")

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