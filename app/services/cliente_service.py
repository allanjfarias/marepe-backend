from supabase_auth import Any, Dict, List
from fastapi import HTTPException
from app.core.logger import logger
from app.core.realtime import broadcast_nova_associacao



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

    # Tenta usar a função que inclui barracas
    try:
        result = supabase_client.rpc(
            "nearby_vendors_with_stands",
            {
                "lat": latitude,
                "lng": longitude,
                "radius": radius
            }
        ).execute()
    except Exception as e:
        # Fallback para função antiga se a nova não existir
        print(f"Usando nearby_vendors (sem barracas): {e}")
        result = supabase_client.rpc(
            "nearby_vendors",
            {
                "lat": latitude,
                "lng": longitude,
                "radius": radius
            }
        ).execute()

    rows = result.data or []

    vendor_ids = [row["vendor_id"] for row in rows if row.get("vendor_id")]

    alcance_map = {}
    if vendor_ids:
        try:
            alcance_resp = (
                supabase_client
                .table("vendedores")
                .select("user_id, alcance_km")
                .in_("user_id", vendor_ids)
                .execute()
            )
            if alcance_resp.data:
                for item in alcance_resp.data:
                    alcance_map[item["user_id"]] = item.get("alcance_km", 2)
        except Exception as e:
            print(f"[WARN] Erro ao buscar alcance_km: {e}")

    vendors = []

    for row in rows:
        location = row.get("location")

        if location and "coordinates" in location:
            lng_val, lat_val = location["coordinates"]
            vendor_id = row["vendor_id"]

            # Buscar categorias do vendedor
            categorias = []
            try:
                catalogo_response = supabase_client.table("vendedor_catalogo").select(
                    "id_categoria, catalogo(id, nome_categoria)"
                ).eq("id_vendedor", vendor_id).execute()

                if catalogo_response.data:
                    categorias = [
                        item["catalogo"]["nome_categoria"]
                        for item in catalogo_response.data
                        if item.get("catalogo")
                    ]
            except Exception as e:
                print(f"Erro ao buscar categorias para vendedor {vendor_id}: {e}")

            # Buscar nome do vendedor
            nome_vendedor = None
            try:
                # Buscar no auth.users via admin API
                users_response = supabase_client.auth.admin.list_users()
                for user in users_response:
                    if user.id == vendor_id:
                        nome_vendedor = user.user_metadata.get('nome', None)
                        break
            except Exception as e:
                print(f"Erro ao buscar nome do vendedor {vendor_id}: {e}")

            # Buscar nome da barraca se for stand
            nome_barraca = None
            if row.get("is_stand"):
                try:
                    vendedor_response = supabase_client.table("vendedores").select("nome_barraca").eq("user_id", vendor_id).single().execute()
                    nome_barraca = vendedor_response.data.get("nome_barraca") if vendedor_response.data else None
                except Exception as e:
                    print(f"Erro ao buscar nome_barraca: {e}")

            vendors.append({
                "vendor_id": vendor_id,
                "status": row["status"],
                "latitude": lat_val,
                "longitude": lng_val,
                "last_seen_at": row.get("last_seen_at"),
                "created_at": row.get("created_at"),
                "categorias": categorias,
                "nome": nome_barraca or nome_vendedor,
                "tipo": "barraca" if row.get("is_stand") else "ambulante",
                "alcance_km": alcance_map.get(vendor_id, 2) if not row.get("is_stand") else None,
            })

    return vendors


def get_catalogo_vendedor(vendor_id: str, supabase_client):
    """Retorna o catálogo (com itens do cardápio) do vendedor para o vendedor logado"""
    try:
        logger.info(f"Buscando catálogo completo para o vendedor: {vendor_id}")

        # Buscar itens do cardápio do vendedor
        result = (
            supabase_client.table("cardapio")
            .select("*")
            .eq("vendedor_id", vendor_id)
            .eq("disponivel", True)
            .execute()
        )

        return result.data

    except Exception as e:
        logger.error(f"Erro ao buscar catálogo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao carregar o catálogo")


def listar_todas_categorias(supabase_client):
    """Lista todas as categorias disponíveis no sistema"""
    try:
        result = (
            supabase_client.table("catalogo")
            .select("id, nome_categoria")
            .eq("status_categoria", True)
            .execute()
        )

        return result.data

    except Exception as e:
        logger.error(f"Erro ao listar categorias: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao carregar categorias")
    




def create_association(customer_id: str, vendor_id: str, supabase_client):
    # 1. AC04: Verificar se já existe associação ativa antes de criar
    existing_check = (
        supabase_client
        .table("customer_associations")
        .select("id")
        .eq("customer_id", customer_id)
        .eq("active", True)
        .execute()
    )

    if existing_check.data:
        raise HTTPException(
            status_code=409,
            detail="O cliente já possui uma associação ativa."
        )

    # 2. AC02: Criação do registro
    new_association = (
        supabase_client
        .table("customer_associations")
        .insert({
            "customer_id": customer_id,
            "vendor_id": vendor_id,
            "active": True
        })
        .execute()
    )
    broadcast_nova_associacao(
        supabase_client,
        vendor_id,
        {"customer_id": customer_id, "status": "ativa"}
    )

    return {"message": "Associação criada com sucesso"}


def get_client_association(customer_id: str, supabase_client):
    """Busca a associação ativa do cliente e retorna os detalhes do estabelecimento"""
    try:
        response = (
            supabase_client
            .table("customer_associations")
            .select("id, vendor_id, status, charge_amount, charge_photo_url, pix_key")
            .eq("customer_id", customer_id)
            .eq("active", True)
            .maybe_single()
            .execute()
        )

        if not response.data:
            return None

        association_id = response.data["id"]
        vendor_id = response.data["vendor_id"]
        status = response.data.get("status", "active")

        from app.services.barraca_service import _get_establishment, _get_signed_photos
        establishment = _get_establishment(vendor_id, supabase_client)

        result = {
            "association_id": association_id,
            "vendor_id": establishment["user_id"],
            "establishment_name": establishment["nome_barraca"],
            "owner_name": establishment["nome"],
            "establishment_photos": _get_signed_photos(vendor_id, "establishment", supabase_client),
            "menu_photos": _get_signed_photos(vendor_id, "menu", supabase_client),
            "association_status": "this",
            "status": status,
        }

        if status == "pending_payment":
            result.update({
                "charge_amount": response.data.get("charge_amount"),
                "charge_photo_url": response.data.get("charge_photo_url"),
                "pix_key": response.data.get("pix_key"),
            })

        return result

    except Exception as e:
        logger.error(f"Erro ao buscar associação do cliente: {str(e)}", exc_info=True)
        return None


def delete_association(customer_id: str, supabase_client):
    """Desativa a associação do cliente"""
    try:
        # Buscar associação ativa
        existing = (
            supabase_client
            .table("customer_associations")
            .select("id, vendor_id")
            .eq("customer_id", customer_id)
            .eq("active", True)
            .maybe_single()
            .execute()
        )

        if not existing.data:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma associação ativa encontrada."
            )

        # Desativar associação
        supabase_client.table("customer_associations").update({
            "active": False
        }).eq("id", existing.data["id"]).execute()

        return {"message": "Desassociado com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao desassociar cliente: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro ao desassociar"
        )