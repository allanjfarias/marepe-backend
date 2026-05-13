# 📦 Instalação - Backend Marepe

## Dependências Python

Instalar todas as dependências do `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Nota**: Foi adicionado `APScheduler==3.10.4` para o job de expiração de pedidos.

## Configuração

1. Certifique-se de que o arquivo `.env` contém:
   ```
   SUPABASE_URL=your-supabase-url
   SUPABASE_KEY=your-supabase-key
   ```

2. Criar as tabelas no Supabase:

### Tabela `pedidos`

```sql
CREATE TABLE pedidos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID NOT NULL REFERENCES profiles(id),
    ambulante_id UUID NOT NULL REFERENCES profiles(id),
    categorias TEXT[] NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pendente', 'aceito', 'negado', 'cancelado', 'expirado')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX idx_pedidos_ambulante_status ON pedidos(ambulante_id, status);
CREATE INDEX idx_pedidos_cliente_status ON pedidos(cliente_id, status);
CREATE INDEX idx_pedidos_created_at ON pedidos(created_at);
```

### Atualizar tabela `vendor_presence`

Adicionar status "em_atendimento":

```sql
ALTER TABLE vendor_presence 
DROP CONSTRAINT IF EXISTS vendor_presence_status_check;

ALTER TABLE vendor_presence 
ADD CONSTRAINT vendor_presence_status_check 
CHECK (status IN ('online', 'offline', 'paused', 'em_atendimento'));
```

## Executar

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

Documentação interativa: `http://localhost:8000/docs`

## Endpoints Criados

### Pedidos

- `POST /api/pedidos` - Criar pedido (cliente)
- `GET /api/ambulante/pedidos/fila` - Listar fila (ambulante)
- `PATCH /api/pedidos/{id}/aceitar` - Aceitar pedido (ambulante)
- `PATCH /api/pedidos/{id}/negar` - Negar pedido (ambulante)
- `DELETE /api/pedidos/{id}` - Cancelar pedido (cliente)

### Jobs automáticos

- Job de expiração de pedidos roda a cada 10 segundos
- Pedidos pendentes com mais de 60s são marcados como "expirado"
