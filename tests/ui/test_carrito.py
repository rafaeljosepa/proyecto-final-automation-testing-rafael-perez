"""
tests/ui/test_carrito.py
Interacción con productos y carrito de compras (Page Object Model).
Las combinaciones de productos se parametrizan desde datos/productos.json.
"""
import pytest

from utils.lector_datos import cargar_json

pytestmark = pytest.mark.ui

COMBINACIONES = cargar_json("productos.json")["combinaciones_carrito"]


@pytest.mark.smoke
def test_agregar_primer_producto_al_carrito(inventario):
    """Agregar el primer producto incrementa el contador y el producto aparece en el carrito."""
    assert inventario.obtener_cantidad_carrito() == 0, "El carrito no arrancó vacío"

    nombre_agregado = inventario.agregar_producto_por_indice(0)
    assert inventario.obtener_cantidad_carrito() == 1, \
        f"Contador obtenido: {inventario.obtener_cantidad_carrito()}"

    carrito = inventario.ir_al_carrito()
    nombres_en_carrito = carrito.obtener_nombres_items()
    assert nombres_en_carrito == [nombre_agregado], \
        f"Se esperaba ['{nombre_agregado}'], el carrito tiene {nombres_en_carrito}"


@pytest.mark.parametrize("combinacion", COMBINACIONES, ids=[c["caso"] for c in COMBINACIONES])
def test_agregar_varios_productos(inventario, combinacion):
    """El contador y el carrito reflejan exactamente los productos agregados."""
    productos = combinacion["productos"]
    for nombre in productos:
        inventario.agregar_producto_por_nombre(nombre)

    assert inventario.obtener_cantidad_carrito() == len(productos), \
        f"Contador: {inventario.obtener_cantidad_carrito()}, esperado: {len(productos)}"

    carrito = inventario.ir_al_carrito()
    assert sorted(carrito.obtener_nombres_items()) == sorted(productos), \
        f"Carrito: {carrito.obtener_nombres_items()}, esperado: {productos}"


def test_eliminar_producto_del_carrito(inventario):
    """Al eliminar el único producto, el carrito queda vacío y el contador desaparece."""
    nombre = inventario.agregar_producto_por_indice(0)
    carrito = inventario.ir_al_carrito()

    carrito.eliminar_item(nombre)

    assert carrito.obtener_nombres_items() == [], f"El carrito no quedó vacío: {carrito.obtener_nombres_items()}"
    assert inventario.obtener_cantidad_carrito() == 0, "El contador del carrito sigue visible"
