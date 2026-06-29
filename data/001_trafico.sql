CREATE TABLE IF NOT EXISTS trafico (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    zona VARCHAR(50) NOT NULL,
    vehiculos INT NOT NULL CHECK (vehiculos >= 0),
    velocidad_promedio FLOAT NOT NULL CHECK (velocidad_promedio >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
