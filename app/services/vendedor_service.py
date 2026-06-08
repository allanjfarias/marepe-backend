
from fastapi import HTTPException
from datetime import datetime, timezone
from app.core.logger import logger
from app.schemas.vendedor import ToggleCategoriaRequest, VitrineResponse



def now_utc():
    return datetime.now(timezone.utc).isoformat()


def update_vendedor_status(user_id, status, supabase_client):
    try:
        response = (
            supabase_client.table("vendor_presence")
            .upsert({
                "vendor_id": user_id,
                "status": status,
                "last_seen_at": now_utc()
            })
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

        return response.data[0]

    except Exception as e:
        raise HTTPException(500, str(e))
    

def listar_catalogo(user_id: str, supabase_client):
    try:
        logger.info(f"Iniciando busca no catálogo para o vendedor: {user_id}")

        
        result = (
            supabase_client
            .table("catalogo")
            .select("id, nome_categoria, vendedor_catalogo(id_vendedor, is_active)")
            .eq("status_categoria", True)
            .eq("vendedor_catalogo.id_vendedor", user_id)
            .execute()
        )

        # LOG FUNDAMENTAL: Verifique o console para ver o que o banco respondeu
        logger.info(f"Dados brutos recebidos do Supabase: {result.data}")

        lista_itens = []

        for item in result.data:
            vinculo = item.get("vendedor_catalogo", [])
            
            # Se a lista de vínculo vier vazia, significa que o vendedor 
            # ainda não tem um registro nessa tabela para este item.
            is_active = False
            if vinculo and len(vinculo) > 0:
                is_active = vinculo[0].get("is_active", False)

            lista_itens.append({
                "id": item["id"],
                "nome_categoria": item["nome_categoria"], # Mantido conforme seu JSON/Schema
                "is_active": is_active
            })

        logger.info(f"Total de itens processados: {len(lista_itens)}")
        return {"categorias": lista_itens}

    except Exception as e:
        logger.error(f"Erro crítico ao listar catálogo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao carregar os dados do catálogo")


def toggle_catalogo(user_id: str, data: ToggleCategoriaRequest, supabase_client):
    try:
        logger.info(f"Executando toggle para user: {user_id}, item: {data.id_categoria}, status: {data.is_active}")

        response = (
            supabase_client.table("vendedor_catalogo")
            .upsert({
                "id_vendedor": user_id,
                "id_categoria": str(data.id_categoria),
                "is_active": data.is_active
            })
            .execute()
        )

        logger.info(f"Toggle realizado com sucesso: {response.data}")
        return {"success": True}

    except Exception as e:
        logger.error(f"Erro ao realizar toggle: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao atualizar status")


def get_categorias_vendedor(user_id: str, supabase_client):
    """Retorna todas as categorias com status ativo/inativo para o vendedor"""
    try:
        print(f"[SERVICE] Buscando categorias para vendedor: {user_id}")
        logger.info(f"Buscando categorias para vendedor: {user_id}")

        # Buscar todas as categorias disponíveis
        todas_categorias = supabase_client.table("catalogo").select("id, nome_categoria").eq("status_categoria", True).execute()
        print(f"[SERVICE] Total de categorias no sistema: {len(todas_categorias.data)}")

        resultado = []

        for categoria in todas_categorias.data:
            categoria_id = categoria["id"]
            categoria_id_str = str(categoria_id)

            # Verificar se vendedor tem essa categoria e se está ativa
            vinculo = supabase_client.table("vendedor_catalogo").select("is_active").eq(
                "id_vendedor", user_id
            ).eq("id_categoria", categoria_id_str).execute()

            print(f"[SERVICE] Categoria {categoria_id_str}: vinculo={vinculo.data}")

            is_active = False
            if vinculo.data and len(vinculo.data) > 0:
                is_active = vinculo.data[0].get("is_active", False)

            resultado.append({
                "id": categoria_id,
                "nome_categoria": categoria["nome_categoria"],
                "is_active": is_active
            })

        print(f"[SERVICE] Retornando {len(resultado)} categorias, ativas: {sum(1 for r in resultado if r['is_active'])}")
        logger.info(f"Retornando {len(resultado)} categorias para vendedor {user_id}")
        return resultado

    except Exception as e:
        logger.error(f"Erro ao buscar categorias do vendedor: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao carregar categorias")


def atualizar_catalogo(user_id: str, data, supabase_client):
    """Atualiza o catálogo do vendedor com as categorias selecionadas"""
    try:
        logger.info(f"Atualizando catálogo para user: {user_id}, categorias: {data.categorias}")

        # Buscar todas as categorias disponíveis
        todas_categorias = supabase_client.table("catalogo").select("id").eq("status_categoria", True).execute()
        categorias_ids = [cat["id"] for cat in todas_categorias.data]

        logger.info(f"Categorias disponíveis no sistema: {categorias_ids}")

        # Para cada categoria disponível, criar ou atualizar o registro
        categorias_selecionadas_str = [str(c) for c in data.categorias]
        print(f"[SERVICE] Categorias selecionadas (como string): {categorias_selecionadas_str}")

        for categoria_id in categorias_ids:
            categoria_id_str = str(categoria_id)
            is_active = categoria_id_str in categorias_selecionadas_str

            print(f"[SERVICE] Processando categoria {categoria_id_str}: is_active={is_active}")
            logger.info(f"Processando categoria {categoria_id}: is_active={is_active}")

            # Verificar se já existe
            existing = supabase_client.table("vendedor_catalogo").select("*").eq(
                "id_vendedor", user_id
            ).eq("id_categoria", str(categoria_id)).execute()

            if existing.data and len(existing.data) > 0:
                # Atualizar
                print(f"[SERVICE] Atualizando categoria {categoria_id_str}: is_active={is_active}")
                supabase_client.table("vendedor_catalogo").update({
                    "is_active": is_active
                }).eq("id_vendedor", user_id).eq("id_categoria", categoria_id_str).execute()
                logger.info(f"Categoria {categoria_id} atualizada")
            else:
                # Inserir
                print(f"[SERVICE] Inserindo categoria {categoria_id_str}: is_active={is_active}")
                supabase_client.table("vendedor_catalogo").insert({
                    "id_vendedor": user_id,
                    "id_categoria": categoria_id_str,
                    "is_active": is_active
                }).execute()
                logger.info(f"Categoria {categoria_id} inserida")

        logger.info(f"Catálogo atualizado com sucesso para user {user_id}")
        return {"success": True, "message": "Catálogo atualizado com sucesso"}

    except Exception as e:
        logger.error(f"Erro ao atualizar catálogo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar catálogo: {str(e)}")