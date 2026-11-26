"""
tests/api/test_posts_api.py
Pruebas de la API pública JSONPlaceholder (https://jsonplaceholder.typicode.com) con Requests.
Cubre GET, POST, PUT y DELETE; valida códigos de estado, estructura y contenido del JSON,
escenarios de error (404), tiempo de respuesta y un flujo de peticiones encadenadas.

Nota: JSONPlaceholder es una API de práctica; acepta POST/PUT/DELETE y responde como si
los aplicara, pero no persiste los cambios.
"""
import logging

import pytest

from utils.config import TIEMPO_MAXIMO_API
from utils.lector_datos import cargar_json

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.api

DATOS = cargar_json("api_posts.json")

# Estructura esperada de cada recurso: {campo: tipo}
ESQUEMA_POST = {"userId": int, "id": int, "title": str, "body": str}
ESQUEMA_USUARIO = {"id": int, "name": str, "username": str, "email": str}
ESQUEMA_COMENTARIO = {"postId": int, "id": int, "name": str, "email": str, "body": str}


def validar_esquema(objeto, esquema):
    """Verifica que el objeto JSON tenga todos los campos del esquema y con el tipo correcto."""
    for campo, tipo in esquema.items():
        assert campo in objeto, f"Falta el campo '{campo}' en la respuesta: {objeto}"
        assert isinstance(objeto[campo], tipo), \
            f"El campo '{campo}' debería ser {tipo.__name__}, es {type(objeto[campo]).__name__}"


def validar_respuesta_json(respuesta, codigo_esperado):
    """Valida el código de estado y que el cuerpo sea JSON; devuelve el cuerpo ya parseado."""
    assert respuesta.status_code == codigo_esperado, \
        f"Código {respuesta.status_code}, esperado {codigo_esperado}. Cuerpo: {respuesta.text[:200]}"
    assert "application/json" in respuesta.headers.get("Content-Type", ""), \
        f"La respuesta no es JSON: {respuesta.headers.get('Content-Type')}"
    return respuesta.json()


# ---------------------------------------------------------------------------
# GET
# ---------------------------------------------------------------------------
@pytest.mark.smoke
def test_listar_posts(api_client):
    """GET /posts devuelve 200 y una lista de 100 posts con la estructura correcta."""
    posts = validar_respuesta_json(api_client.get("/posts"), 200)

    assert isinstance(posts, list), f"Se esperaba una lista, se obtuvo {type(posts).__name__}"
    assert len(posts) == 100, f"Cantidad de posts: {len(posts)}"
    for post in posts:
        validar_esquema(post, ESQUEMA_POST)


@pytest.mark.parametrize("post_esperado", DATOS["posts_existentes"],
                         ids=[f"post_{p['id']}" for p in DATOS["posts_existentes"]])
def test_obtener_post_por_id(api_client, post_esperado):
    """GET /posts/{id} devuelve el post pedido con su autor correcto."""
    post = validar_respuesta_json(api_client.get(f"/posts/{post_esperado['id']}"), 200)

    validar_esquema(post, ESQUEMA_POST)
    assert post["id"] == post_esperado["id"], f"id obtenido: {post['id']}"
    assert post["userId"] == post_esperado["userId"], f"userId obtenido: {post['userId']}"
    assert post["title"].strip(), "El post no tiene título"


def test_filtrar_posts_por_usuario(api_client):
    """GET /posts?userId=X devuelve solo los posts de ese usuario."""
    usuario = DATOS["usuario_para_filtrar"]
    posts = validar_respuesta_json(api_client.get("/posts", params={"userId": usuario}), 200)

    assert len(posts) > 0, f"El usuario {usuario} no tiene posts"
    otros_autores = {p["userId"] for p in posts if p["userId"] != usuario}
    assert not otros_autores, f"El filtro devolvió posts de otros usuarios: {otros_autores}"


# ---------------------------------------------------------------------------
# POST / PUT / DELETE
# ---------------------------------------------------------------------------
@pytest.mark.smoke
def test_crear_post(api_client):
    """POST /posts devuelve 201 con los datos enviados y un id asignado."""
    nuevo_post = DATOS["nuevo_post"]
    creado = validar_respuesta_json(api_client.post("/posts", nuevo_post), 201)

    validar_esquema(creado, ESQUEMA_POST)
    for campo, valor in nuevo_post.items():
        assert creado[campo] == valor, f"Campo '{campo}': se envió '{valor}', se obtuvo '{creado[campo]}'"
    logger.info(f"Post creado con id {creado['id']}")


def test_actualizar_post(api_client):
    """PUT /posts/1 devuelve 200 con el contenido actualizado."""
    cambios = DATOS["post_actualizado"]
    actualizado = validar_respuesta_json(api_client.put(f"/posts/{cambios['id']}", cambios), 200)

    assert actualizado == cambios, f"Respuesta: {actualizado}, esperado: {cambios}"


def test_eliminar_post(api_client):
    """DELETE /posts/1 devuelve 200 y un cuerpo vacío."""
    cuerpo = validar_respuesta_json(api_client.delete("/posts/1"), 200)

    assert cuerpo == {}, f"Se esperaba un cuerpo vacío, se obtuvo: {cuerpo}"


# ---------------------------------------------------------------------------
# Escenarios de error y no funcionales
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("id_inexistente", DATOS["ids_inexistentes"],
                         ids=[f"id_{i}" for i in DATOS["ids_inexistentes"]])
def test_post_inexistente_devuelve_404(api_client, id_inexistente):
    """Escenario de error: pedir un post que no existe devuelve 404 y un cuerpo vacío."""
    cuerpo = validar_respuesta_json(api_client.get(f"/posts/{id_inexistente}"), 404)

    assert cuerpo == {}, f"Se esperaba un cuerpo vacío para el 404, se obtuvo: {cuerpo}"


def test_tiempo_de_respuesta(api_client):
    """No funcional: GET /posts/1 responde por debajo del umbral definido en la configuración."""
    respuesta = api_client.get("/posts/1")
    duracion = respuesta.elapsed.total_seconds()

    assert respuesta.status_code == 200
    assert duracion < TIEMPO_MAXIMO_API, f"La respuesta tardó {duracion:.2f}s (máximo {TIEMPO_MAXIMO_API}s)"


# ---------------------------------------------------------------------------
# Encadenamiento de peticiones
# ---------------------------------------------------------------------------
def test_flujo_encadenado_post_autor_comentarios(api_client):
    """Cada petición usa datos de la anterior: post -> su autor -> sus comentarios."""
    # 1. Obtener un post y tomar el id de su autor
    post = validar_respuesta_json(api_client.get("/posts/1"), 200)
    id_autor = post["userId"]
    logger.info(f"El post {post['id']} pertenece al usuario {id_autor}")

    # 2. Con ese userId, obtener los datos del autor
    autor = validar_respuesta_json(api_client.get(f"/users/{id_autor}"), 200)
    validar_esquema(autor, ESQUEMA_USUARIO)
    assert autor["id"] == id_autor, f"Se pidió el usuario {id_autor}, se obtuvo {autor['id']}"
    assert "@" in autor["email"], f"Email inválido: {autor['email']}"

    # 3. Con el id del post, obtener sus comentarios
    comentarios = validar_respuesta_json(api_client.get(f"/posts/{post['id']}/comments"), 200)
    assert len(comentarios) > 0, "El post no tiene comentarios"
    for comentario in comentarios:
        validar_esquema(comentario, ESQUEMA_COMENTARIO)
        assert comentario["postId"] == post["id"], f"Comentario de otro post: {comentario['postId']}"
    logger.info(f"Autor: {autor['name']} | Comentarios del post: {len(comentarios)}")


def test_flujo_encadenado_crear_y_eliminar(api_client):
    """Se crea un post y con el id devuelto se ejecuta su eliminación."""
    creado = validar_respuesta_json(api_client.post("/posts", DATOS["nuevo_post"]), 201)
    id_creado = creado["id"]

    respuesta_eliminacion = api_client.delete(f"/posts/{id_creado}")
    assert respuesta_eliminacion.status_code == 200, \
        f"No se pudo eliminar el post {id_creado}: código {respuesta_eliminacion.status_code}"
