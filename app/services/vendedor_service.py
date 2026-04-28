from fastapi import HTTPException
from app.core.logger import logger


def update_vendedor_status(user_id: str, status: str, supabase_client):
    """
    Atualiza o status (online/offline) de um vendedor
    """
    try:
        logger.info(f"[update_vendedor_status] user_id: {user_id}, status: {status}")

        response = (
            supabase_client.table("vendedores")
            .update({"status": status})
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Vendedor não encontrado")

        logger.info(f"[update_vendedor_status] Status atualizado com sucesso")
        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[update_vendedor_status] ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {str(e)}")


def save_vendedor_location(user_id: str, latitude: float, longitude: float, accuracy: float, supabase_client):
    
    try:
        logger.info(f"[save_vendedor_location] user_id: {user_id}, lat: {latitude}, lng: {longitude}, accuracy: {accuracy}")

        location_data = {
            "user_id": user_id,
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy
        }

        response = (
            supabase_client.table("vendor_locations")
            .update({'latitude': latitude, 'longitude': longitude})
            .eq("user_id", user_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=500, detail="Falha ao salvar localização")

        logger.info(f"[save_vendedor_location] Localização salva com sucesso")
        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[save_vendedor_location] ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar localização: {str(e)}")
