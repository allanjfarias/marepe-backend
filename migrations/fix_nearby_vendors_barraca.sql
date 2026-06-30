-- Função atualizada para incluir BARRACAS no mapa
-- Cria uma view unificada que retorna ambulantes + barracas

CREATE OR REPLACE FUNCTION nearby_vendors_with_stands(
    lat FLOAT,
    lng FLOAT,
    radius INT
)
RETURNS TABLE (
    vendor_id UUID,
    location GEOMETRY,
    status TEXT,
    last_seen_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    is_stand BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    -- Ambulantes (vendor_locations)
    SELECT
        vl.vendor_id,
        vl.location,
        COALESCE(vp.status, 'offline') as status,
        vp.last_seen_at,
        vl.created_at,
        FALSE as is_stand
    FROM vendor_locations vl
    LEFT JOIN vendor_presence vp ON vl.vendor_id = vp.vendor_id
    WHERE ST_DWithin(
        vl.location::geography,
        ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography,
        radius
    )

    UNION ALL

    -- Barracas (vendor_stands)
    SELECT
        vs.vendor_id,
        ST_SetSRID(ST_MakePoint(vs.longitude, vs.latitude), 4326) as location,
        'online' as status, -- Barracas sempre "online" (fixas)
        NOW() as last_seen_at,
        vs.created_at,
        TRUE as is_stand
    FROM vendor_stands vs
    WHERE ST_DWithin(
        ST_SetSRID(ST_MakePoint(vs.longitude, vs.latitude), 4326)::geography,
        ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography,
        radius
    );
END;
$$ LANGUAGE plpgsql STABLE;
