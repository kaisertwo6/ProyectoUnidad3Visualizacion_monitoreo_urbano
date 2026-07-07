from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any

class TraficoResponse(BaseModel):
    id: int
    timestamp: datetime
    zona: str
    vehiculos: int
    velocidad_promedio: float
    congestion_level: str

    class Config:
        from_attributes = True

class CalidadAireResponse(BaseModel):
    id: int
    timestamp: datetime
    zona: str
    pm25: float
    no2: float
    o3: float
    aqi: float

    class Config:
        from_attributes = True

class ClimaResponse(BaseModel):
    id: int
    timestamp: datetime
    temperatura: float
    humedad: float
    viento: float

    class Config:
        from_attributes = True

class EstadoActualResponse(BaseModel):
    timestamp: datetime
    clima: ClimaResponse
    trafico: Dict[str, TraficoResponse]
    calidad_aire: Dict[str, CalidadAireResponse]
