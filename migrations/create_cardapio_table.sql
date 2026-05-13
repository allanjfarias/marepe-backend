-- Tabela de cardapio dos vendedores
CREATE TABLE IF NOT EXISTS cardapio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendedor_id UUID NOT NULL REFERENCES vendedores(user_id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    preco DECIMAL(10, 2) NOT NULL CHECK (preco >= 0),
    disponivel BOOLEAN DEFAULT TRUE,
    descricao TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index para busca rapida por vendedor
CREATE INDEX IF NOT EXISTS idx_cardapio_vendedor ON cardapio(vendedor_id);
CREATE INDEX IF NOT EXISTS idx_cardapio_disponivel ON cardapio(disponivel);
