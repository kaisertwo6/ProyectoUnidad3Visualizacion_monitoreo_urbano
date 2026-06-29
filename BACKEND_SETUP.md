# 🎯 Backend Setup Guide: API → Database → Scheduler

## Estructura de 3 Capas (3 Sprints)

```
SPRINT 1: API + Fetch Data
├── Instalar requests
├── Crear backend/apis/openmeteo.py (fetch clima)
└── Probar que trae datos reales

SPRINT 2: Conexión Database
├── Instalar psycopg2-binary + sqlalchemy
├── Crear backend/config.py (conexión)
├── Crear backend/db/manager.py (INSERT a BD)
└── Probar que inserta datos

SPRINT 3: Orquestación
├── Instalar apscheduler
├── Crear backend/main.py (scheduler)
└── Ejecutar cada 10 segundos
```

---

# SPRINT 1: API + Requests

## 📚 Documentación a leer (OBLIGATORIO ANTES DE PROGRAMAR)

### 1. **Requests Library** (30 min)
¿Qué es? Librería para hacer HTTP requests (GET, POST, etc) en Python.

**Lee esto:**
- Docs: https://requests.readthedocs.io/en/latest/
- Tutorial corto: https://realpython.com/python-requests/

**Conceptos clave a entender:**
- `requests.get(url)` → hace GET request
- `.json()` → convierte respuesta a diccionario Python
- `response.status_code` → código HTTP (200=OK, 404=Not Found)
- `.raise_for_status()` → lanza error si falla

**Ejemplo básico:**
```python
import requests

response = requests.get("https://api.open-meteo.com/v1/forecast?latitude=40&longitude=-74&current=temperature_2m")
data = response.json()
print(data['current']['temperature_2m'])  # Extrae temperatura
```

### 2. **Open-Meteo API** (Climate Data)
¿Qué es? API pública (gratis, sin autenticación) que da datos climáticos.

**Lee esto:**
- Docs: https://open-meteo.com/en/docs
- Ejemplo: https://open-meteo.com/en/docs#latitude=40.7128&longitude=-74.0060&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m

**Tu ciudad (Santiago, Chile):**
```
Coordenadas: -33.8688, -151.2093
URL: https://api.open-meteo.com/v1/forecast?latitude=-33.8688&longitude=-151.2093&current=temperature_2m,relative_humidity_2m,wind_speed_10m
```

**Response ejemplo:**
```json
{
  "current": {
    "temperature_2m": 22.5,
    "relative_humidity_2m": 65,
    "wind_speed_10m": 12.3
  }
}
```

### 3. **OpenAQ API** (Air Quality)
¿Qué es? API pública que da datos de calidad del aire (PM2.5, NO2, O3).

**Lee esto:**
- Docs: https://docs.openaq.org/
- Acceso gratuito: https://openaq.org/developers

**Tu ciudad (Santiago):**
```
URL: https://api.openaq.org/v1/latest?city=Santiago&country=CL&parameter=pm25,no2,o3
```

**Response ejemplo:**
```json
{
  "results": [
    {
      "measurements": [
        {"parameter": "pm25", "value": 45.2},
        {"parameter": "no2", "value": 32.1}
      ]
    }
  ]
}
```

---

## 🧪 ANTES DE PROGRAMAR: Contesta estas preguntas

**Pregunta 1:** ¿Cuál es la diferencia entre `response.json()` y `response.text`?
> Tu respuesta:

**Pregunta 2:** Si Open-Meteo retorna `temperature_2m: 22.5`, ¿cómo extraerías ese valor en Python?
```python
response = requests.get("...")
data = response.json()
temp = ???  # completa
```

**Pregunta 3:** ¿Por qué OpenAQ y Open-Meteo NO requieren API key?
> Tu respuesta:

---

# SPRINT 2: Conexión Database

## 📚 Documentación a leer (DESPUÉS de Sprint 1)

### 1. **psycopg2** (PostgreSQL Driver)
¿Qué es? Librería que conecta Python ↔ PostgreSQL.

**Lee esto:**
- Docs: https://www.psycopg.org/psycopg2/docs/
- Tutorial: https://www.postgresqltutorial.com/postgresql-python/connect/

**Conceptos clave:**
- `psycopg2.connect()` → abre conexión a BD
- `conn.cursor()` → prepara query
- `cursor.execute()` → ejecuta SQL
- `conn.commit()` → guarda cambios

**Ejemplo:**
```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="monitoreo",
    user="admin",
    password="pass123"
)
cursor = conn.cursor()
cursor.execute("SELECT * FROM trafico LIMIT 10")
data = cursor.fetchall()
conn.close()
```

### 2. **SQLAlchemy** (ORM - más fácil)
¿Qué es? Librería que mapea tablas SQL → objetos Python (no escribes SQL manualmente).

**Lee esto:**
- Docs: https://docs.sqlalchemy.org/
- Tutorial rápido: https://realpython.com/sqlalchemy-orm-tutorial/

**Ventaja:**
```python
# Sin SQLAlchemy (escribes SQL):
cursor.execute("INSERT INTO trafico (zona, vehiculos) VALUES (%s, %s)", ("Centro", 150))

# Con SQLAlchemy (usas objetos Python):
session.add(Trafico(zona="Centro", vehiculos=150))
session.commit()
```

**Para este proyecto usaremos SQLAlchemy.**

---

# SPRINT 3: APScheduler

## 📚 Documentación a leer (DESPUÉS de Sprint 2)

### 1. **APScheduler** (Task Scheduler)
¿Qué es? Librería que ejecuta funciones Python en intervalos (cada 10 seg, cada hora, etc).

**Lee esto:**
- Docs: https://apscheduler.readthedocs.io/en/3.10.4/
- Tutorial: https://realpython.com/intro-to-python-threading/

**Conceptos clave:**
- `BackgroundScheduler()` → crea scheduler
- `.add_job(func, trigger, seconds=10)` → agrega tarea
- `.start()` → inicia el scheduler

**Ejemplo:**
```python
from apscheduler.schedulers.background import BackgroundScheduler

def fetch_and_insert():
    print("Ejecutando cada 10 segundos...")
    # aquí va lógica de APIs + INSERT

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_insert, 'interval', seconds=10)
scheduler.start()

# El scheduler corre en background
# Tu código principal continúa normalmente
```

---

# 🛠️ Requirements.txt Explicado

Una vez hayas entendido la documentación, vamos a crear:

```
requirements.txt:
├── requests==2.31.0           # HTTP requests (APIs)
├── psycopg2-binary==2.9.9    # PostgreSQL driver
├── sqlalchemy==2.0.23        # ORM (mapear tablas → objetos)
├── apscheduler==3.10.4       # Scheduler (tareas periódicas)
├── pandas==2.1.1             # Data transformation
├── python-dotenv==1.0.0      # Lee .env
└── pydantic==2.4.2           # Validación de datos
```

**¿Por qué cada una?**

| Librería | Para qué | Cuándo la usas |
|----------|----------|---|
| `requests` | Fetch de APIs externas | En `backend/apis/` |
| `psycopg2-binary` | Driver PostgreSQL | En `backend/db/manager.py` |
| `sqlalchemy` | ORM para BD | En `backend/db/manager.py` |
| `apscheduler` | Scheduler (cada 10s) | En `backend/main.py` |
| `pandas` | Transformar JSON → DataFrame → Insert | En `backend/main.py` |
| `python-dotenv` | Leer variables de `.env` | En `backend/config.py` |
| `pydantic` | Validar datos (opcional pero recomendado) | En `backend/` |

---

# ✅ Tu próximo paso

**Una vez hayas:**
1. ✅ Leído toda la documentación
2. ✅ Respondido las 3 preguntas de Sprint 1
3. ✅ Entendido cómo funcionan requests + APIs

**Entonces:**
- Creas un **venv** (virtual environment)
- Instalas las librerías
- Comienzas a programar `backend/apis/openmeteo.py`

---

# 🚀 Comando para crear venv e instalar librerías (YA LISTO)

Cuando termines de leer, ejecuta:

```bash
cd /home/kaisertwo/Documentos/git/u/monitoreo_urbano

# Crear virtual environment
python3 -m venv venv

# Activar
source venv/bin/activate

# Instalar librerías (cuando tengas requirements.txt)
pip install -r backend/requirements.txt
```

---

**⚠️ NO CONTINÚES HASTA QUE:**
1. Hayas leído toda la documentación
2. Hayas respondido las preguntas de cada Sprint
3. Hayas entendido qué hace cada librería

Cuéntame cuando termines y respondemos juntos. 👨‍💻
