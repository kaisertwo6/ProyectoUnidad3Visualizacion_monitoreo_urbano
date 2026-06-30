# 🎯 Backend Setup Guide: API → Database → Scheduler

## 🌟 ¿Por qué esto impresiona al profesor?

Open-Meteo ofrece **mucho más que solo temperatura**:
- `visibility`: Visibilidad (detecta niebla, humo de contaminación)
- `wind_speed_10m`: Velocidad del viento (correlaciona con congestión)
- `weather_code`: Código de clima (lluvia, nieve, etc)
- `cloud_cover`: Cobertura de nubes (condiciones adversas)

**Idea premium:** Crear alertas inteligentes basadas en **múltiples factores**:
```python
# Ejemplo: Si la combinación es peligrosa
if visibility < 500 and wind_speed > 50 and traffic > 300:
    alert_level = "CRÍTICA - Condiciones peligrosas"
```

Este tipo de **lógica correlativa** es lo que hace un dashboard realmente útil.

---

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

---

# 📊 Tipos de Datos: SQL vs Python

**¿Sabías que los tipos en SQL Y Python son diferentes?**

| SQL | Python | Ejemplo |
|-----|--------|---------|
| `INT` | `int` | `vehiculos = 150` |
| `FLOAT` | `float` | `temperatura = 22.5` |
| `VARCHAR(50)` | `str` | `zona = "Centro"` |
| `TIMESTAMP` | `datetime` | `timestamp = datetime.now()` |
| `BOOLEAN` | `bool` | `is_congestion = True` |

**Cuando insertamos a la BD, Python convierte automáticamente:**
```python
trafico_data = {
    'zona': 'Centro',        # Python str → SQL VARCHAR
    'vehiculos': 150,        # Python int → SQL INT
    'velocidad_promedio': 45.5,  # Python float → SQL FLOAT
    'timestamp': datetime.now()  # Python datetime → SQL TIMESTAMP
}
```

---

# 🔮 Dunder Methods (Double Underscore) - ¿Qué son?

**Dunder methods = "Magic methods" = Métodos especiales de Python**

Controlan cómo se comportan tus objetos:

## Ejemplo 1: `__init__` (Constructor)
```python
class Trafico:
    def __init__(self, zona, vehiculos, velocidad):
        # Se ejecuta cuando creas: trafico = Trafico("Centro", 150, 45.5)
        self.zona = zona
        self.vehiculos = vehiculos
        self.velocidad = velocidad
        self.timestamp = datetime.now()
```

## Ejemplo 2: `__str__` (Qué mostrar en print)
```python
class Trafico:
    def __str__(self):
        return f"🚗 Tráfico {self.zona}: {self.vehiculos} vehículos a {self.velocidad} km/h"

# Uso:
trafico = Trafico("Centro", 150, 45.5)
print(trafico)  # Output: 🚗 Tráfico Centro: 150 vehículos a 45.5 km/h
```

## Ejemplo 3: `__repr__` (Para debug técnico)
```python
class Trafico:
    def __repr__(self):
        return f"Trafico(zona='{self.zona}', vehiculos={self.vehiculos})"

# Útil en desarrollo para ver exactamente qué datos tienes
print(repr(trafico))  # Output: Trafico(zona='Centro', vehiculos=150)
```

## Ejemplo 4: `__eq__` (Comparación)
```python
class Trafico:
    def __eq__(self, other):
        # ¿Dos tráficos son iguales si están en la misma zona?
        return self.zona == other.zona and self.vehiculos == other.vehiculos

# Uso:
trafico1 = Trafico("Centro", 150, 45.5)
trafico2 = Trafico("Centro", 150, 45.5)
print(trafico1 == trafico2)  # True
```

**¿Para qué sirve en tu proyecto?**
- `__init__`: Crear objetos TraficoData, CalidadAireData
- `__str__`: Logs claros ("Centro: 150 vehículos")
- `__repr__`: Debug en consola
- `__eq__`: Comparar si hay cambios en los datos

---

# 🎯 Cómo usarás esto en BACKEND

**Estructura propuesta:**

```python
# backend/models.py (nuevo archivo)
from datetime import datetime

class TraficoData:
    def __init__(self, zona, vehiculos, velocidad_promedio):
        self.zona = zona
        self.vehiculos = vehiculos
        self.velocidad_promedio = velocidad_promedio
        self.timestamp = datetime.now()
    
    def __str__(self):
        return f"Tráfico {self.zona}: {self.vehiculos} veh @ {self.velocidad_promedio} km/h"
    
    def to_dict(self):
        """Convierte a diccionario para insertar en BD"""
        return {
            'zona': self.zona,
            'vehiculos': self.vehiculos,
            'velocidad_promedio': self.velocidad_promedio,
            'timestamp': self.timestamp
        }

class CalidadAireData:
    def __init__(self, zona, pm25, no2, o3):
        self.zona = zona
        self.pm25 = pm25
        self.no2 = no2
        self.o3 = o3
        self.timestamp = datetime.now()
        self.aqi = self.calculate_aqi()  # ← Usa la función SQL!
    
    def calculate_aqi(self):
        """Llama a la función SQL desde Python"""
        return (self.pm25 * 0.5 + self.no2 * 0.3 + self.o3 * 0.2)
    
    def __str__(self):
        return f"Aire {self.zona}: PM2.5={self.pm25}, AQI={self.aqi:.1f}"
```

**Luego usas así en main.py:**
```python
# Fetch datos de APIs
trafico = Trafico("Centro", 150, 45.5)
aire = CalidadAireData("Centro", 45.2, 32.1, 25.0)

# Logs claros
print(trafico)  # "Tráfico Centro: 150 veh @ 45.5 km/h"
print(aire)     # "Aire Centro: PM2.5=45.2, AQI=23.4"

# Inserta en BD
db.insert_trafico(trafico.to_dict())
db.insert_aire(aire.to_dict())
```

---

# 💡 Ideas avanzadas (Para impresionar)

## 1. Alertas inteligentes basadas en múltiples factores

```python
class AlertaInteligente:
    def __init__(self, temperatura, visibilidad, viento, trafico):
        self.temperatura = temperatura
        self.visibilidad = visibilidad
        self.viento = viento
        self.trafico = trafico
    
    def evaluar_riesgo(self):
        riesgo = 0
        
        if self.temperatura < 0 and self.visibilidad < 500:
            riesgo += 3  # Peligro de hielo
        
        if self.viento > 50:
            riesgo += 2  # Vientos peligrosos
        
        if self.trafico > 300 and self.visibilidad < 1000:
            riesgo += 2  # Congestión + mala visibilidad
        
        if riesgo >= 5:
            return "🔴 CRÍTICA"
        elif riesgo >= 3:
            return "🟠 ALTA"
        elif riesgo >= 1:
            return "🟡 MEDIA"
        else:
            return "🟢 BAJA"
```

## 2. Predicción simple (machine learning basic)

```python
def predecir_congestión(temperatura, humedad, hora_del_dia):
    """Predicción básica de congestión"""
    congestión_base = 100
    
    # Horas pico (7-9 AM, 5-7 PM)
    if hora_del_dia in [7, 8, 17, 18]:
        congestión_base += 100
    
    # Temperatura (gente evita salir si es muy caliente)
    if temperatura > 30:
        congestión_base -= 30
    
    # Humedad (lluvia → menos tráfico)
    if humedad > 80:
        congestión_base -= 20
    
    return max(0, congestión_base)
```

---

**⚠️ NO CONTINÚES HASTA QUE:**
1. Hayas leído toda la documentación
2. Hayas respondido las preguntas de cada Sprint
3. Hayas entendido:
   - Qué son los dunder methods
   - Cómo se mapean tipos SQL ↔ Python
   - Cómo crear objetos de datos

Cuéntame cuando termines y respondemos juntos. 👨‍💻
