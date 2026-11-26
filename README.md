# Proyecto Final – Framework de Automatización de Pruebas

Framework de automatización de pruebas en **Python** que combina pruebas de **UI con Selenium WebDriver** sobre [saucedemo.com](https://www.saucedemo.com/) y pruebas de **API con Requests** sobre [JSONPlaceholder](https://jsonplaceholder.typicode.com/). Lo desarrollé como Trabajo Final Integrador del curso de QA Automation de Talento Tech.

## 🎯 Propósito

Construir un framework **mantenible y escalable** que:

- automatice flujos completos de un e-commerce: login, catálogo, carrito y checkout, incluyendo escenarios negativos;
- valide una API REST con distintos métodos HTTP (GET, POST, PUT y DELETE), escenarios de error y peticiones encadenadas;
- separe la lógica de las pruebas de la interacción con la página mediante **Page Object Model**;
- lea los datos de prueba desde **fuentes externas** (CSV y JSON) y los use para **parametrizar** los tests;
- genere **evidencias claras**: reporte HTML, logs y capturas de pantalla automáticas cuando un test falla.

## 🛠️ Tecnologías

| Herramienta | Uso |
|---|---|
| Python 3.10+ | Lenguaje principal |
| Pytest | Framework de testing: fixtures, parametrización y marcadores |
| Selenium WebDriver | Automatización del navegador (Chrome) |
| Requests | Pruebas de API REST |
| pytest-html | Reporte HTML con estado, duración y capturas |
| logging (Python) | Registro de pasos clave en consola y archivo |
| Git / GitHub | Control de versiones con ramas por funcionalidad |

## 📁 Estructura del proyecto

- **`pages/`**: Page Objects, una clase por página
  - `base_page.py`: acciones comunes (esperas, clics, escritura) heredadas por todas las páginas
  - `login_page.py`: pantalla de login
  - `inventory_page.py`: catálogo de productos, orden, carrito y menú
  - `cart_page.py`: carrito de compras
  - `checkout_page.py`: los 3 pasos del checkout (datos, resumen, confirmación)
- **`tests/`**: casos de prueba
  - **`ui/`**: pruebas de interfaz con Selenium
    - `test_login.py`, `test_catalogo.py`, `test_carrito.py`, `test_checkout.py`
  - **`api/`**: pruebas de API con Requests
    - `conftest.py`: fixture del cliente HTTP
    - `test_posts_api.py`
- **`utils/`**: funciones auxiliares
  - `config.py`: configuración central (URLs, tiempos de espera, modo headless)
  - `lector_datos.py`: lectura de datos de prueba desde JSON y CSV
  - `api_client.py`: cliente HTTP reutilizable con logging de cada petición
  - `helpers.py`: utilidades genéricas (conversión de precios, nombres de archivo, fecha/hora)
- **`datos/`**: datos de prueba externos
  - `usuarios.json`, `login_invalido.csv`, `productos.json`, `clientes.json`, `checkout.csv`, `api_posts.json`
- **`reports/`**: evidencias de ejecución
  - `reporte.html`, `ejecucion.log`, `screenshots/`
- `conftest.py`: fixtures del navegador, capturas en fallos y personalización del reporte
- `pytest.ini`: configuración de Pytest, marcadores, logging y reporte
- `requirements.txt`: dependencias del proyecto

### ¿Por qué esta estructura?

- **Los tests no conocen selectores.** Si cambia un botón en la web, se corrige **una sola vez** en su Page Object y todos los tests siguen funcionando.
- **Los datos no están en el código.** Para sumar un caso nuevo, por ejemplo otro login inválido, alcanza con agregar una fila al CSV, sin tocar Python.
- **Agregar una página o un test nuevo** es crear una clase en `pages/` o una función en `tests/`, reutilizando fixtures y utilidades existentes.

## ✅ Casos de prueba

**37 ejecuciones en total** (23 de UI y 14 de API), contando cada combinación de datos parametrizada.

### UI – Selenium WebDriver (`tests/ui/`)

| Test | Qué valida | Datos |
|---|---|---|
| `test_login_exitoso` | Redirección a `/inventory.html`, título "Swag Labs" y encabezado "Products" | `usuarios.json` |
| `test_login_invalido` ❌ | 5 escenarios negativos: bloqueado, contraseña incorrecta, usuario inexistente, usuario vacío y contraseña vacía | `login_invalido.csv` |
| `test_logout` | Cierre de sesión desde el menú lateral | — |
| `test_titulo_inventario` | Título de la pestaña y encabezado del catálogo | — |
| `test_productos_visibles` | Existencia de productos; nombre y precio del primero | — |
| `test_elementos_interfaz` | Menú, filtro de orden e ícono del carrito visibles | — |
| `test_ordenar_productos` | Orden A-Z, Z-A, precio menor a mayor y mayor a menor | `productos.json` |
| `test_agregar_primer_producto_al_carrito` | Contador de 0 a 1 y que el producto en el carrito sea el agregado | — |
| `test_agregar_varios_productos` | Contador y contenido del carrito con 1, 2 y 3 productos | `productos.json` |
| `test_eliminar_producto_del_carrito` | El carrito queda vacío y el contador desaparece | — |
| `test_checkout_completo` 🛒 | **Flujo E2E**: compra de 2 productos, subtotal = suma de precios, total = subtotal + impuesto y confirmación de la orden | `clientes.json` |
| `test_checkout_datos_obligatorios` ❌ | 3 escenarios negativos: falta nombre, apellido o código postal | `checkout.csv` |

### API – Requests (`tests/api/`)

| Test | Método | Qué valida |
|---|---|---|
| `test_listar_posts` | GET | 200, 100 posts y estructura/tipos de cada uno |
| `test_obtener_post_por_id` | GET | 3 ids parametrizados: contenido y autor correctos |
| `test_filtrar_posts_por_usuario` | GET | Query param `userId`: solo devuelve posts de ese usuario |
| `test_crear_post` | POST | 201, datos enviados presentes en la respuesta e id asignado |
| `test_actualizar_post` | PUT | 200 y contenido actualizado |
| `test_eliminar_post` | DELETE | 200 y cuerpo vacío |
| `test_post_inexistente_devuelve_404` ❌ | GET | Escenario de error: 3 ids inexistentes devuelven 404 |
| `test_tiempo_de_respuesta` | GET | No funcional: la respuesta llega en menos de 2 segundos |
| `test_flujo_encadenado_post_autor_comentarios` 🔗 | GET | Petición encadenada: post → su autor → sus comentarios |
| `test_flujo_encadenado_crear_y_eliminar` 🔗 | POST + DELETE | Se crea un post y con el id devuelto se elimina |

> JSONPlaceholder es una API de práctica: responde a POST/PUT/DELETE como si aplicara los cambios, pero no los guarda. Por eso el encadenamiento "crear y consultar" se valida con los recursos existentes.

## ⚙️ Instalación

**Requisitos previos:** Python 3.10 o superior, Git y Google Chrome. El driver de Chrome lo descarga automáticamente Selenium Manager.

```bash
# 1. Clonar el repositorio
git clone https://github.com/rafaeljosepa/proyecto-final-automation-testing-rafael-perez.git
cd proyecto-final-automation-testing-rafael-perez

# 2. Crear y activar el entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # Windows (PowerShell)
source .venv/bin/activate           # macOS / Linux

# 3. Instalar dependencias
pip install -r requirements.txt
```

## ▶️ Ejecución

Cada ejecución genera automáticamente el reporte HTML y el log en `reports/`.

```bash
# Todas las pruebas (UI + API)
pytest

# Solo UI o solo API (marcadores)
pytest -m ui
pytest -m api

# Solo las pruebas críticas (smoke)
pytest -m smoke

# Un archivo o un test puntual
pytest tests/ui/test_checkout.py
pytest tests/ui/test_login.py::test_logout

# Sin abrir la ventana del navegador (modo headless)
$env:HEADLESS="1"; pytest           # Windows (PowerShell)
HEADLESS=1 pytest                   # macOS / Linux
```

## 📊 Cómo interpretar los reportes

### Reporte HTML (`reports/reporte.html`)

Se abre con cualquier navegador.

1. **Encabezado y "Environment":** fecha de ejecución, versión de Python y plugins, sitio y API bajo prueba, y navegador usado.
2. **Summary:** totales de tests **Passed** (verde), **Failed** (rojo), **Skipped** y **Errors**, y la duración total. Haciendo clic en cada contador se filtra la tabla.
3. **Tabla de resultados:** una fila por test, con:
   - **Result:** estado del test.
   - **Test:** archivo y nombre. Entre corchetes figura el caso parametrizado, por ejemplo `test_login_invalido[usuario_bloqueado]`.
   - **Descripción:** qué valida el test, en lenguaje natural.
   - **Duration:** tiempo de ejecución.
4. **Detalle de un test:** al hacer clic en una fila se despliegan los **logs** de ese test y, si falló, el **mensaje del assert** (que muestra el valor esperado y el obtenido) y la **captura de pantalla** incrustada.

### Capturas de pantalla (`reports/screenshots/`)

Cuando un test de UI falla, se guarda automáticamente una captura con el **nombre del test y la fecha/hora**, por ejemplo `test_checkout_completo_20261127_213045.png`. La misma imagen queda adjunta en el reporte HTML.

### Log de ejecución (`reports/ejecucion.log`)

Registra los pasos clave con fecha, hora, nivel y origen: usuario con el que se inicia sesión (**nunca la contraseña**), productos agregados, totales del checkout, cada petición HTTP con su código de estado y duración, y la ruta de cada captura. Es el primer lugar donde mirar para depurar un fallo.

```
2026-11-27 21:30:12 [INFO] pages.login_page: Iniciando sesión con el usuario: 'standard_user'
2026-11-27 21:30:14 [INFO] tests.ui.test_checkout: Subtotal: $39.98 | Impuesto: $3.2 | Total: $43.18
2026-11-27 21:30:20 [INFO] utils.api_client: <-- 201 POST https://jsonplaceholder.typicode.com/posts (0.215s)
```

## 💡 Buenas prácticas aplicadas

- **Page Object Model** con una clase base que concentra esperas y acciones comunes.
- **Esperas explícitas** (`WebDriverWait`) en lugar de `time.sleep()`.
- **Tests independientes:** cada test de UI abre y cierra su propio navegador mediante fixtures, así que la falla de uno no afecta a los demás.
- **Parametrización con datos externos** (CSV/JSON) en lugar de datos fijos en el código.
- **Configuración centralizada** en `utils/config.py` y variables de entorno (`HEADLESS`, `CHROMEDRIVER_PATH`).
- **Asserts con mensajes descriptivos** que muestran el valor obtenido cuando algo falla.
- **Logs sin datos sensibles.**
- **Historial con ramas por funcionalidad** (`feature/*`, `docs/*`) fusionadas a `main` y mensajes con *Conventional Commits*.

## 👤 Autor

**Rafael Pérez** – QA Analyst / Engineer
[GitHub](https://github.com/rafaeljosepa) · [LinkedIn](https://www.linkedin.com/in/rafael-perez-4578ab272/)
