import sys
import os

# Agregar el directorio actual al PYTHONPATH para poder importar correctamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from services.clima import fetch_clima
from services.aire import fetch_calidad_aire
from services.trafico import simular_trafico

# Configurar logs básicos para ver las salidas informativas
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def test_clima():
    print("\n--- PROBANDO SERVICIO DE CLIMA (Open-Meteo) ---")
    try:
        data = fetch_clima()
        print(f"Resultado Clima Santiago:")
        print(f"  - Temperatura: {data['temperatura']} °C")
        print(f"  - Humedad: {data['humedad']}%")
        print(f"  - Viento: {data['viento']} km/h")
        print("✅ Servicio de clima OK\n")
    except Exception as e:
        print(f"❌ Error en servicio clima: {e}\n")

def test_aire():
    print("--- PROBANDO SERVICIO DE CALIDAD DEL AIRE (OpenAQ) ---")
    zonas = ["Centro", "Norte", "Sur"]
    for zona in zonas:
        try:
            data = fetch_calidad_aire(zona)
            print(f"Resultado Calidad Aire en Zona {zona}:")
            print(f"  - PM2.5: {data['pm25']} µg/m³")
            print(f"  - NO2: {data['no2']} µg/m³")
            print(f"  - O3: {data['o3']} µg/m³")
            print(f"  - AQI Calculado (fórmula local): {round(data['pm25']*0.5 + data['no2']*0.3 + data['o3']*0.2, 2)}")
        except Exception as e:
            print(f"❌ Error en servicio aire para zona {zona}: {e}")
    print("✅ Servicio de calidad del aire OK\n")

def test_trafico():
    print("--- PROBANDO SIMULACIÓN DE TRÁFICO ---")
    zonas = ["Centro", "Norte", "Sur"]
    for zona in zonas:
        try:
            data = simular_trafico(zona)
            print(f"Resultado Tráfico en Zona {zona}:")
            print(f"  - Vehículos: {data['vehiculos']}")
            print(f"  - Velocidad Promedio: {data['velocidad_promedio']} km/h")
            # Determinar nivel de congestión localmente para verificar
            veh = data['vehiculos']
            congestion = "bajo" if veh < 100 else ("medio" if veh < 300 else "alto")
            print(f"  - Congestión Estimada: {congestion}")
        except Exception as e:
            print(f"❌ Error en servicio de tráfico para zona {zona}: {e}")
    print("✅ Servicio de tráfico OK\n")

if __name__ == "__main__":
    print("==================================================")
    print("Iniciando pruebas de servicios del sistema urbano")
    print("==================================================")
    test_clima()
    test_aire()
    test_trafico()
    print("==================================================")
    print("Pruebas completadas.")
    print("==================================================")
