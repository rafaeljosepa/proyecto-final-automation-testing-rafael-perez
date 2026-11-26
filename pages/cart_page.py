"""
pages/cart_page.py
Page Object del carrito de compras.
"""
import logging

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.checkout_page import CheckoutInfoPage
from utils.helpers import convertir_precio

logger = logging.getLogger(__name__)


class CartPage(BasePage):
    """Carrito: listado de ítems agregados, eliminación y acceso al checkout."""

    RUTA = "/cart.html"

    # --- Localizadores ---
    ITEMS = (By.CLASS_NAME, "cart_item")
    NOMBRE_ITEM = (By.CLASS_NAME, "inventory_item_name")
    PRECIO_ITEM = (By.CLASS_NAME, "inventory_item_price")
    BOTON_ITEM = (By.TAG_NAME, "button")  # botón "Remove" dentro de cada ítem
    BOTON_CHECKOUT = (By.ID, "checkout")
    BOTON_SEGUIR_COMPRANDO = (By.ID, "continue-shopping")

    def obtener_items(self):
        """Devuelve los ítems del carrito (lista vacía si no hay ninguno, sin lanzar error)."""
        self.esperar_url()
        return self.driver.find_elements(*self.ITEMS)

    def obtener_nombres_items(self):
        return [item.find_element(*self.NOMBRE_ITEM).text for item in self.obtener_items()]

    def obtener_precios_items(self):
        return [convertir_precio(item.find_element(*self.PRECIO_ITEM).text) for item in self.obtener_items()]

    def eliminar_item(self, nombre_buscado):
        """Elimina del carrito el ítem con el nombre indicado."""
        for item in self.obtener_items():
            if item.find_element(*self.NOMBRE_ITEM).text == nombre_buscado:
                item.find_element(*self.BOTON_ITEM).click()
                logger.info(f"Producto eliminado del carrito: {nombre_buscado}")
                return
        raise ValueError(f"El producto '{nombre_buscado}' no está en el carrito")

    def ir_al_checkout(self):
        self.hacer_clic(self.BOTON_CHECKOUT)
        return CheckoutInfoPage(self.driver).esperar_url()
