"""
utils/helpers.py
Funciones auxiliares genéricas, independientes de cualquier página o test.
"""
import re
from datetime import datetime


def convertir_precio(texto):
    """Convierte un texto con precio (ej. 'Item total: $29.99') en un número decimal (29.99)."""
    coincidencia = re.search(r"\d+(?:\.\d+)?", texto)
    if coincidencia is None:
        raise ValueError(f"No se encontró un precio en el texto: '{texto}'")
    return float(coincidencia.group())


def nombre_archivo_seguro(texto):
    """Reemplaza caracteres no válidos para nombres de archivo (ej. los corchetes de tests parametrizados)."""
    return re.sub(r"[^\w\-]+", "_", texto).strip("_")


def marca_de_tiempo():
    """Devuelve la fecha y hora actual en formato AAAAMMDD_HHMMSS, ideal para nombres de archivo."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
