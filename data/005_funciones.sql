CREATE OR REPLACE FUNCTION get_congestion_level(vehiculos INT)
RETURNS VARCHAR AS $$
BEGIN
    IF vehiculos < 100 THEN
        RETURN 'bajo';
    ELSIF vehiculos < 300 THEN
        RETURN 'medio';
    ELSE
        RETURN 'alto';
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION calculate_aqi(pm25 FLOAT, no2 FLOAT, o3 FLOAT)
RETURNS FLOAT AS $$
BEGIN
    RETURN ((pm25 * 0.5) + (no2 * 0.3) + (o3 * 0.2));
END;
$$ LANGUAGE plpgsql;
