"""
utils/api_client.py
Cliente HTTP reutilizable para las pruebas de API, construido sobre la biblioteca Requests.
Centraliza la URL base, los headers, el timeout y el logging de cada petición/respuesta,
para que los tests solo se ocupen de qué pedir y qué validar.
"""
import logging

import requests

from utils.config import API_URL_BASE, TIMEOUT_API

logger = logging.getLogger(__name__)


class ApiClient:
    """Envoltorio de requests.Session con logging de cada llamada."""

    def __init__(self, url_base=API_URL_BASE, timeout=TIMEOUT_API):
        self.url_base = url_base.rstrip("/")
        self.timeout = timeout
        self.sesion = requests.Session()
        self.sesion.headers.update({
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json",
        })

    def _enviar(self, metodo, endpoint, **kwargs):
        """Envía la petición y registra método, URL, código de estado y duración."""
        url = f"{self.url_base}/{endpoint.lstrip('/')}"
        logger.info(f"--> {metodo} {url} {kwargs.get('params') or ''}{kwargs.get('json') or ''}")
        respuesta = self.sesion.request(metodo, url, timeout=self.timeout, **kwargs)
        logger.info(f"<-- {respuesta.status_code} {metodo} {url} ({respuesta.elapsed.total_seconds():.3f}s)")
        return respuesta

    def get(self, endpoint, params=None):
        return self._enviar("GET", endpoint, params=params)

    def post(self, endpoint, datos):
        return self._enviar("POST", endpoint, json=datos)

    def put(self, endpoint, datos):
        return self._enviar("PUT", endpoint, json=datos)

    def delete(self, endpoint):
        return self._enviar("DELETE", endpoint)

    def cerrar(self):
        self.sesion.close()
