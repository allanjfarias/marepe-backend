-- Adicionar campo categoria_id à tabela cardapio
-- ATENÇÃO: A tabela de categorias se chama 'catalogo'
ALTER TABLE cardapio
ADD COLUMN IF NOT EXISTS categoria_id UUID
REFERENCES catalogo(id) ON DELETE SET NULL;

-- Index para busca por categoria
CREATE INDEX IF NOT EXISTS idx_cardapio_categoria ON cardapio(categoria_id);

-- Comentário
COMMENT ON COLUMN cardapio.categoria_id IS 'Referência opcional à categoria do produto';
