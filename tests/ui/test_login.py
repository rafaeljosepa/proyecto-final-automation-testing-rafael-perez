"""
tests/ui/test_login.py
Casos de prueba del login de saucedemo.com (Page Object Model).
Los escenarios negativos se parametrizan desde datos/login_invalido.csv.
"""
import pytest

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.lector_datos import cargar_csv, cargar_usuario

pytestmark = pytest.mark.ui

# Cada fila del CSV se convierte en una ejecución independiente del test
CASOS_LOGIN_INVALIDO = cargar_csv("login_invalido.csv")


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


@pytest.mark.parametrize("caso", CASOS_LOGIN_INVALIDO, ids=[c["caso"] for c in CASOS_LOGIN_INVALIDO])
def test_login_invalido(login_page, caso):
    """Escenario negativo: con credenciales inválidas se muestra el error esperado y no se accede."""
    login_page.iniciar_sesion(caso["usuario"], caso["password"])

    mensaje_error = login_page.obtener_mensaje_error()
    assert caso["mensaje_esperado"] in mensaje_error, \
        f"Se esperaba un mensaje con '{caso['mensaje_esperado']}', se obtuvo: '{mensaje_error}'"
    assert "/inventory.html" not in login_page.url_actual, "Se accedió al inventario con credenciales inválidas"


def test_logout(inventario, driver):
    """Desde el menú lateral se cierra la sesión y se vuelve a la pantalla de login."""
    inventario.cerrar_sesion()

    login = LoginPage(driver)
    login.encontrar(login.BOTON_LOGIN)  # espera explícita a que vuelva el formulario
    assert login.formulario_visible(), "No se volvió a mostrar el formulario de login"
    assert "/inventory.html" not in login.url_actual, f"La sesión sigue abierta. URL: {login.url_actual}"
