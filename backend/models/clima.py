from sqlalchemy import Column, Integer, Float, DateTime, func
from database import Base

class CondicionesClima(Base):
    __tablename__ = "condiciones_clima"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    temperatura = Column(Float, nullable=False)
    humedad = Column(Float, nullable=False)
    viento = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<CondicionesClima(temp={self.temperatura}, humedad={self.humedad}, viento={self.viento})>"
