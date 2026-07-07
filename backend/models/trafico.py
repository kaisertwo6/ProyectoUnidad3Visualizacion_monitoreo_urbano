from sqlalchemy import Column, Integer, String, Float, DateTime, func
from database import Base

class Trafico(Base):
    __tablename__ = "trafico"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    zona = Column(String(50), nullable=False, index=True)
    vehiculos = Column(Integer, nullable=False)
    velocidad_promedio = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<Trafico(zona='{self.zona}', vehiculos={self.vehiculos}, velocidad={self.velocidad_promedio})>"
