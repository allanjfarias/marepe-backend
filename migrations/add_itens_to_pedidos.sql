-- Adiciona campos itens e valor_total na tabela pedidos

-- Adicionar coluna itens (JSONB)
ALTER TABLE pedidos
ADD COLUMN IF NOT EXISTS itens JSONB DEFAULT NULL;

-- Adicionar coluna valor_total
ALTER TABLE pedidos
ADD COLUMN IF NOT EXISTS valor_total DECIMAL(10, 2) DEFAULT NULL;

-- Adicionar index para buscas por valor_total
CREATE INDEX IF NOT EXISTS idx_pedidos_valor_total ON pedidos(valor_total);
