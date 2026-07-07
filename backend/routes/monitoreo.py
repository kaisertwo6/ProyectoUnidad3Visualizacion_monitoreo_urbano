from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from database import get_db
from models.trafico import Trafico
from models.calidad_aire import CalidadAire
from models.clima import CondicionesClima
from schemas.monitoreo import (
    TraficoResponse,
    CalidadAireResponse,
    ClimaResponse,
    EstadoActualResponse
)

logger = logging.getLogger("monitoreo")
router = APIRouter(prefix="/api/monitoreo", tags=["Monitoreo Urbano"])

# Lógica auxiliar para determinar nivel de congestión (replica función PL/pgSQL)
def helper_congestion(vehiculos: int) -> str:
    if vehiculos < 100:
        return "bajo"
    elif vehiculos < 300:
        return "medio"
    return "alto"

# Lógica auxiliar para calcular AQI (replica función PL/pgSQL)
def helper_aqi(pm25: float, no2: float, o3: float) -> float:
    return round((pm25 * 0.5) + (no2 * 0.3) + (o3 * 0.2), 2)

# Lógica auxiliar para determinar la fecha de inicio según rango de tiempo
def obtener_fecha_inicio(rango: str) -> datetime:
    ahora = datetime.now()
    if rango == "5m":
        return ahora - timedelta(minutes=5)
    elif rango == "1h":
        return ahora - timedelta(hours=1)
    elif rango == "24h" or rango == "1d":
        return ahora - timedelta(days=1)
    # Por defecto 24 horas si no es reconocido
    return ahora - timedelta(days=1)

@router.get("/actual", response_model=EstadoActualResponse)
def get_estado_actual(db: Session = Depends(get_db)):
    """
    Retorna el estado de monitoreo más reciente consolidado (clima global y datos por zona).
    """
    try:
        # 1. Obtener último clima
        ultimo_clima = db.query(CondicionesClima).order_by(CondicionesClima.timestamp.desc()).first()
        if not ultimo_clima:
            raise HTTPException(status_code=404, detail="No se encontraron registros de clima en la base de datos.")
        
        clima_data = ClimaResponse.model_validate(ultimo_clima)

        # Zonas a procesar
        zonas = ["Centro", "Norte", "Sur"]
        trafico_map = {}
        aire_map = {}

        for zona in zonas:
            # Obtener último tráfico de la zona
            ult_trafico = db.query(Trafico).filter(Trafico.zona == zona).order_by(Trafico.timestamp.desc()).first()
            if ult_trafico:
                trafico_map[zona] = TraficoResponse(
                    id=ult_trafico.id,
                    timestamp=ult_trafico.timestamp,
                    zona=ult_trafico.zona,
                    vehiculos=ult_trafico.vehiculos,
                    velocidad_promedio=ult_trafico.velocidad_promedio,
                    congestion_level=helper_congestion(ult_trafico.vehiculos)
                )

            # Obtener última calidad del aire de la zona
            ult_aire = db.query(CalidadAire).filter(CalidadAire.zona == zona).order_by(CalidadAire.timestamp.desc()).first()
            if ult_aire:
                aire_map[zona] = CalidadAireResponse(
                    id=ult_aire.id,
                    timestamp=ult_aire.timestamp,
                    zona=ult_aire.zona,
                    pm25=ult_aire.pm25,
                    no2=ult_aire.no2,
                    o3=ult_aire.o3,
                    aqi=helper_aqi(ult_aire.pm25, ult_aire.no2, ult_aire.o3)
                )

        # Devolver respuesta consolidada
        return EstadoActualResponse(
            timestamp=ultimo_clima.timestamp,
            clima=clima_data,
            trafico=trafico_map,
            calidad_aire=aire_map
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error recuperando estado actual: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")

@router.get("/historico/trafico", response_model=List[TraficoResponse])
def get_historico_trafico(
    zona: Optional[str] = Query(None, description="Filtro por zona (Centro, Norte, Sur)"),
    rango: str = Query("24h", description="Rango de tiempo (5m, 1h, 24h)"),
    db: Session = Depends(get_db)
):
    """
    Retorna el histórico de registros de tráfico según filtros de zona y rango de tiempo.
    """
    try:
        fecha_inicio = obtener_fecha_inicio(rango)
        query = db.query(Trafico).filter(Trafico.timestamp >= fecha_inicio)

        if zona:
            query = query.filter(Trafico.zona == zona)

        resultados = query.order_by(Trafico.timestamp.asc()).all()

        return [
            TraficoResponse(
                id=r.id,
                timestamp=r.timestamp,
                zona=r.zona,
                vehiculos=r.vehiculos,
                velocidad_promedio=r.velocidad_promedio,
                congestion_level=helper_congestion(r.vehiculos)
            )
            for r in resultados
        ]
    except Exception as e:
        logger.error(f"Error consultando histórico de tráfico: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

@router.get("/historico/calidad-aire", response_model=List[CalidadAireResponse])
def get_historico_calidad_aire(
    zona: Optional[str] = Query(None, description="Filtro por zona (Centro, Norte, Sur)"),
    rango: str = Query("24h", description="Rango de tiempo (5m, 1h, 24h)"),
    db: Session = Depends(get_db)
):
    """
    Retorna el histórico de registros de calidad del aire según filtros de zona y rango de tiempo.
    """
    try:
        fecha_inicio = obtener_fecha_inicio(rango)
        query = db.query(CalidadAire).filter(CalidadAire.timestamp >= fecha_inicio)

        if zona:
            query = query.filter(CalidadAire.zona == zona)

        resultados = query.order_by(CalidadAire.timestamp.asc()).all()

        return [
            CalidadAireResponse(
                id=r.id,
                timestamp=r.timestamp,
                zona=r.zona,
                pm25=r.pm25,
                no2=r.no2,
                o3=r.o3,
                aqi=helper_aqi(r.pm25, r.no2, r.o3)
            )
            for r in resultados
        ]
    except Exception as e:
        logger.error(f"Error consultando histórico de calidad del aire: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

@router.get("/historico/clima", response_model=List[ClimaResponse])
def get_historico_clima(
    rango: str = Query("24h", description="Rango de tiempo (5m, 1h, 24h)"),
    db: Session = Depends(get_db)
):
    """
    Retorna el histórico de condiciones climáticas de Santiago según el rango de tiempo.
    """
    try:
        fecha_inicio = obtener_fecha_inicio(rango)
        resultados = db.query(CondicionesClima).filter(
            CondicionesClima.timestamp >= fecha_inicio
        ).order_by(CondicionesClima.timestamp.asc()).all()

        return [ClimaResponse.model_validate(r) for r in resultados]
    except Exception as e:
        logger.error(f"Error consultando histórico de clima: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
