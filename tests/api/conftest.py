"""
tests/api/conftest.py
Fixtures exclusivas de las pruebas de API.
"""
import pytest

from utils.api_client import ApiClient


@pytest.fixture(scope="session")
def api_client():
    """Un único cliente HTTP compartido por todos los tests de API (reutiliza la conexión)."""
    cliente = ApiClient()
    yield cliente
    cliente.cerrar()
