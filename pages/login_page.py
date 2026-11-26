"""
pages/login_page.py
Page Object de la pantalla de login de saucedemo.com.
"""
import logging

from selenium.webdriver.common.by import By

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """Pantalla de inicio de sesión."""

    RUTA = "/"

    # --- Localizadores ---
    CAMPO_USUARIO = (By.ID, "user-name")
    CAMPO_PASSWORD = (By.ID, "password")
    BOTON_LOGIN = (By.ID, "login-button")
    MENSAJE_ERROR = (By.CSS_SELECTOR, "h3[data-test='error']")

    # --- Acciones ---
    def abrir(self):
        """Navega al login y espera a que el formulario esté visible."""
        self.navegar()
        self.encontrar(self.CAMPO_USUARIO)
        return self

    def iniciar_sesion(self, usuario, password):
        """Completa el formulario y envía. Nunca se loguea la contraseña."""
        logger.info(f"Iniciando sesión con el usuario: '{usuario}'")
        self.escribir(self.CAMPO_USUARIO, usuario)
        self.escribir(self.CAMPO_PASSWORD, password)
        self.hacer_clic(self.BOTON_LOGIN)

    def obtener_mensaje_error(self):
        mensaje = self.obtener_texto(self.MENSAJE_ERROR)
        logger.info(f"Mensaje de error mostrado: {mensaje}")
        return mensaje

    def formulario_visible(self):
        """True si el botón de login está en pantalla (útil para validar el logout)."""
        return self.esta_visible(self.BOTON_LOGIN)
