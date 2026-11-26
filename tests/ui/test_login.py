"""
tests/ui/test_login.py
Casos de prueba del login de saucedemo.com (Page Object Model).
"""
import pytest

from pages.inventory_page import InventoryPage
from utils.lector_datos import cargar_usuario

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_login_exitoso(login_page, driver):
    """Un usuario válido inicia sesión y es redirigido al inventario."""
    usuario, password = cargar_usuario("valido")

    login_page.iniciar_sesion(usuario, password)

    inventario = InventoryPage(driver)
    assert inventario.esta_cargada(), f"No se cargó el inventario. URL actual: {inventario.url_actual}"
    assert "/inventory.html" in inventario.url_actual, f"URL inesperada: {inventario.url_actual}"
    assert inventario.titulo_pestana == "Swag Labs", f"Título obtenido: {inventario.titulo_pestana}"
    assert inventario.obtener_encabezado() == "Products", f"Encabezado obtenido: {inventario.obtener_encabezado()}"


def test_login_usuario_bloqueado(login_page):
    """Un usuario bloqueado no puede iniciar sesión y ve el mensaje correspondiente."""
    usuario, password = cargar_usuario("bloqueado")

    login_page.iniciar_sesion(usuario, password)

    mensaje_error = login_page.obtener_mensaje_error()
    assert "locked out" in mensaje_error, f"Mensaje inesperado: {mensaje_error}"
    assert "/inventory.html" not in login_page.url_actual, "El usuario bloqueado accedió al inventario"


def test_login_password_incorrecta(login_page):
    """Con contraseña incorrecta se muestra el error de credenciales."""
    usuario, password = cargar_usuario("password_incorrecta")

    login_page.iniciar_sesion(usuario, password)

    mensaje_error = login_page.obtener_mensaje_error()
    assert "do not match" in mensaje_error, f"Mensaje inesperado: {mensaje_error}"
    assert "/inventory.html" not in login_page.url_actual, "Se accedió al inventario con credenciales inválidas"
