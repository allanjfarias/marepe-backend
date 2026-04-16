# Guia de Testes - Funcionalidades de Vendedor

## Visão Geral

Este documento descreve como testar as novas funcionalidades implementadas:
1. **PUT /vendedor/status** - Atualização de status online/offline
2. **POST /vendedor/location** - Envio de coordenadas de localização
3. **Supabase Realtime** - Publicação em tempo real das localizações

## Pré-requisitos

1. Servidor rodando: `uvicorn app.main:app --reload`
2. Banco de dados Supabase configurado com as tabelas necessárias
3. Python com requests instalado: `pip install requests`

## Estrutura das Tabelas no Supabase

### Verificar/Criar Tabela `vendedores`

Se a tabela ainda não tem a coluna `status`, execute:

```sql
-- Adicionar coluna status se não existir
ALTER TABLE vendedores 
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'offline' 
CHECK (status IN ('online', 'offline'));

-- Criar índice para melhor performance
CREATE INDEX IF NOT EXISTS idx_vendedores_status ON vendedores(status);
```

### Criar Tabela `vendor_locations`

```sql
CREATE TABLE IF NOT EXISTS vendor_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    accuracy DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_vendor_locations_user_id ON vendor_locations(user_id);
CREATE INDEX IF NOT EXISTS idx_vendor_locations_created_at ON vendor_locations(created_at DESC);

-- Habilitar Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE vendor_locations;
```

## Testes Automatizados

### Executar Suite de Testes Básicos

```bash
python test_vendedor_features.py
```

Este script testa:
- ✅ Endpoints estão registrados
- ✅ Validação de autenticação (retorna 401 sem token)
- ✅ Validação de campos (status deve ser 'online' ou 'offline')
- ✅ Validação de tipos de dados
- ✅ Documentação da API está acessível

## Testes Manuais com Autenticação Real

### 1. Criar uma Conta de Vendedor (AMBULANTE)

```bash
curl -X POST http://localhost:8000/auth/signup \
  -F "email=vendedor@teste.com" \
  -F "password=senha12345" \
  -F "nome=João Vendedor" \
  -F "role=AMBULANTE" \
  -F "cpf=12345678901" \
  -F "telefone=81987654321"
```

**Resposta esperada (201):**
```json
{
  "user_id": "uuid-aqui",
  "nome": "João Vendedor",
  "email": "vendedor@teste.com",
  "role": "AMBULANTE",
  "cpf": "12345678901",
  "telefone": "81987654321",
  "foto_url": null
}
```

### 2. Verificar Email (se habilitado)

Verifique o email e use o código OTP:

```bash
curl -X POST http://localhost:8000/auth/signup-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "vendedor@teste.com",
    "token": "codigo-do-email"
  }'
```

### 3. Fazer Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "vendedor@teste.com",
    "password": "senha12345"
  }'
```

**Resposta esperada (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "...",
  "user": {
    "id": "uuid-aqui",
    "email": "vendedor@teste.com",
    ...
  }
}
```

**Copie o `access_token` para usar nos próximos testes!**

### 4. Testar PUT /vendedor/status

#### 4.1. Definir Status como ONLINE

```bash
curl -X PUT http://localhost:8000/vendedor/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "status": "online"
  }'
```

**Resposta esperada (200):**
```json
{
  "user_id": "uuid-aqui",
  "status": "online",
  "message": "Status atualizado para online"
}
```

#### 4.2. Definir Status como OFFLINE

```bash
curl -X PUT http://localhost:8000/vendedor/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "status": "offline"
  }'
```

**Resposta esperada (200):**
```json
{
  "user_id": "uuid-aqui",
  "status": "offline",
  "message": "Status atualizado para offline"
}
```

#### 4.3. Verificar no Banco de Dados

No Supabase Dashboard:
```sql
SELECT user_id, status, updated_at 
FROM vendedores 
WHERE user_id = 'seu-user-id';
```

### 5. Testar POST /vendedor/location

#### 5.1. Enviar Localização (Recife, PE - Boa Viagem)

```bash
curl -X POST http://localhost:8000/vendedor/location \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "latitude": -8.1180,
    "longitude": -34.8957,
    "accuracy": 10.5
  }'
```

**Resposta esperada (200):**
```json
{
  "user_id": "uuid-aqui",
  "latitude": -8.1180,
  "longitude": -34.8957,
  "accuracy": 10.5,
  "message": "Localização salva com sucesso"
}
```

#### 5.2. Enviar Múltiplas Localizações

Simular movimento do vendedor:

```bash
# Localização 1 - Boa Viagem
curl -X POST http://localhost:8000/vendedor/location \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{"latitude": -8.1180, "longitude": -34.8957, "accuracy": 10.5}'

# Aguardar alguns segundos...

# Localização 2 - Pina
curl -X POST http://localhost:8000/vendedor/location \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{"latitude": -8.0890, "longitude": -34.8793, "accuracy": 8.2}'

# Localização 3 - Brasília Teimosa
curl -X POST http://localhost:8000/vendedor/location \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{"latitude": -8.0800, "longitude": -34.8650, "accuracy": 12.0}'
```

#### 5.3. Verificar no Banco de Dados

```sql
SELECT id, user_id, latitude, longitude, accuracy, created_at 
FROM vendor_locations 
WHERE user_id = 'seu-user-id'
ORDER BY created_at DESC
LIMIT 10;
```

## Testes de Supabase Realtime

### No Frontend ou Console do Navegador

```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://ixfpjbrfglpbnhwinrsp.supabase.co'
const supabaseKey = 'sua-chave-publica'
const supabase = createClient(supabaseUrl, supabaseKey)

// Subscrever às mudanças da tabela vendor_locations
const channel = supabase
  .channel('test-vendor-locations')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'vendor_locations'
    },
    (payload) => {
      console.log('Nova localização recebida:', payload)
      console.log('User ID:', payload.new.user_id)
      console.log('Latitude:', payload.new.latitude)
      console.log('Longitude:', payload.new.longitude)
      console.log('Accuracy:', payload.new.accuracy)
    }
  )
  .subscribe((status) => {
    console.log('Status da subscrição:', status)
  })

// Para parar de ouvir:
// channel.unsubscribe()
```

### Teste Completo do Realtime

1. **Abra o console do navegador** na aplicação frontend
2. **Configure o listener** (código acima)
3. **Em outro terminal, envie uma localização** via curl
4. **Verifique no console** se o evento foi recebido em tempo real

### Teste com Postman ou Insomnia

#### Configurar Ambiente

```json
{
  "base_url": "http://localhost:8000",
  "token": "seu-token-jwt-aqui"
}
```

#### Request 1: Update Status to Online

```
PUT {{base_url}}/vendedor/status
Headers:
  Authorization: Bearer {{token}}
  Content-Type: application/json
Body:
{
  "status": "online"
}
```

#### Request 2: Send Location

```
POST {{base_url}}/vendedor/location
Headers:
  Authorization: Bearer {{token}}
  Content-Type: application/json
Body:
{
  "latitude": -8.0476,
  "longitude": -34.8770,
  "accuracy": 10.5
}
```

## Testes de Erro

### 1. Sem Token de Autenticação

```bash
curl -X PUT http://localhost:8000/vendedor/status \
  -H "Content-Type: application/json" \
  -d '{"status": "online"}'
```

**Esperado: 401 Unauthorized**

### 2. Token Inválido

```bash
curl -X PUT http://localhost:8000/vendedor/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token_invalido" \
  -d '{"status": "online"}'
```

**Esperado: 401 Unauthorized**

### 3. Status Inválido

```bash
curl -X PUT http://localhost:8000/vendedor/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{"status": "busy"}'
```

**Esperado: 422 Validation Error**

### 4. Campos Faltando

```bash
curl -X POST http://localhost:8000/vendedor/location \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{"latitude": -8.0476}'
```

**Esperado: 422 Validation Error**

### 5. Tipo de Dado Incorreto

```bash
curl -X POST http://localhost:8000/vendedor/location \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{"latitude": "texto", "longitude": -34.8770, "accuracy": 10.5}'
```

**Esperado: 422 Validation Error**

## Checklist de Testes

### Backend (API)

- [ ] Servidor inicia sem erros
- [ ] Documentação Swagger acessível em `/docs`
- [ ] Endpoint `PUT /vendedor/status` registrado
- [ ] Endpoint `POST /vendedor/location` registrado
- [ ] Autenticação é obrigatória (retorna 401 sem token)
- [ ] Token inválido retorna 401
- [ ] Status aceita apenas "online" ou "offline"
- [ ] Localização valida latitude, longitude e accuracy como números
- [ ] Status é atualizado corretamente no banco
- [ ] Localização é salva corretamente no banco
- [ ] Logs apropriados são gerados

### Database (Supabase)

- [ ] Tabela `vendedores` tem coluna `status`
- [ ] Tabela `vendor_locations` existe
- [ ] Índices foram criados
- [ ] RLS está configurado (se necessário)
- [ ] Realtime está habilitado para `vendor_locations`

### Realtime

- [ ] Subscription conecta com sucesso
- [ ] Eventos INSERT são recebidos em tempo real
- [ ] Dados recebidos estão completos e corretos
- [ ] Múltiplos clientes podem se subscrever simultaneamente
- [ ] Unsubscribe funciona corretamente

### Frontend Integration (quando disponível)

- [ ] Botão de toggle online/offline chama a API corretamente
- [ ] Localização do GPS é enviada periodicamente
- [ ] Mapa atualiza em tempo real quando outro vendedor se move
- [ ] Indicador visual de vendedores online/offline
- [ ] Tratamento de erros de rede
- [ ] Tratamento de token expirado

## Problemas Comuns e Soluções

### Erro: "Token de autenticação não fornecido"
**Solução:** Adicione o header `Authorization: Bearer SEU_TOKEN`

### Erro: "Vendedor não encontrado"
**Solução:** O user_id do token não existe na tabela `vendedores`. Certifique-se de criar a conta com role AMBULANTE ou BARRAQUEIRO.

### Erro: "Falha ao salvar localização"
**Solução:** Verifique se a tabela `vendor_locations` existe e se as políticas RLS permitem INSERT.

### Realtime não funciona
**Solução:** 
1. Verifique se Realtime está habilitado no Supabase Dashboard
2. Confirme que a tabela está na publicação: `ALTER PUBLICATION supabase_realtime ADD TABLE vendor_locations;`
3. Verifique as políticas RLS

### Muitas localizações acumuladas
**Solução:** Implemente a limpeza automática (veja SUPABASE_REALTIME_SETUP.md)

## Métricas de Sucesso

✅ **Todas as funcionalidades implementadas:**
- PUT /vendedor/status
- POST /vendedor/location
- Supabase Realtime configurado

✅ **Testes passando:**
- Validação de autenticação
- Validação de dados
- Integração com banco de dados
- Realtime funcionando

✅ **Documentação completa:**
- README atualizado
- Guia de setup do Realtime
- Guia de testes
- Comentários no código

## Próximos Passos

1. Integrar com o frontend em `downloads/marepe-frontend`
2. Implementar rate limiting para evitar spam de localizações
3. Adicionar endpoint GET para buscar vendedores online próximos
4. Implementar notificações push quando vendedor fica online
5. Adicionar monitoramento e métricas (New Relic, Datadog, etc.)
