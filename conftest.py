"""
conftest.py
Configuración compartida por todos los tests. Pytest detecta este archivo automáticamente.

Fixtures:
  - driver:     abre un Chrome nuevo antes de cada test de UI y lo cierra al terminar.
  - login_page: página de login ya abierta.
  - inventario: sesión iniciada con el usuario válido, ubicada en el catálogo (InventoryPage).

Hooks:
  - pytest_runtest_makereport: si un test de UI falla, guarda una captura con nombre del test
    y fecha/hora, y la adjunta al reporte HTML.
  - pytest_html_*: personalizan el reporte HTML (título, entorno y columna "Descripción").
"""
import html
import logging

import pytest
from pytest_html import extras as html_extras
from pytest_metadata.plugin import metadata_key
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.config import API_URL_BASE, CARPETA_SCREENSHOTS, CHROMEDRIVER_PATH, HEADLESS, URL_BASE
from utils.helpers import marca_de_tiempo, nombre_archivo_seguro
from utils.lector_datos import cargar_usuario

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Fixtures de UI
# ---------------------------------------------------------------------------
def crear_opciones_chrome():
    """Opciones de Chrome comunes a todas las ejecuciones (local y CI)."""
    opciones = webdriver.ChromeOptions()
    # Desactivamos el gestor de contraseñas para evitar popups que interrumpan el flujo
    # (con standard_user, Chrome avisa "contraseña filtrada").
    opciones.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    if HEADLESS:
        # Modo sin ventana: necesario en servidores de CI (GitHub Actions)
        opciones.add_argument("--headless=new")
        opciones.add_argument("--no-sandbox")
        opciones.add_argument("--disable-dev-shm-usage")
        opciones.add_argument("--window-size=1920,1080")
    else:
        opciones.add_argument("--start-maximized")
    return opciones


@pytest.fixture
def driver():
    """Navegador nuevo y aislado para cada test: garantiza la independencia entre tests."""
    servicio = Service(CHROMEDRIVER_PATH) if CHROMEDRIVER_PATH else None
    navegador = webdriver.Chrome(options=crear_opciones_chrome(), service=servicio)
    logger.info(f"Navegador iniciado (headless={HEADLESS})")

    yield navegador  # <- aquí se ejecuta el test

    navegador.quit()  # <- se ejecuta SIEMPRE, pase o falle el test
    logger.info("Navegador cerrado")


@pytest.fixture
def login_page(driver):
    """Página de login abierta y lista para usar."""
    return LoginPage(driver).abrir()


@pytest.fixture
def inventario(login_page, driver):
    """Sesión iniciada con el usuario válido; devuelve el catálogo (InventoryPage)."""
    usuario, password = cargar_usuario("valido")
    login_page.iniciar_sesion(usuario, password)
    pagina_inventario = InventoryPage(driver)
    assert pagina_inventario.esta_cargada(), "No se pudo cargar el inventario después del login"
    return pagina_inventario


# ---------------------------------------------------------------------------
# Capturas de pantalla automáticas en fallos
# ---------------------------------------------------------------------------
@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """Si un test de UI falla, guarda una captura y la adjunta al reporte HTML."""
    reporte = yield  # Pytest ejecuta la fase y nos devuelve su resultado

    # El docstring del test se muestra como "Descripción" en el reporte HTML
    reporte.descripcion = (item.function.__doc__ or "").strip()

    # 'setup' cubre fallos en fixtures (ej. login), 'call' cubre fallos dentro del test
    if reporte.when in ("setup", "call") and reporte.failed:
        navegador = item.funcargs.get("driver")
        if navegador is not None:
            CARPETA_SCREENSHOTS.mkdir(parents=True, exist_ok=True)
            nombre_captura = f"{nombre_archivo_seguro(item.name)}_{marca_de_tiempo()}.png"
            ruta = CARPETA_SCREENSHOTS / nombre_captura

            navegador.save_screenshot(str(ruta))
            logger.error(f"Test fallido: {item.name}. Captura guardada en {ruta}")

            adjuntos = getattr(reporte, "extras", [])
            adjuntos.append(html_extras.image(navegador.get_screenshot_as_base64(), name=nombre_captura))
            reporte.extras = adjuntos

    return reporte


# ---------------------------------------------------------------------------
# Personalización del reporte HTML
# ---------------------------------------------------------------------------
def pytest_configure(config):
    """Agrega datos del entorno de prueba a la sección 'Environment' del reporte."""
    metadatos = config.stash[metadata_key]
    metadatos["Proyecto"] = "Framework de Automatización de Pruebas - Rafael Pérez"
    metadatos["Sitio UI"] = URL_BASE
    metadatos["API"] = API_URL_BASE
    metadatos["Navegador"] = "Chrome (headless)" if HEADLESS else "Chrome"


def pytest_html_report_title(report):
    report.title = "Reporte de pruebas automatizadas - UI (Selenium) y API (Requests)"


def pytest_html_results_table_header(cells):
    cells.insert(2, "<th>Descripción</th>")


def pytest_html_results_table_row(report, cells):
    cells.insert(2, f"<td>{html.escape(getattr(report, 'descripcion', ''))}</td>")
