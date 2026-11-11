# -*- coding: utf-8 -*-
"""
probar_api.py -- Autocorrección del Parcial 2: Food Store API.

Prueba la API por HTTP, sin levantar servidor y SIN tocar tu base real: cada grupo de
pruebas arma su propia base SQLite EN MEMORIA y la descarta al terminar. Se puede correr
las veces que quieras, desde la carpeta del proyecto:

    python probar_api.py                 todas las pruebas
    python probar_api.py --transaccion   demostración para el video, sobre tu base real
    python probar_api.py --ver-base      muestra lo que hay en tu base real

Cada línea dice [ OK ] o [FALLA], con el código esperado y el que llegó. Al final muestra
el total. Las pruebas son la misma lista de control para todos: que pasen todas no reemplaza
la corrección del código ni el video, pero si alguna falla, a tu entrega le falta algo.

NO modifiques este archivo.
"""

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA))

try:
    from fastapi.testclient import TestClient
    from sqlalchemy import event, text
    from sqlalchemy.pool import StaticPool
    from sqlmodel import Session, SQLModel, create_engine
except ImportError as error:
    sys.exit(f"Falta instalar dependencias ({error}). Corré: pip install -r requirements.txt")

try:
    import database
    import models  # noqa: F401  -- registra las tablas
    from database import get_session
    from main import app
except Exception as error:  # noqa: BLE001 -- al empezar, el proyecto puede no existir todavía
    sys.exit("No se pudo cargar el proyecto. Tienen que existir main.py (con la variable app), "
             f"database.py (con get_session) y models.py.\nError: {error!r}")

# raise_server_exceptions=False: si algo explota adentro, lo vemos como un 500 y seguimos.
client = TestClient(app, raise_server_exceptions=False)
resultados: list[tuple[str, bool]] = []
ENGINES: list = []

CATEGORIAS, ETIQUETAS, PRODUCTOS, PEDIDOS = "/categorias/", "/etiquetas/", "/productos/", "/pedidos/"


# ----------------------------------------------------------------------
# Herramientas
# ----------------------------------------------------------------------
def registrar(parte: str, descripcion: str, ok: bool, detalle: str = "") -> None:
    resultados.append((parte, ok))
    marca = "[ OK ]" if ok else "[FALLA]"
    print(f"{marca} {parte} - {descripcion}" + ("" if ok else f"   -> {detalle}"))


def http(parte, descripcion, respuesta, codigo, condicion=None):
    """Compara el código HTTP y, opcionalmente, una condición sobre el JSON."""
    ok = respuesta.status_code == codigo
    detalle = f"esperaba {codigo}, llegó {respuesta.status_code}: {respuesta.text[:160]}"
    if ok and condicion is not None:
        try:
            ok = bool(condicion(respuesta.json()))
            detalle = f"el código está bien, pero el cuerpo no: {respuesta.text[:200]}"
        except Exception as error:  # noqa: BLE001
            ok, detalle = False, f"error al revisar la respuesta: {error!r}"
    registrar(parte, descripcion, ok, detalle)


def sin_cuerpo(parte, descripcion, respuesta):
    ok = respuesta.status_code == 204 and respuesta.content == b""
    registrar(parte, descripcion, ok,
              f"esperaba 204 sin cuerpo, llegó {respuesta.status_code} con {respuesta.content[:80]!r}")


def comprobar(parte, descripcion, prueba, detalle="la condición no se cumplió"):
    try:
        ok = bool(prueba())
    except Exception as error:  # noqa: BLE001
        ok, detalle = False, repr(error)
    registrar(parte, descripcion, ok, detalle)


def bd_nueva():
    """Una base vacía en memoria y get_session apuntando a ella."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
    ENGINES.append(engine)
    SQLModel.metadata.create_all(engine)

    def sesion_de_prueba():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = sesion_de_prueba
    return engine


def id_de(respuesta, si_falla=999):
    """El id creado. Si el alta todavía no funciona, las pruebas siguientes dan [FALLA] sin cortarse."""
    try:
        return respuesta.json()["id"]
    except Exception:  # noqa: BLE001
        return si_falla


def categoria(nombre="Pizzas"):
    return id_de(client.post(CATEGORIAS, json={"nombre": nombre, "descripcion": "De prueba"}))


def producto(categoria_id, nombre="Pizza muzzarella", precio=1000.0, stock=10, **extra):
    datos = {"nombre": nombre, "descripcion": "Con salsa de tomate", "precio": precio,
             "stock": stock, "categoria_id": categoria_id, **extra}
    return id_de(client.post(PRODUCTOS, json=datos))


def stock_de(producto_id):
    try:
        return client.get(f"{PRODUCTOS}{producto_id}").json()["stock"]
    except Exception:  # noqa: BLE001
        return None


def pedido_body(*lineas, **extra):
    return {"cliente_nombre": "Ana Gómez", "direccion_entrega": "San Martín 1234",
            "forma_pago": "EFECTIVO",
            "detalles": [{"producto_id": p, "cantidad": c} for p, c in lineas], **extra}


class FallaSimulada(Exception):
    """Simula un corte en medio de la transacción, por ejemplo, que se caiga la conexión."""


class falla_en_segunda_linea:
    """Mientras dura el bloque, guardar la SEGUNDA línea de un pedido lanza FallaSimulada."""

    def __enter__(self):
        self.lineas = 0
        event.listen(models.DetallePedido, "before_insert", self._contar)
        return self

    def __exit__(self, *_):
        event.remove(models.DetallePedido, "before_insert", self._contar)

    def _contar(self, *_):
        self.lineas += 1
        if self.lineas == 2:
            raise FallaSimulada("Falla simulada al guardar la segunda línea del pedido")


# ----------------------------------------------------------------------
# Partes
# ----------------------------------------------------------------------
def parte_1_modelos():
    print("\n=== PARTE 1: tablas y relaciones (models.py) ===")
    P = "P1"
    tablas = SQLModel.metadata.tables
    for nombre in ("categoria", "etiqueta", "producto", "productoetiqueta", "pedido", "detallepedido"):
        comprobar(P, f"existe la tabla {nombre}", lambda n=nombre: n in tablas,
                  f"no está: revisá el nombre de la clase y table=True. Hay: {sorted(tablas)}")

    def fks(tabla):
        return {fk.target_fullname for fk in tablas[tabla].foreign_keys}

    comprobar(P, "producto tiene FK a categoria.id", lambda: "categoria.id" in fks("producto"))
    comprobar(P, "detallepedido tiene FK a pedido.id y a producto.id",
              lambda: {"pedido.id", "producto.id"} <= fks("detallepedido"))
    comprobar(P, "productoetiqueta tiene clave primaria compuesta (producto_id, etiqueta_id)",
              lambda: {c.name for c in tablas["productoetiqueta"].primary_key.columns}
              == {"producto_id", "etiqueta_id"})
    comprobar(P, "detallepedido guarda copia de nombre_producto y precio_unitario",
              lambda: {"nombre_producto", "precio_unitario", "cantidad", "subtotal"}
              <= set(tablas["detallepedido"].columns.keys()))


def parte_2_categorias():
    print("\n=== PARTE 2: categorías ===")
    P = "P2"
    bd_nueva()
    r = client.post(CATEGORIAS, json={"nombre": "Pizzas", "descripcion": "A la piedra"})
    http(P, "POST crea una categoría (201) con id y activo", r, 201,
         lambda j: j["id"] > 0 and j["nombre"] == "Pizzas" and j["activo"] is True)
    cat = id_de(r)
    http(P, "POST con nombre repetido en otras mayúsculas: 409",
         client.post(CATEGORIAS, json={"nombre": "PIZZAS"}), 409)
    http(P, "POST con nombre de 1 letra: 422", client.post(CATEGORIAS, json={"nombre": "P"}), 422)
    http(P, "GET lista las categorías", client.get(CATEGORIAS), 200,
         lambda j: isinstance(j, list) and len(j) == 1)
    http(P, "GET /{id} trae la lista productos", client.get(f"{CATEGORIAS}{cat}"), 200,
         lambda j: j["productos"] == [])
    http(P, "GET /{id} inexistente: 404", client.get(f"{CATEGORIAS}999"), 404)
    http(P, "PUT reemplaza los datos", client.put(f"{CATEGORIAS}{cat}", json={
        "nombre": "Pizzas caseras", "descripcion": "Nueva"}), 200,
        lambda j: j["nombre"] == "Pizzas caseras" and j["descripcion"] == "Nueva")
    http(P, "PUT con su propio nombre no es conflicto", client.put(f"{CATEGORIAS}{cat}", json={
        "nombre": "Pizzas caseras", "descripcion": "Otra"}), 200)
    otra = categoria("Bebidas")
    http(P, "PUT con el nombre de otra categoría: 409",
         client.put(f"{CATEGORIAS}{otra}", json={"nombre": "Pizzas caseras"}), 409)
    http(P, "PUT de un id inexistente: 404",
         client.put(f"{CATEGORIAS}999", json={"nombre": "Algo"}), 404)
    producto(cat)
    http(P, "DELETE con productos activos: 409", client.delete(f"{CATEGORIAS}{cat}"), 409)
    http(P, "DELETE hace baja lógica (200, activo false)", client.delete(f"{CATEGORIAS}{otra}"), 200,
         lambda j: j["activo"] is False)
    http(P, "la categoría dada de baja no se lista", client.get(CATEGORIAS), 200,
         lambda j: otra not in [c["id"] for c in j])
    http(P, "DELETE de una ya dada de baja: 409", client.delete(f"{CATEGORIAS}{otra}"), 409)
    http(P, "DELETE de un id inexistente: 404", client.delete(f"{CATEGORIAS}999"), 404)
    http(P, "una categoría dada de baja conserva su nombre: 409",
         client.post(CATEGORIAS, json={"nombre": "Bebidas"}), 409)

