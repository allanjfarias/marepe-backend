-- Corrige a constraint de status para incluir todos os status necessários

ALTER TABLE pedidos
DROP CONSTRAINT IF EXISTS pedidos_status_check;

ALTER TABLE pedidos
ADD CONSTRAINT pedidos_status_check
CHECK (status IN ('pendente', 'aceito', 'em_preparo', 'pronto', 'entregue', 'negado', 'cancelado', 'expirado'));
