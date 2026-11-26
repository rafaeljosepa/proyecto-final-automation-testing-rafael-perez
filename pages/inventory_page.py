"""
pages/inventory_page.py
Page Object del catálogo de productos (página de inventario).
"""
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage
from pages.cart_page import CartPage
from utils.helpers import convertir_precio

logger = logging.getLogger(__name__)


class InventoryPage(BasePage):
    """Catálogo: listado de productos, filtro de orden, menú y acceso al carrito."""

    RUTA = "/inventory.html"

    # --- Localizadores de la página ---
    ENCABEZADO = (By.CLASS_NAME, "title")
    PRODUCTOS = (By.CLASS_NAME, "inventory_item")
    FILTRO_ORDEN = (By.CLASS_NAME, "product_sort_container")
    MENU_HAMBURGUESA = (By.ID, "react-burger-menu-btn")
    LINK_LOGOUT = (By.ID, "logout_sidebar_link")
    ICONO_CARRITO = (By.CLASS_NAME, "shopping_cart_link")
    CONTADOR_CARRITO = (By.CLASS_NAME, "shopping_cart_badge")

    # --- Localizadores relativos (se buscan DENTRO de cada producto) ---
    NOMBRE_PRODUCTO = (By.CLASS_NAME, "inventory_item_name")
    PRECIO_PRODUCTO = (By.CLASS_NAME, "inventory_item_price")
    BOTON_PRODUCTO = (By.TAG_NAME, "button")

    # --- Estado de la página ---
    def esta_cargada(self):
        """Espera la URL del inventario y confirma que el encabezado sea visible."""
        self.esperar_url()
        return self.esta_visible(self.ENCABEZADO)

    def obtener_encabezado(self):
        return self.obtener_texto(self.ENCABEZADO)

    def elementos_principales_visibles(self):
        """Devuelve un diccionario {elemento: visible} con los controles principales de la interfaz."""
        return {
            "menu hamburguesa": self.esta_visible(self.MENU_HAMBURGUESA),
            "filtro de orden": self.esta_visible(self.FILTRO_ORDEN),
            "icono del carrito": self.esta_visible(self.ICONO_CARRITO),
        }

    # --- Productos ---
    def obtener_productos(self):
        return self.encontrar_todos(self.PRODUCTOS)

    def obtener_datos_producto(self, indice):
        """Devuelve {'nombre', 'precio'} del producto en la posición indicada."""
        producto = self.obtener_productos()[indice]
        nombre = producto.find_element(*self.NOMBRE_PRODUCTO).text
        precio = convertir_precio(producto.find_element(*self.PRECIO_PRODUCTO).text)
        return {"nombre": nombre, "precio": precio}

    def obtener_nombres(self):
        return [p.find_element(*self.NOMBRE_PRODUCTO).text for p in self.obtener_productos()]

    def obtener_precios(self):
        return [convertir_precio(p.find_element(*self.PRECIO_PRODUCTO).text) for p in self.obtener_productos()]

    def ordenar_por(self, opcion):
        """Ordena el catálogo. Opciones válidas: 'az', 'za', 'lohi', 'hilo'."""
        logger.info(f"Ordenando productos por: {opcion}")
        Select(self.encontrar(self.FILTRO_ORDEN)).select_by_value(opcion)

    # --- Carrito ---
    def agregar_producto_por_indice(self, indice):
        """Agrega al carrito el producto en la posición indicada y devuelve su nombre."""
        producto = self.obtener_productos()[indice]
        nombre = producto.find_element(*self.NOMBRE_PRODUCTO).text
        producto.find_element(*self.BOTON_PRODUCTO).click()
        logger.info(f"Producto agregado al carrito: {nombre}")
        return nombre

    def agregar_producto_por_nombre(self, nombre_buscado):
        """Agrega al carrito el producto cuyo nombre coincide exactamente."""
        for producto in self.obtener_productos():
            if producto.find_element(*self.NOMBRE_PRODUCTO).text == nombre_buscado:
                producto.find_element(*self.BOTON_PRODUCTO).click()
                logger.info(f"Producto agregado al carrito: {nombre_buscado}")
                return
        raise ValueError(f"No existe el producto '{nombre_buscado}' en el catálogo")

    def obtener_cantidad_carrito(self):
        """Devuelve el número del contador del carrito (0 si el contador no se muestra)."""
        contadores = self.driver.find_elements(*self.CONTADOR_CARRITO)
        return int(contadores[0].text) if contadores else 0

    def ir_al_carrito(self):
        self.hacer_clic(self.ICONO_CARRITO)
        return CartPage(self.driver).esperar_url()

    # --- Sesión ---
    def cerrar_sesion(self):
        """Abre el menú lateral y cierra la sesión."""
        self.hacer_clic(self.MENU_HAMBURGUESA)
        self.hacer_clic(self.LINK_LOGOUT)
        logger.info("Sesión cerrada desde el menú lateral")
