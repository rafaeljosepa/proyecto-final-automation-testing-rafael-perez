"""
tests/ui/test_carrito.py
Interacción con productos y carrito de compras (Page Object Model).
"""
import pytest

pytestmark = pytest.mark.ui


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
