"""
pages/base_page.py
Clase base de todos los Page Objects.
Centraliza las acciones comunes (buscar, hacer clic, escribir, esperar) para que cada página
solo defina sus localizadores y sus acciones de negocio.
"""
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.config import TIEMPO_ESPERA, URL_BASE


class BasePage:
    """Acciones genéricas reutilizables por cualquier página."""

    RUTA = "/"  # cada página hija define su propia ruta

    def __init__(self, driver):
        self.driver = driver
        self.espera = WebDriverWait(driver, TIEMPO_ESPERA)

    # --- Navegación ---
    def navegar(self):
        """Abre la página directamente por su URL."""
        self.driver.get(URL_BASE + self.RUTA)
        return self

    def esperar_url(self, fragmento=None):
        """Espera explícitamente a que la URL contenga la ruta de la página (o el fragmento indicado)."""
        self.espera.until(EC.url_contains(fragmento or self.RUTA))
        return self

    @property
    def url_actual(self):
        return self.driver.current_url

    @property
    def titulo_pestana(self):
        return self.driver.title

    # --- Búsqueda de elementos ---
    def encontrar(self, localizador):
        """Espera a que el elemento sea visible y lo devuelve."""
        return self.espera.until(EC.visibility_of_element_located(localizador))

    def encontrar_todos(self, localizador):
        """Espera a que todos los elementos sean visibles y devuelve la lista."""
        return self.espera.until(EC.visibility_of_all_elements_located(localizador))

    def esta_visible(self, localizador):
        """Devuelve True/False sin lanzar error si el elemento no existe."""
        elementos = self.driver.find_elements(*localizador)
        return len(elementos) > 0 and elementos[0].is_displayed()

    # --- Interacciones ---
    def hacer_clic(self, localizador):
        """Espera a que el elemento sea clickeable y hace clic."""
        self.espera.until(EC.element_to_be_clickable(localizador)).click()

    def escribir(self, localizador, texto):
        """Limpia el campo y escribe el texto indicado."""
        campo = self.encontrar(localizador)
        campo.clear()
        campo.send_keys(texto)

    def obtener_texto(self, localizador):
        return self.encontrar(localizador).text
