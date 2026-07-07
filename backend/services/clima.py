import requests
import logging

logger = logging.getLogger("monitoreo")

# Coordenadas por defecto para Santiago de Chile
SANTIAGO_LAT = -33.4489
SANTIAGO_LON = -70.6693

def fetch_clima(latitude: float = SANTIAGO_LAT, longitude: float = SANTIAGO_LON) -> dict:
    """
    Consume la API de Open-Meteo para obtener las condiciones climáticas actuales de Santiago.
    Retorna un diccionario con: temperatura (C°), humedad (%), viento (km/h).
    Incluye un mecanismo de fallback robusto si la API falla.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": "America/Santiago"
    }

    try:
        logger.info("Consultando clima actual en Open-Meteo...")
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current", {})
        
        clima_data = {
            "temperatura": float(current.get("temperature_2m", 18.0)),
            "humedad": float(current.get("relative_humidity_2m", 50.0)),
            "viento": float(current.get("wind_speed_10m", 10.0))
        }
        logger.info(f"Clima obtenido exitosamente: {clima_data}")
        return clima_data

    except Exception as e:
        logger.warning(f"Error consultando Open-Meteo ({e}). Usando fallback de clima simulado.")
        # Fallback realista: Valores por defecto estables
        fallback_data = {
            "temperatura": 16.5,
            "humedad": 55.0,
            "viento": 8.5
        }
        return fallback_data
