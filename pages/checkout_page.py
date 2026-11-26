"""
pages/checkout_page.py
Page Objects del proceso de compra (checkout), que tiene tres pasos:
  1. CheckoutInfoPage      -> datos del comprador
  2. CheckoutOverviewPage  -> resumen y totales
  3. CheckoutCompletePage  -> confirmación de la orden
"""
import logging

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.helpers import convertir_precio

logger = logging.getLogger(__name__)


class CheckoutInfoPage(BasePage):
    """Paso 1: formulario con nombre, apellido y código postal."""

    RUTA = "/checkout-step-one.html"

    CAMPO_NOMBRE = (By.ID, "first-name")
    CAMPO_APELLIDO = (By.ID, "last-name")
    CAMPO_CODIGO_POSTAL = (By.ID, "postal-code")
    BOTON_CONTINUAR = (By.ID, "continue")
    MENSAJE_ERROR = (By.CSS_SELECTOR, "h3[data-test='error']")

    def completar_datos(self, nombre, apellido, codigo_postal):
        logger.info(f"Datos de checkout -> nombre: '{nombre}', apellido: '{apellido}', CP: '{codigo_postal}'")
        self.escribir(self.CAMPO_NOMBRE, nombre)
        self.escribir(self.CAMPO_APELLIDO, apellido)
        self.escribir(self.CAMPO_CODIGO_POSTAL, codigo_postal)

    def continuar(self):
        """Envía el formulario. Si los datos son válidos, avanza al resumen."""
        self.hacer_clic(self.BOTON_CONTINUAR)
        return CheckoutOverviewPage(self.driver)

    def obtener_mensaje_error(self):
        mensaje = self.obtener_texto(self.MENSAJE_ERROR)
        logger.info(f"Mensaje de error en checkout: {mensaje}")
        return mensaje


class CheckoutOverviewPage(BasePage):
    """Paso 2: resumen de la compra con subtotal, impuestos y total."""

    RUTA = "/checkout-step-two.html"

    ITEMS = (By.CLASS_NAME, "cart_item")
    NOMBRE_ITEM = (By.CLASS_NAME, "inventory_item_name")
    SUBTOTAL = (By.CLASS_NAME, "summary_subtotal_label")
    IMPUESTO = (By.CLASS_NAME, "summary_tax_label")
    TOTAL = (By.CLASS_NAME, "summary_total_label")
    BOTON_FINALIZAR = (By.ID, "finish")

    def obtener_nombres_items(self):
        return [item.find_element(*self.NOMBRE_ITEM).text for item in self.encontrar_todos(self.ITEMS)]

    def obtener_subtotal(self):
        return convertir_precio(self.obtener_texto(self.SUBTOTAL))

    def obtener_impuesto(self):
        return convertir_precio(self.obtener_texto(self.IMPUESTO))

    def obtener_total(self):
        return convertir_precio(self.obtener_texto(self.TOTAL))

    def finalizar_compra(self):
        self.hacer_clic(self.BOTON_FINALIZAR)
        logger.info("Compra finalizada")
        return CheckoutCompletePage(self.driver).esperar_url()


class CheckoutCompletePage(BasePage):
    """Paso 3: confirmación de la orden."""

    RUTA = "/checkout-complete.html"

    ENCABEZADO_CONFIRMACION = (By.CLASS_NAME, "complete-header")
    BOTON_VOLVER = (By.ID, "back-to-products")

    def obtener_mensaje_confirmacion(self):
        mensaje = self.obtener_texto(self.ENCABEZADO_CONFIRMACION)
        logger.info(f"Mensaje de confirmación: {mensaje}")
        return mensaje
