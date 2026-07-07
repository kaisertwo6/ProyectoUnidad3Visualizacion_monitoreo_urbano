import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import engine, Base
import models
from tasks import start_scheduler, stop_scheduler
from routes import monitoreo_router

# Configuración básica de logging para el backend
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("monitoreo")

# Crear tablas automáticamente en caso de que no existan
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Acciones al iniciar el servidor
    logger.info("Iniciando aplicación de monitoreo urbano...")
    start_scheduler()
    yield
    # Acciones al detener el servidor
    logger.info("Deteniendo aplicación de monitoreo urbano...")
    stop_scheduler()

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar enrutador de API
app.include_router(monitoreo_router)

@app.get("/")
def read_root():
    return {
        "message": "Sistema de Monitoreo Urbano API",
        "version": settings.API_VERSION,
        "debug": settings.DEBUG
    }

@app.get("/health")
def health():
    return {"status": "ok", "db": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
