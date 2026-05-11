



from app.schemas.profile import ProfileResponse


from app.schemas.profile import VendedorResponse


def get_my_profile(supabase_client, user_id: str):
    try:
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

        return ProfileResponse(
            id=data["id"],
            nome=data["nome"],
            role=data["role"],
            vendedor=(
                VendedorResponse(**vendedor)
                if vendedor else None
            )
        )


        
    except Exception as e:
        raise Exception(f"Erro ao buscar usuário: {str(e)}")