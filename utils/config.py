"""
utils/config.py
Configuración central del framework: URLs, tiempos de espera y opciones del navegador.
Cambiar un valor acá impacta en todo el proyecto, sin tocar los tests.
"""
import os
from pathlib import Path

# --- Rutas del proyecto ---
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ_PROYECTO / "datos"
CARPETA_REPORTES = RAIZ_PROYECTO / "reports"
CARPETA_SCREENSHOTS = CARPETA_REPORTES / "screenshots"

# --- UI (Selenium) ---
URL_BASE = "https://www.saucedemo.com"
TIEMPO_ESPERA = 10  # segundos máximos para las esperas explícitas

# Variables de entorno opcionales (útiles para CI o para correr sin ventana):
#   HEADLESS=1             -> ejecuta Chrome sin interfaz gráfica
#   CHROMEDRIVER_PATH=...  -> usa un chromedriver específico en lugar de Selenium Manager
HEADLESS = os.getenv("HEADLESS", "0") == "1"
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")

# --- API (Requests) ---
API_URL_BASE = "https://jsonplaceholder.typicode.com"
TIMEOUT_API = 10            # segundos máximos de espera por respuesta
TIEMPO_MAXIMO_API = 2.0     # umbral de rendimiento esperado (segundos)
