from sqlalchemy import Column, Integer, String, Float, DateTime, func
from database import Base

class CalidadAire(Base):
    __tablename__ = "calidad_aire"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    zona = Column(String(50), nullable=False, index=True)
    pm25 = Column(Float, nullable=False)
    no2 = Column(Float, nullable=False)
    o3 = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<CalidadAire(zona='{self.zona}', pm25={self.pm25}, no2={self.no2}, o3={self.o3})>"
