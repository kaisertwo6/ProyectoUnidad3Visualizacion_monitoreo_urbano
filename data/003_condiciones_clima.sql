CREATE TABLE IF NOT EXISTS condiciones_clima (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    temperatura FLOAT NOT NULL CHECK (temperatura > -50 AND temperatura < 60),
    humedad FLOAT NOT NULL CHECK (humedad >= 0 AND humedad <= 100),
    viento FLOAT NOT NULL CHECK (viento >= 0 AND viento <= 150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
