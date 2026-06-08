from fastapi import HTTPException
from app.core.logger import logger


PHOTO_BUCKET = "vendor-media"

SIGNED_URL_TTL = 60 * 60 * 24


def get_establishment_details(
    vendor_id: str,
    customer_id: str,
    supabase_client
):
    establishment = _get_establishment(vendor_id, supabase_client)

    association_status = _get_association_status(
        customer_id,
        vendor_id,
        supabase_client
    )

    return {
        "vendor_id": establishment["user_id"],
        "establishment_name": establishment["nome_barraca"],
        "owner_name": establishment["nome"],
        "establishment_photos": _get_signed_photos(vendor_id, "establishment", supabase_client),
        "menu_photos": _get_signed_photos(vendor_id, "menu", supabase_client),
        "association_status": association_status
    }


def _get_establishment(
    vendor_id: str,
    supabase_client
):
    response = (
        supabase_client
        .table("vendedores")
        .select("""
            user_id,
            nome_barraca,
            users(nome)
        """)
        .eq("user_id", vendor_id)
        .single()
        .execute()
    )
   
    establishment = response.data

    if not establishment:
        raise HTTPException(
            status_code=404,
            detail="Estabelecimento não encontrado"
        )

    return {
        "user_id": establishment["user_id"],
        "nome_barraca": establishment["nome_barraca"],
        "nome": establishment["users"]["nome"]
    }


def _get_association_status(customer_id: str, vendor_id: str, supabase_client):
    try:
        response = (
            supabase_client
            .table("customer_associations")
            .select("vendor_id")
            .eq("customer_id", customer_id)
            .eq("active", True)
            .maybe_single()
            .execute()
        )

        if response is None:
            print("AVISO: Supabase retornou None na query de associações.")
            return "none"

        
        association = response.data

        
        if association is None:
            return "none"

        # Se chegou aqui, temos um registro válido
        if association.get("vendor_id") == vendor_id:
            return "this"

        return "other"

    except Exception as e:
        print(f"ERRO CRÍTICO EM _get_association_status: {str(e)}")
        return "none"


def _get_signed_photos(vendor_id: str, photo_type: str, supabase_client):
    response = (
        supabase_client
        .table("vendor_photos")
        .select("storage_path")
        .eq("vendor_id", vendor_id)
        .eq("photo_type", photo_type)
        .execute()
    )

    data = response.data or []
    signed_urls = []

    for item in data:
        try:
            url_data = supabase_client.storage.from_(PHOTO_BUCKET).create_signed_url(
                item["storage_path"], SIGNED_URL_TTL
            )
            if url_data and "signedURL" in url_data:
                signed_urls.append(url_data["signedURL"])
        except Exception as e:
            logger.error(
                f"Erro ao gerar URL para foto {item['storage_path']}: {e}")
            continue

    return signed_urls




def get_associated_customers(vendor_id: str, supabase_client):
    response = (
        supabase_client
        .table("customer_associations")
        .select("""
            id,
            created_at,
            users:customer_id (nome)
        """)
        .eq("vendor_id", vendor_id)
        .eq("active", True)
        .order("created_at", desc=True)
        .execute()
    )
    
    data = response.data or []
    
    return [
        {
            "association_id": item["id"],
            "nome": item["users"]["nome"] if item["users"] else "Usuário",
            "horario_associacao": item["created_at"]
        }
        for item in data
    ]