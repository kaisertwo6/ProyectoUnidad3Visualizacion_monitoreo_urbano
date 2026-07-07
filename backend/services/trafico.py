import random
import logging
from datetime import datetime

logger = logging.getLogger("monitoreo")

def simular_trafico(zona: str) -> dict:
    """
    Simula datos de tráfico realistas para una zona específica (Centro, Norte, Sur).
    La simulación considera la hora del día para recrear horas pico y horas valle,
    y aplica una variación aleatoria controlada para simular el paso del tiempo en tiempo real.
    Retorna un diccionario con: vehiculos (int) y velocidad_promedio (float).
    """
    # Configuraciones base por zona
    # El Centro tiene mayor flujo base y menor velocidad, el Sur menor flujo y mayor velocidad.
    base_settings = {
        "Centro": {"vehiculos_base": 220, "velocidad_base": 42.0},
        "Norte": {"vehiculos_base": 150, "velocidad_base": 55.0},
        "Sur": {"vehiculos_base": 100, "velocidad_base": 65.0}
    }

    settings = base_settings.get(zona, base_settings["Centro"])
    veh_base = settings["vehiculos_base"]
    vel_base = settings["velocidad_base"]

    # Lógica de hora del día
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    time_float = hour + (minute / 60.0)

    # Factores multiplicadores según horas pico
    flow_multiplier = 1.0
    speed_multiplier = 1.0

    # Hora pico mañana (07:30 - 09:30)
    if 7.5 <= time_float <= 9.5:
        flow_multiplier = 2.1 if zona == "Centro" else 1.6
        speed_multiplier = 0.45 if zona == "Centro" else 0.6
    # Hora pico tarde (17:30 - 19:30)
    elif 17.5 <= time_float <= 19.5:
        flow_multiplier = 1.9 if zona == "Centro" else 1.7
        speed_multiplier = 0.50 if zona == "Centro" else 0.65
    # Almuerzo (12:30 - 14:00)
    elif 12.5 <= time_float <= 14.0:
        flow_multiplier = 1.4
        speed_multiplier = 0.8
    # Madrugada (23:30 - 06:00)
    elif time_float >= 23.5 or time_float <= 6.0:
        flow_multiplier = 0.15
        speed_multiplier = 1.35

    # Aplicar variación aleatoria controlada (ruido de tráfico cada 10s)
    # Variación del +/- 15% sobre la cantidad de vehículos calculada
    vehiculos = int(veh_base * flow_multiplier + random.randint(-15, 15))
    vehiculos = max(5, vehiculos) # Evitar valores negativos o cero absoluto

    # Variación del +/- 10% sobre la velocidad promedio calculada
    velocidad = vel_base * speed_multiplier + random.uniform(-4.0, 4.0)
    # Restricciones físicas: velocidades no pueden ser ridículamente bajas ni superar límites
    min_speed = 10.0 if flow_multiplier > 1.5 else 25.0
    max_speed = 90.0 if zona == "Sur" else 70.0
    velocidad = max(min_speed, min(max_speed, velocidad))

    trafico_data = {
        "vehiculos": vehiculos,
        "velocidad_promedio": round(velocidad, 2)
    }

    logger.info(f"Simulación de tráfico generada para {zona}: {trafico_data}")
    return trafico_data
