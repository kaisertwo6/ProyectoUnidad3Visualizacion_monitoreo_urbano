import logging
from apscheduler.schedulers.background import BackgroundScheduler
from tasks.ingest import ejecutar_ingesta

logger = logging.getLogger("monitoreo")

# Instancia global del scheduler
scheduler = BackgroundScheduler()

def start_scheduler():
    """
    Inicializa y arranca el scheduler de fondo para la ingesta periódica de datos.
    Se ejecuta cada 10 segundos.
    """
    if not scheduler.running:
        logger.info("Inicializando programador de tareas en segundo plano...")
        scheduler.add_job(
            func=ejecutar_ingesta,
            trigger="interval",
            seconds=10,
            id="ingesta_datos_urbano",
            replace_existing=True
        )
        scheduler.start()
        logger.info("Programador de tareas iniciado con éxito. Ingesta programada cada 10 segundos.")
    else:
        logger.warning("El programador de tareas ya se encuentra en ejecución.")

def stop_scheduler():
    """
    Detiene el scheduler de fondo ordenadamente.
    """
    if scheduler.running:
        logger.info("Deteniendo programador de tareas...")
        scheduler.shutdown()
        logger.info("Programador de tareas detenido ordenadamente.")
