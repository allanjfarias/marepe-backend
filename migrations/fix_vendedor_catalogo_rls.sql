-- Corrigir políticas RLS da tabela vendedor_catalogo
-- Execute no Supabase SQL Editor

-- 1. Remover políticas antigas se existirem
DROP POLICY IF EXISTS "Vendedores podem ler seu próprio catálogo" ON vendedor_catalogo;
DROP POLICY IF EXISTS "Vendedores podem gerenciar seu próprio catálogo" ON vendedor_catalogo;
DROP POLICY IF EXISTS "allow_all_vendedor_catalogo" ON vendedor_catalogo;

-- 2. Desabilitar RLS temporariamente para testar
-- (REMOVA ESTA LINHA EM PRODUÇÃO)
ALTER TABLE vendedor_catalogo DISABLE ROW LEVEL SECURITY;

-- OU mantenha RLS mas crie políticas permissivas:

-- 3. Reabilitar RLS
ALTER TABLE vendedor_catalogo ENABLE ROW LEVEL SECURITY;

-- 4. Política para SELECT (qualquer usuário autenticado pode ler qualquer catálogo)
CREATE POLICY "Usuários autenticados podem ler catálogos"
ON vendedor_catalogo FOR SELECT
TO authenticated
USING (true);

-- 5. Política para INSERT/UPDATE/DELETE (vendedor pode gerenciar apenas seu próprio)
CREATE POLICY "Vendedores gerenciam próprio catálogo"
ON vendedor_catalogo FOR ALL
TO authenticated
USING (auth.uid() = id_vendedor)
WITH CHECK (auth.uid() = id_vendedor);

-- 6. Verificar políticas criadas
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE tablename = 'vendedor_catalogo';
