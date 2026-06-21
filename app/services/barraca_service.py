from fastapi import HTTPException
from pydantic.v1 import ValidationError
from app.core.logger import logger
from app.core.upload_photo import upload_image

PHOTO_BUCKET = "vendor-media"

SIGNED_URL_TTL = 60 * 60 * 24


def get_establishment_details(
    vendor_id: str,
    customer_id: str,
    supabase_client
):
    establishment = _get_establishment(vendor_id, supabase_client)

    association_data = _get_association_status(
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
        "association_status": association_data["status"],
        "association_id": association_data.get("association_id")
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
            .select("vendor_id, association_id")
            .eq("customer_id", customer_id)
            .eq("active", True)
            .maybe_single()
            .execute()
        )

        if response is None:
            print("AVISO: Supabase retornou None na query de associações.")
            return {"status": "none", "association_id": None}


        association = response.data

        if association is None:
            return {"status": "none", "association_id": None}

        # Se chegou aqui, temos um registro válido
        if association.get("vendor_id") == vendor_id:
            return {
                "status": "this",
                "association_id": association.get("association_id")
            }

        return {"status": "other", "association_id": None}

    except Exception as e:
        print(f"ERRO CRÍTICO EM _get_association_status: {str(e)}")
        return {"status": "none", "association_id": None}


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

    return [
        item["storage_path"]
        for item in data
    ]




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


async def create_vendor_stand(
    vendor_id: str,
    latitude: float,
    longitude: float,
    establishment_photos: list,
    menu_photos: list,
    supabase_client,
):


     

    uploaded_paths = []

    if not establishment_photos:
        raise HTTPException(
            status_code=400,
            detail="Pelo menos uma foto do estabelecimento é obrigatória."
        )

    if not menu_photos:
        raise HTTPException(
            status_code=400,
            detail="Pelo menos uma foto do cardápio é obrigatória."
        )


    try:
        supabase_client.table(
            "vendor_stands"
        ).insert({
            "vendor_id": vendor_id,
            "latitude": latitude,
            "longitude": longitude
        }).execute()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar barraca: {str(e)}"
        )

    try:

        photos_to_insert = []

        for photo in establishment_photos:

            url = await upload_image(
                file=photo,
                vendor_id=vendor_id,
                folder="establishment",
                supabase_client=supabase_client
            )

            # guardar para rollback
            file_path = url.split("/vendor-media/")[-1]
            uploaded_paths.append(file_path)

            photos_to_insert.append({
                "vendor_id": vendor_id,
                "photo_type": "establishment",
                "storage_path": url
            })

        for photo in menu_photos:

            url = await upload_image(
                file=photo,
                vendor_id=vendor_id,
                folder="menu",
                supabase_client=supabase_client
            )

            file_path = url.split("/vendor-media/")[-1]
            uploaded_paths.append(file_path)

            photos_to_insert.append({
                "vendor_id": vendor_id,
                "photo_type": "menu",
                "storage_path": url
            })

        (
            supabase_client
            .table("vendor_photos")
            .insert(photos_to_insert)
            .execute()
        )

    except Exception as e:

        # remove barraca criada
        try:
            (
                supabase_client
                .table("vendor_stands")
                .delete()
                .eq("vendor_id", vendor_id)
                .execute()
            )
        except Exception:
            pass

        # remove fotos do bucket
        try:
            if uploaded_paths:
                (
                    supabase_client
                    .storage
                    .from_("vendor-media")
                    .remove(uploaded_paths)
                )
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail=f"Erro ao fazer upload das fotos: {str(e)}"
        )

    return {
        "vendor_id": vendor_id,
        "latitude": latitude,
        "longitude": longitude
    }

def get_all_vendor_stands(supabase_client) -> list:
        response = (
            supabase_client
            .table("vendor_stands")
            .select("vendor_id, latitude, longitude")
            .execute()
        )
        return response.data