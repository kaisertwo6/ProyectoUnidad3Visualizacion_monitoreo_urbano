import os
from dotenv import load_dotenv
import dash

# Cargar variables de entorno
load_dotenv()

# Hojas de estilo externas: FontAwesome para íconos y Google Fonts (Inter y Outfit)
external_stylesheets = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700;800&display=swap"
]

# Inicializar la aplicación Dash
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    title="Monitoreo Urbano Inteligente",
    update_title="Actualizando datos...",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)

# Exponer el servidor Flask subyacente para producción (WSGI)
server = app.server

# Asegurar que se puedan importar módulos locales desde layouts y callbacks
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar y asignar la maquetación visual (Layout)
from layouts.layout import main_layout
app.layout = main_layout

# Importar y registrar los callbacks reactivos
from callbacks.callbacks import register_callbacks
register_callbacks(app)

if __name__ == "__main__":
    debug_mode = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    app.run_server(host="0.0.0.0", port=8050, debug=debug_mode)
