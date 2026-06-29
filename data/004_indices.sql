-- Para trafico: filtra por (zona, timestamp)
CREATE INDEX idx_trafico_zona_timestamp ON trafico(zona, timestamp DESC);

-- Para calidad_aire: filtra por (zona, timestamp)
CREATE INDEX idx_calidad_aire_zona_timestamp ON calidad_aire(zona, timestamp DESC);

-- Para clima: solo timestamp (no tiene zona)
CREATE INDEX idx_condiciones_clima_timestamp ON condiciones_clima(timestamp DESC);

-- Bonus: para limpiar datos antiguos (DELETE old rows)
CREATE INDEX idx_trafico_created_at ON trafico(created_at);
CREATE INDEX idx_calidad_aire_created_at ON calidad_aire(created_at);
CREATE INDEX idx_clima_created_at ON condiciones_clima(created_at);
