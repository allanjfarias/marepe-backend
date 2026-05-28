



from app.schemas.profile import ProfileResponse, ClienteResponse


from app.schemas.profile import VendedorResponse


def get_my_profile(supabase_client, user_id: str):
    try:
        # Buscar dados do usuário
        response = (
            supabase_client
            .table("users")
            .select("""
                id,
                nome,
                role,
                vendedores (
                    cpf,
                    telefone,
                    foto_url,
                    nome_barraca
                )
            """)
            .eq("id", user_id)
            .single()
            .execute()
        )

        if not response.data:
            raise Exception("Usuário não encontrado")

        data = response.data
        vendedor = data.get("vendedores")

        # Tentar buscar dados de cliente se for CLIENTE
        cliente = None
        if data.get("role") == "CLIENTE":
            try:
                cliente_response = (
                    supabase_client
                    .table("clientes")
                    .select("cpf, telefone, foto_url")
                    .eq("user_id", user_id)
                    .single()
                    .execute()
                )
                if cliente_response.data:
                    cliente = cliente_response.data
            except Exception as e:
                # Se tabela não existe ou não tem dados, ignora
                print(f"[WARN] Não foi possível buscar dados de cliente: {e}")
                pass

        return ProfileResponse(
            id=data["id"],
            nome=data["nome"],
            role=data["role"],
            vendedor=(
                VendedorResponse(**vendedor)
                if vendedor else None
            ),
            cliente=(
                ClienteResponse(**cliente)
                if cliente else None
            )
        )




    except Exception as e:
        raise Exception(f"Erro ao buscar usuário: {str(e)}")


async def update_my_profile(supabase_client, user_id: str, nome: str = None, telefone: str = None, nome_barraca: str = None, foto=None):
    """Atualiza o perfil do usuário logado"""
    try:
        foto_url = None

        # 1. Fazer upload da foto se fornecida
        if foto:
            try:
                file_ext = foto.filename.split(".")[-1]
                file_path = f"{user_id}/profile.{file_ext}"

                file_bytes = await foto.read()
                file_bytes = bytes(file_bytes)

                upload_res = supabase_client.storage.from_("perfil").upload(
                    file_path,
                    file_bytes,
                    {
                        "content-type": foto.content_type,
                        "upsert": "true"
                    }
                )

                foto_url = supabase_client.storage.from_("perfil").get_public_url(file_path)

            except Exception as e:
                raise Exception(f"Erro ao enviar imagem: {str(e)}")

        # 2. Atualizar dados do usuário no auth (nome)
        if nome:
            try:
                supabase_client.auth.admin.update_user_by_id(
                    user_id,
                    {"user_metadata": {"nome": nome}}
                )
            except Exception as e:
                raise Exception(f"Erro ao atualizar nome: {str(e)}")

        # 3. Verificar role do usuário para atualizar tabela correta
        user_response = supabase_client.table("users").select("role").eq("id", user_id).single().execute()
        user_role = user_response.data.get("role") if user_response.data else None

        # 4. Atualizar dados na tabela vendedores ou clientes
        update_data = {}
        if telefone:
            update_data["telefone"] = telefone
        if nome_barraca:
            update_data["nome_barraca"] = nome_barraca
        if foto_url:
            update_data["foto_url"] = foto_url

        if update_data:
            try:
                if user_role == "CLIENTE":
                    # Verificar se registro existe, se não, criar
                    existing = supabase_client.table("clientes").select("user_id").eq("user_id", user_id).execute()
                    if not existing.data:
                        # Criar registro de cliente
                        supabase_client.table("clientes").insert({
                            "user_id": user_id,
                            **update_data
                        }).execute()
                    else:
                        # Atualizar registro existente
                        supabase_client.table("clientes").update(update_data).eq("user_id", user_id).execute()
                else:
                    # Atualizar vendedor (ambulante ou barraqueiro)
                    supabase_client.table("vendedores").update(update_data).eq("user_id", user_id).execute()
            except Exception as e:
                raise Exception(f"Erro ao atualizar dados do usuário: {str(e)}")

        # 5. Retornar perfil atualizado
        return get_my_profile(supabase_client, user_id)

    except Exception as e:
        raise Exception(f"Erro ao atualizar perfil: {str(e)}")