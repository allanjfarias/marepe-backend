from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_user_id_from_token
from app.schemas.vendedor import (
    StatusUpdateRequest,
    StatusUpdateResponse,
    LocationRequest,
    LocationResponse,
    ToggleCategoriaRequest,
    VitrineResponse,
    CatalogoResponse,
    AtualizarCatalogoRequest
)
from app.schemas.cardapio import CardapioItem, ProdutoCreate, ProdutoUpdate
from app.services import vendedor_service
from app.services import cardapio_service
from app.core.supabase_client import get_supabase_client

router = APIRouter(tags=["Vendedor"])


@router.put("/status", response_model=StatusUpdateResponse)
async def update_status(
    data: StatusUpdateRequest,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    updated = vendedor_service.update_vendedor_status(
        user_id, data.status, supabase_client
    )

    return StatusUpdateResponse(
        user_id=updated["vendor_id"],
        status=updated["status"],
        last_seen_at=updated["last_seen_at"],
        message="Status atualizado com sucesso"
    )


@router.post("/location", response_model=LocationResponse)
async def save_location(
    data: LocationRequest,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    vendedor_service.save_vendedor_location(
        user_id=user_id,
        latitude=data.latitude,
        longitude=data.longitude,
        accuracy=data.accuracy,
        supabase_client=supabase_client
    )

    return LocationResponse(
        user_id=user_id,
        latitude=data.latitude,
        longitude=data.longitude,
        accuracy=data.accuracy,
        message="Localização salva com sucesso"
    )


@router.get("/minhas-categorias", response_model=VitrineResponse)
async def listar(
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    return vendedor_service.listar_catalogo(user_id, supabase_client)


@router.patch("/atualizar-categoria")
async def toggle(
    data: ToggleCategoriaRequest,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    return vendedor_service.toggle_catalogo(user_id, data, supabase_client)


@router.get("/catalogo", response_model=list[CatalogoResponse])
async def obter_meu_catalogo(
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
    """Retorna as categorias do vendedor logado com status ativo/inativo"""
    from app.core.logger import logger
    logger.info(f"[ROUTER-GET-CATALOGO] user_id: {user_id}")
    from app.services import vendedor_service
    result = vendedor_service.get_categorias_vendedor(user_id, supabase_client)
    logger.info(f"[ROUTER-GET-CATALOGO] Retornando {len(result)} categorias")
    return result


@router.put("/catalogo")
async def salvar_catalogo(
    data: AtualizarCatalogoRequest,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client=Depends(get_supabase_client)
):
    """Atualiza o catálogo do vendedor"""
    print(f"[ROUTER] PUT /vendedor/catalogo - user_id: {user_id}")
    print(f"[ROUTER] Categorias recebidas: {data.categorias}")
    from app.services import vendedor_service
    result = vendedor_service.atualizar_catalogo(user_id, data, supabase_client)
    print(f"[ROUTER] Resultado: {result}")
    return result


@router.get("/catalogo/categorias")
async def listar_categorias(
    supabase_client = Depends(get_supabase_client)
):
    """Lista todas as categorias disponíveis"""
    from app.services import cliente_service
    return cliente_service.listar_todas_categorias(supabase_client)


# ==================== ENDPOINTS DE PRODUTOS ====================

@router.get("/produtos", response_model=list[CardapioItem])
async def listar_meus_produtos(
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
    """Lista todos os produtos do vendedor logado"""
    try:
        response = supabase_client.table("cardapio") \
            .select("*") \
            .eq("vendedor_id", user_id) \
            .order("created_at", desc=True) \
            .execute()

        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar produtos: {str(e)}")


@router.post("/produtos", response_model=CardapioItem)
async def criar_produto(
    produto: ProdutoCreate,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
    """Cria um novo produto no cardápio do vendedor"""
    try:
        data = {
            "vendedor_id": user_id,
            "nome": produto.nome,
            "preco": float(produto.preco),
            "descricao": produto.descricao,
            "disponivel": True
        }

        # Adicionar categoria se fornecida
        if produto.categoria_id:
            data["categoria_id"] = produto.categoria_id

        response = supabase_client.table("cardapio") \
            .insert(data) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Erro ao criar produto")

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar produto: {str(e)}")


@router.put("/produtos/{produto_id}", response_model=CardapioItem)
async def atualizar_produto(
    produto_id: str,
    produto: ProdutoUpdate,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
    """Atualiza um produto existente do vendedor"""
    try:
        # Verificar se o produto pertence ao vendedor
        check = supabase_client.table("cardapio") \
            .select("*") \
            .eq("id", produto_id) \
            .eq("vendedor_id", user_id) \
            .execute()

        if not check.data:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        # Preparar dados para atualização
        data = {}
        if produto.nome is not None:
            data["nome"] = produto.nome
        if produto.preco is not None:
            data["preco"] = float(produto.preco)
        if produto.descricao is not None:
            data["descricao"] = produto.descricao
        if produto.categoria_id is not None:
            data["categoria_id"] = produto.categoria_id

        data["updated_at"] = "now()"

        # Atualizar
        response = supabase_client.table("cardapio") \
            .update(data) \
            .eq("id", produto_id) \
            .eq("vendedor_id", user_id) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Erro ao atualizar produto")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar produto: {str(e)}")


@router.delete("/produtos/{produto_id}")
async def deletar_produto(
    produto_id: str,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
    """Deleta um produto do cardápio"""
    try:
        # Verificar se o produto pertence ao vendedor
        check = supabase_client.table("cardapio") \
            .select("*") \
            .eq("id", produto_id) \
            .eq("vendedor_id", user_id) \
            .execute()

        if not check.data:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        # Deletar
        response = supabase_client.table("cardapio") \
            .delete() \
            .eq("id", produto_id) \
            .eq("vendedor_id", user_id) \
            .execute()

        return {"message": "Produto deletado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar produto: {str(e)}")


@router.patch("/produtos/{produto_id}/toggle")
async def toggle_disponibilidade(
    produto_id: str,
    user_id: str = Depends(get_user_id_from_token),
    supabase_client = Depends(get_supabase_client)
):
    """Alterna a disponibilidade de um produto (ativo/inativo)"""
    try:
        # Buscar produto atual
        check = supabase_client.table("cardapio") \
            .select("*") \
            .eq("id", produto_id) \
            .eq("vendedor_id", user_id) \
            .execute()

        if not check.data:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        produto_atual = check.data[0]
        novo_status = not produto_atual["disponivel"]

        # Atualizar
        response = supabase_client.table("cardapio") \
            .update({"disponivel": novo_status, "updated_at": "now()"}) \
            .eq("id", produto_id) \
            .eq("vendedor_id", user_id) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Erro ao atualizar disponibilidade")

        return {
            "id": produto_id,
            "disponivel": novo_status,
            "message": f"Produto {'ativado' if novo_status else 'desativado'} com sucesso"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao alterar disponibilidade: {str(e)}")
