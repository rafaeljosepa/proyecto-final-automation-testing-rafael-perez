"""
tests/ui/test_catalogo.py
Navegación y verificación del catálogo de productos (Page Object Model).
El ordenamiento se parametriza desde datos/productos.json.
"""
import logging

import pytest

from utils.lector_datos import cargar_json

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.ui

ORDENAMIENTOS = cargar_json("productos.json")["ordenamientos"]


@pytest.mark.smoke
def test_titulo_inventario(inventario):
    """El inventario muestra el título de pestaña y el encabezado correctos."""
    assert inventario.titulo_pestana == "Swag Labs", f"Título obtenido: {inventario.titulo_pestana}"
    assert inventario.obtener_encabezado() == "Products", f"Encabezado obtenido: {inventario.obtener_encabezado()}"


def test_productos_visibles(inventario):
    """Hay productos visibles y el primero tiene nombre y precio válidos."""
    productos = inventario.obtener_productos()
    assert len(productos) > 0, "No se encontraron productos en el catálogo"

    primer_producto = inventario.obtener_datos_producto(0)
    logger.info(f"Primer producto: {primer_producto['nombre']} - Precio: ${primer_producto['precio']}")

    assert primer_producto["nombre"], "El primer producto no tiene nombre"
    assert primer_producto["precio"] > 0, f"Precio inválido: {primer_producto['precio']}"


def test_elementos_interfaz(inventario):
    """El menú, el filtro de orden y el ícono del carrito están visibles."""
    elementos = inventario.elementos_principales_visibles()
    no_visibles = [nombre for nombre, visible in elementos.items() if not visible]
    assert not no_visibles, f"Elementos NO visibles: {no_visibles}"


@pytest.mark.parametrize("orden", ORDENAMIENTOS, ids=[o["opcion"] for o in ORDENAMIENTOS])
def test_ordenar_productos(inventario, orden):
    """El filtro ordena el catálogo por nombre o precio, en forma ascendente o descendente."""
    inventario.ordenar_por(orden["opcion"])

    if orden["criterio"] == "nombre":
        valores = inventario.obtener_nombres()
    else:
        valores = inventario.obtener_precios()

    esperado = sorted(valores, reverse=orden["descendente"])
    logger.info(f"Orden '{orden['opcion']}' -> {valores}")
    assert valores == esperado, f"El catálogo no quedó ordenado por '{orden['opcion']}': {valores}"
