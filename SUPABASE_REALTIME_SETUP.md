# Configuração do Supabase Realtime para vendor_locations

## Visão Geral

Este documento descreve como configurar o Supabase Realtime para publicar atualizações da tabela `vendor_locations` para clientes conectados em tempo real.

## Pré-requisitos

1. Acesso ao painel do Supabase (https://app.supabase.com)
2. Projeto Marepe já criado
3. Tabelas `vendedores` e `vendor_locations` criadas no banco de dados

## Estrutura das Tabelas Necessárias

### Tabela: `vendedores`

```sql
CREATE TABLE vendedores (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    telefone VARCHAR(15) NOT NULL,
    nome_barraca VARCHAR(255),
    foto_url TEXT,
    status VARCHAR(20) DEFAULT 'offline' CHECK (status IN ('online', 'offline')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para melhorar performance de consultas por status
CREATE INDEX idx_vendedores_status ON vendedores(status);
```

### Tabela: `vendor_locations`

```sql
CREATE TABLE vendor_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    accuracy DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para melhorar performance
CREATE INDEX idx_vendor_locations_user_id ON vendor_locations(user_id);
CREATE INDEX idx_vendor_locations_created_at ON vendor_locations(created_at DESC);
```

## Passo a Passo: Configuração do Realtime

### 1. Acessar o Painel do Supabase

1. Acesse: https://app.supabase.com
2. Selecione o projeto MaréPE
3. No menu lateral, clique em **Database** → **Replication**

### 2. Habilitar Realtime para a Tabela

1. Na página de **Replication**, procure pela tabela `vendor_locations`
2. Ative o toggle **Enable Realtime** para esta tabela
3. Configure as operações que serão publicadas:
   - ✅ **INSERT** (nova localização salva)
   - ✅ **UPDATE** (atualização de localização existente)
   - ✅ **DELETE** (remoção de localização)

### 3. Configurar Row Level Security (RLS)

Para garantir segurança, configure políticas de acesso:

```sql
-- Habilitar RLS
ALTER TABLE vendor_locations ENABLE ROW LEVEL SECURITY;

-- Política: Vendedores podem inserir suas próprias localizações
CREATE POLICY "Vendedores podem inserir localizações"
ON vendor_locations
FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);

-- Política: Todos usuários autenticados podem ler localizações
CREATE POLICY "Usuários podem ler localizações"
ON vendor_locations
FOR SELECT
TO authenticated
USING (true);

-- Política: Vendedores podem atualizar suas próprias localizações
CREATE POLICY "Vendedores podem atualizar suas localizações"
ON vendor_locations
FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);
```

### 4. Criar Trigger para Limpeza Automática (Opcional)

Para evitar acúmulo excessivo de dados históricos:

```sql
-- Função para deletar localizações antigas (mais de 7 dias)
CREATE OR REPLACE FUNCTION delete_old_vendor_locations()
RETURNS void AS $$
BEGIN
    DELETE FROM vendor_locations
    WHERE created_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- Criar extensão pg_cron se ainda não existir
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Agendar limpeza diária às 3h da manhã
SELECT cron.schedule(
    'delete-old-vendor-locations',
    '0 3 * * *',
    'SELECT delete_old_vendor_locations();'
);
```

### 5. Configurar RLS para a Tabela vendedores

```sql
-- Habilitar RLS
ALTER TABLE vendedores ENABLE ROW LEVEL SECURITY;

-- Política: Vendedores podem atualizar seu próprio status
CREATE POLICY "Vendedores podem atualizar status"
ON vendedores
FOR UPDATE
TO authenticated
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

-- Política: Todos podem ler informações de vendedores
CREATE POLICY "Usuários podem ler vendedores"
ON vendedores
FOR SELECT
TO authenticated
USING (true);

-- Política: Sistema pode inserir vendedores (via service_role)
CREATE POLICY "Sistema pode inserir vendedores"
ON vendedores
FOR INSERT
TO authenticated
WITH CHECK (true);
```

## Como o Frontend Deve Consumir

### Exemplo de Código para o Frontend (JavaScript/TypeScript)

```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://ixfpjbrfglpbnhwinrsp.supabase.co'
const supabaseKey = 'SUA_CHAVE_PUBLICA'
const supabase = createClient(supabaseUrl, supabaseKey)

// Configurar listener para mudanças na tabela vendor_locations
const channel = supabase
  .channel('vendor-locations-changes')
  .on(
    'postgres_changes',
    {
      event: '*', // ou 'INSERT', 'UPDATE', 'DELETE'
      schema: 'public',
      table: 'vendor_locations'
    },
    (payload) => {
      console.log('Mudança recebida:', payload)
      
      // payload.eventType: 'INSERT', 'UPDATE', ou 'DELETE'
      // payload.new: novos dados (para INSERT e UPDATE)
      // payload.old: dados antigos (para UPDATE e DELETE)
      
      if (payload.eventType === 'INSERT') {
        // Atualizar mapa com nova localização
        updateMapMarker(payload.new)
      }
    }
  )
  .subscribe()

// Limpar subscription quando não for mais necessário
// channel.unsubscribe()
```

### Filtrar Apenas Vendedores Online

```javascript
// Buscar apenas localizações de vendedores online
const { data: activeLocations } = await supabase
  .from('vendor_locations')
  .select(`
    *,
    vendedores!inner(status, nome_barraca)
  `)
  .eq('vendedores.status', 'online')
  .order('created_at', { ascending: false })

// Configurar realtime com filtro
const channel = supabase
  .channel('active-vendors')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'vendor_locations'
    },
    async (payload) => {
      // Verificar se o vendedor está online
      const { data: vendedor } = await supabase
        .from('vendedores')
        .select('status')
        .eq('user_id', payload.new.user_id)
        .single()
      
      if (vendedor?.status === 'online') {
        updateMapMarker(payload.new)
      }
    }
  )
  .subscribe()
```

## Testando a Configuração

### 1. Teste via API REST

```bash
# Atualizar status do vendedor
curl -X PUT http://localhost:8000/vendedor/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{"status": "online"}'

# Enviar localização
curl -X POST http://localhost:8000/vendedor/location \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "latitude": -8.0476,
    "longitude": -34.8770,
    "accuracy": 10.5
  }'
```

### 2. Verificar no Supabase Dashboard

1. Vá em **Database** → **Tables** → `vendor_locations`
2. Verifique se os registros estão sendo inseridos
3. Vá em **Database** → **Replication**
4. Verifique se há atividade em tempo real na tabela

### 3. Teste no Frontend

Abra o console do navegador e verifique se os eventos estão sendo recebidos quando:
- Um vendedor atualiza sua localização
- Um vendedor muda seu status

## Troubleshooting

### Problema: Realtime não está funcionando

**Solução:**
1. Verifique se o Realtime está habilitado para a tabela
2. Confirme que as políticas RLS estão corretas
3. Verifique se o token JWT está válido
4. Confira os logs no painel do Supabase

### Problema: Muitos dados sendo acumulados

**Solução:**
- Implemente a função de limpeza automática (veja seção 4)
- Ou crie uma política de retenção manual
- Considere usar uma view materializada para dados agregados

### Problema: Performance lenta

**Solução:**
- Adicione índices apropriados (já incluídos no schema acima)
- Limite a quantidade de dados retornados usando `.limit()`
- Use filtros específicos nas queries
- Considere implementar paginação

## Monitoramento

### Métricas Importantes

- Número de conexões Realtime ativas
- Taxa de inserções na tabela `vendor_locations`
- Tamanho da tabela ao longo do tempo
- Latência das atualizações Realtime

Acesse essas métricas em: **Project Settings** → **Usage**

## Considerações de Segurança

1. **Nunca exponha a service_role key no frontend**
2. **Use apenas a anon/public key no cliente**
3. **Sempre valide dados no backend antes de salvar**
4. **Implemente rate limiting para evitar spam de localizações**
5. **Considere adicionar validação de coordenadas (range válido)**

## Recursos Adicionais

- [Documentação Oficial Supabase Realtime](https://supabase.com/docs/guides/realtime)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL Replication](https://supabase.com/docs/guides/database/replication)
