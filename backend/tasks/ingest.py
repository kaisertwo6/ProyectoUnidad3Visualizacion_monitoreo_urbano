import logging
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
from models.trafico import Trafico
from models.calidad_aire import CalidadAire
from models.clima import CondicionesClima
from services import fetch_clima, fetch_calidad_aire, simular_trafico

logger = logging.getLogger("monitoreo")

def ejecutar_ingesta():
    """
    Función orquestadora que se ejecuta periódicamente.
    1. Obtiene las condiciones climáticas actuales de Santiago (global).
    2. Simula tráfico y obtiene calidad del aire para cada zona (Centro, Norte, Sur).
    3. Almacena todos los registros de forma segura y transaccional en PostgreSQL.
    """
    db: Session = SessionLocal()
    timestamp_actual = datetime.now()
    
    logger.info(f"--- Iniciando ciclo de ingesta programada a las {timestamp_actual} ---")
    
    try:
        # 1. Recolectar e insertar clima global de Santiago
        clima_res = fetch_clima()
        nuevo_clima = CondicionesClima(
            timestamp=timestamp_actual,
            temperatura=clima_res["temperatura"],
            humedad=clima_res["humedad"],
            viento=clima_res["viento"]
        )
        db.add(nuevo_clima)
        logger.info("Registro de clima preparado para inserción.")

        # Zonas del sistema urbano
        zonas = ["Centro", "Norte", "Sur"]

        # 2. Recolectar tráfico y calidad del aire por zona
        for zona in zonas:
            # Tráfico
            trafico_res = simular_trafico(zona)
            nuevo_trafico = Trafico(
                timestamp=timestamp_actual,
                zona=zona,
                vehiculos=trafico_res["vehiculos"],
                velocidad_promedio=trafico_res["velocidad_promedio"]
            )
            db.add(nuevo_trafico)
            
            # Calidad de Aire
            aire_res = fetch_calidad_aire(zona)
            nueva_calidad = CalidadAire(
                timestamp=timestamp_actual,
                zona=zona,
                pm25=aire_res["pm25"],
                no2=aire_res["no2"],
                o3=aire_res["o3"]
            )
            db.add(nueva_calidad)
            logger.info(f"Registros de tráfico y calidad del aire preparados para la zona: {zona}")

        # 3. Confirmar transacción en base de datos
        db.commit()
        logger.info("Transacción de ingesta confirmada y guardada en PostgreSQL exitosamente.")

    except Exception as e:
        db.rollback()
        logger.error(f"Error crítico en el proceso de ingesta de datos. Se realizó rollback de la transacción. Detalles: {e}")
        
    finally:
        db.close()
        logger.info("Sesión de base de datos de la ingesta cerrada.")
