# ✅ Implementação de Produtos no Backend

## 📋 O Que Foi Feito

### 1. **Endpoints Criados** (`app/routers/vendedor.py`)

Todos os 5 endpoints necessários foram implementados:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/vendedor/produtos` | Lista todos os produtos do vendedor |
| POST | `/vendedor/produtos` | Cria novo produto |
| PUT | `/vendedor/produtos/{id}` | Atualiza produto existente |
| DELETE | `/vendedor/produtos/{id}` | Deleta produto |
| PATCH | `/vendedor/produtos/{id}/toggle` | Ativa/desativa produto |

### 2. **Schemas Criados** (`app/schemas/cardapio.py`)

```python
- CardapioItem: Modelo completo do produto
- ProdutoCreate: Validação para criação
- ProdutoUpdate: Validação para atualização
```

### 3. **Migração de Banco** (`migrations/add_categoria_to_cardapio.sql`)

Adiciona coluna `categoria_id` opcional à tabela `cardapio`.

---

## 🚀 Como Aplicar

### Passo 1: Aplicar Migração no Banco

**Opção A: Supabase Dashboard**
1. Acesse https://supabase.com/dashboard
2. Selecione seu projeto
3. Vá em "SQL Editor"
4. Cole e execute:

```sql
ALTER TABLE cardapio
ADD COLUMN IF NOT EXISTS categoria_id UUID
REFERENCES categorias(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_cardapio_categoria ON cardapio(categoria_id);
```

**Opção B: psql (se tiver acesso)**
```bash
cd marepe-backend
psql $DATABASE_URL < migrations/add_categoria_to_cardapio.sql
```

### Passo 2: Reiniciar o Backend

```bash
cd marepe-backend

# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate  # Windows

# Rodar servidor
python -m uvicorn app.main:app --reload --port 8000
```

### Passo 3: Testar Endpoints

```bash
# 1. Fazer login e obter token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ambulante@test.com","password":"senha123"}'

# Copiar o access_token da resposta

# 2. Criar produto
curl -X POST http://localhost:8000/vendedor/produtos \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Água de Coco Gelada",
    "preco": 5.00,
    "descricao": "Água de coco natural"
  }'

# 3. Listar produtos
curl -X GET http://localhost:8000/vendedor/produtos \
  -H "Authorization: Bearer SEU_TOKEN"

# 4. Atualizar produto
curl -X PUT http://localhost:8000/vendedor/produtos/PRODUTO_ID \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Água de Coco Premium",
    "preco": 6.00
  }'

# 5. Toggle disponibilidade
curl -X PATCH http://localhost:8000/vendedor/produtos/PRODUTO_ID/toggle \
  -H "Authorization: Bearer SEU_TOKEN"

# 6. Deletar produto
curl -X DELETE http://localhost:8000/vendedor/produtos/PRODUTO_ID \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

## 🔐 Segurança Implementada

✅ **Autenticação JWT:** Todos os endpoints requerem token válido  
✅ **Autorização:** Vendedor só acessa seus próprios produtos  
✅ **Validação:** Dados validados via Pydantic  
✅ **SQL Injection:** Protegido pelo Supabase ORM

---

## 📊 Estrutura da Tabela

```sql
cardapio
├── id (UUID, PK)
├── vendedor_id (UUID, FK → vendedores.user_id)
├── nome (VARCHAR 100, NOT NULL)
├── preco (DECIMAL 10,2, NOT NULL, CHECK > 0)
├── disponivel (BOOLEAN, DEFAULT true)
├── descricao (TEXT, NULLABLE)
├── categoria_id (UUID, FK → categorias.id) ← NOVO
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)
```

---

## ✅ Checklist de Implementação

- [x] Criar schemas Pydantic
- [x] Implementar GET /vendedor/produtos
- [x] Implementar POST /vendedor/produtos
- [x] Implementar PUT /vendedor/produtos/{id}
- [x] Implementar DELETE /vendedor/produtos/{id}
- [x] Implementar PATCH /vendedor/produtos/{id}/toggle
- [x] Criar migração para categoria_id
- [x] Adicionar validações
- [x] Garantir autenticação JWT
- [x] Verificar segurança (só próprios produtos)
- [ ] Aplicar migração no banco (MANUAL)
- [ ] Testar todos os endpoints
- [ ] Verificar integração com frontend

---

## 🧪 Exemplos de Resposta

### GET /vendedor/produtos
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "vendedor_id": "660e8400-e29b-41d4-a716-446655440000",
    "nome": "Água de Coco Gelada",
    "preco": 5.00,
    "descricao": "Água de coco natural",
    "disponivel": true,
    "categoria_id": null,
    "created_at": "2026-06-01T10:00:00Z",
    "updated_at": "2026-06-01T10:00:00Z"
  }
]
```

### POST /vendedor/produtos
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "vendedor_id": "660e8400-e29b-41d4-a716-446655440000",
  "nome": "Água de Coco Gelada",
  "preco": 5.00,
  "descricao": "Água de coco natural",
  "disponivel": true,
  "categoria_id": null,
  "created_at": "2026-06-01T10:00:00Z"
}
```

### PATCH /vendedor/produtos/{id}/toggle
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "disponivel": false,
  "message": "Produto desativado com sucesso"
}
```

---

## 🐛 Troubleshooting

### Erro: "column categoria_id does not exist"
**Solução:** Execute a migração `add_categoria_to_cardapio.sql`

### Erro 401: "Unauthorized"
**Solução:** Verifique se o token JWT está correto e não expirado

### Erro 404: "Produto não encontrado"
**Solução:** Verifique se o produto_id existe e pertence ao vendedor

### Erro 500: "Erro ao criar produto"
**Solução:** Verifique logs do backend para detalhes

---

## 📝 Notas

1. **Categoria é opcional:** Produtos podem ser criados sem categoria
2. **Soft delete:** Produtos são deletados permanentemente (considere soft delete no futuro)
3. **Preço:** Sempre maior que 0
4. **Disponibilidade:** Produtos indisponíveis não aparecem no cardápio do cliente

---

## 🔗 Arquivos Relacionados

- `app/routers/vendedor.py` - Endpoints
- `app/schemas/cardapio.py` - Schemas
- `app/services/cardapio_service.py` - Lógica (já existente)
- `migrations/create_cardapio_table.sql` - Tabela base
- `migrations/add_categoria_to_cardapio.sql` - Nova migração

---

## 🎯 Próximos Passos

1. ✅ Aplicar migração no banco
2. ✅ Reiniciar backend
3. ✅ Testar endpoints via Postman/curl
4. ✅ Testar integração com app React Native
5. ⏳ Deploy em produção
