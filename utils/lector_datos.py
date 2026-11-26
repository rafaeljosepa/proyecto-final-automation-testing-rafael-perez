"""
utils/lector_datos.py
Lectura de datos de prueba desde fuentes externas (JSON y CSV) ubicadas en la carpeta datos/.
Separar los datos del código permite agregar casos nuevos sin modificar los tests.
"""
import csv
import json

from utils.config import CARPETA_DATOS


def cargar_json(nombre_archivo):
    """Lee un archivo JSON de la carpeta datos/ y devuelve su contenido."""
    with open(CARPETA_DATOS / nombre_archivo, encoding="utf-8") as archivo:
        return json.load(archivo)


def cargar_csv(nombre_archivo):
    """Lee un archivo CSV de la carpeta datos/ y devuelve una lista de diccionarios (una fila por caso)."""
    with open(CARPETA_DATOS / nombre_archivo, encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def cargar_usuario(tipo):
    """Devuelve (usuario, password) del tipo indicado en datos/usuarios.json."""
    usuarios = cargar_json("usuarios.json")
    return usuarios[tipo]["usuario"], usuarios[tipo]["password"]
