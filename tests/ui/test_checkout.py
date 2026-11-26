"""
tests/ui/test_checkout.py
Flujo completo de compra (E2E): login -> catálogo -> carrito -> checkout -> confirmación.
Los datos del comprador vienen de datos/clientes.json y los casos negativos de datos/checkout.csv.
"""
import logging

import pytest

from utils.lector_datos import cargar_csv, cargar_json

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.ui

CLIENTE = cargar_json("clientes.json")["cliente_valido"]
CASOS_DATOS_FALTANTES = cargar_csv("checkout.csv")
PRODUCTOS_A_COMPRAR = ["Sauce Labs Backpack", "Sauce Labs Bike Light"]


@pytest.mark.smoke
def test_checkout_completo(inventario):
    """E2E: se compran dos productos, los totales son correctos y se confirma la orden."""
    # 1. Agregar productos desde el catálogo y guardar sus precios para validar los totales
    precios_esperados = {}
    for indice, nombre in enumerate(inventario.obtener_nombres()):
        if nombre in PRODUCTOS_A_COMPRAR:
            precios_esperados[nombre] = inventario.obtener_datos_producto(indice)["precio"]
    for nombre in PRODUCTOS_A_COMPRAR:
        inventario.agregar_producto_por_nombre(nombre)

    # 2. Carrito -> checkout con datos válidos
    carrito = inventario.ir_al_carrito()
    assert sorted(carrito.obtener_nombres_items()) == sorted(PRODUCTOS_A_COMPRAR)

    datos_comprador = carrito.ir_al_checkout()
    datos_comprador.completar_datos(CLIENTE["nombre"], CLIENTE["apellido"], CLIENTE["codigo_postal"])
    resumen = datos_comprador.continuar().esperar_url()

    # 3. Resumen: productos y cálculo de totales
    assert sorted(resumen.obtener_nombres_items()) == sorted(PRODUCTOS_A_COMPRAR)

    subtotal_esperado = round(sum(precios_esperados.values()), 2)
    subtotal = resumen.obtener_subtotal()
    impuesto = resumen.obtener_impuesto()
    total = resumen.obtener_total()
    logger.info(f"Subtotal: ${subtotal} | Impuesto: ${impuesto} | Total: ${total}")

    assert subtotal == subtotal_esperado, f"Subtotal ${subtotal}, esperado ${subtotal_esperado}"
    assert total == round(subtotal + impuesto, 2), f"Total ${total} != subtotal + impuesto (${subtotal} + ${impuesto})"

    # 4. Confirmación de la orden y carrito vacío
    confirmacion = resumen.finalizar_compra()
    mensaje = confirmacion.obtener_mensaje_confirmacion()
    assert mensaje == "Thank you for your order!", f"Mensaje de confirmación inesperado: {mensaje}"
    assert inventario.obtener_cantidad_carrito() == 0, "El carrito no se vació después de la compra"


@pytest.mark.parametrize("caso", CASOS_DATOS_FALTANTES, ids=[c["caso"] for c in CASOS_DATOS_FALTANTES])
def test_checkout_datos_obligatorios(inventario, caso):
    """Escenario negativo: el checkout no avanza si falta un dato obligatorio del comprador."""
    inventario.agregar_producto_por_indice(0)
    datos_comprador = inventario.ir_al_carrito().ir_al_checkout()

    datos_comprador.completar_datos(caso["nombre"], caso["apellido"], caso["codigo_postal"])
    datos_comprador.continuar()

    mensaje_error = datos_comprador.obtener_mensaje_error()
    assert caso["mensaje_esperado"] in mensaje_error, \
        f"Se esperaba '{caso['mensaje_esperado']}', se obtuvo: '{mensaje_error}'"
    assert "/checkout-step-one.html" in datos_comprador.url_actual, "El checkout avanzó con datos incompletos"
