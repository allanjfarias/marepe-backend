-- Tabela de mensagens do chat entre cliente e barraqueiro
CREATE TABLE IF NOT EXISTS association_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    association_id UUID NOT NULL REFERENCES customer_associations(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('text', 'photo', 'system')),
    content TEXT, -- texto da mensagem ou URL da foto
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para busca rápida
CREATE INDEX IF NOT EXISTS idx_messages_association ON association_messages(association_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON association_messages(created_at);

-- Adicionar campos para encerramento de associação
ALTER TABLE customer_associations
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'pending_close', 'pending_payment', 'closed')),
ADD COLUMN IF NOT EXISTS charge_amount DECIMAL(10, 2) CHECK (charge_amount >= 0),
ADD COLUMN IF NOT EXISTS charge_photo_url TEXT,
ADD COLUMN IF NOT EXISTS pix_key TEXT,
ADD COLUMN IF NOT EXISTS closed_at TIMESTAMP WITH TIME ZONE;

-- Índice para busca de associações por status
CREATE INDEX IF NOT EXISTS idx_associations_status ON customer_associations(status);
