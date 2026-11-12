# Food Store — TPI Programación III

**Brian Rampone · UTN Facultad Regional Mendoza**

Proyecto HTML, CSS y JavaScript conectado con una API de productos, categorías, etiquetas y pedidos implementada en FastAPI / SQLModel.

## Ejecutar

Descargá el repositorio con **Code → Download ZIP**, extraelo y abrí la carpeta interior del proyecto en Visual Studio Code.

**Terminal 1 — API**
```powershell
cd api
py -m pip install -r requirements.txt
py -m uvicorn main:app --reload
```

**Terminal 2 — Web**
```powershell
cd web
py -m http.server 5500
```

Abrir:
- [Catálogo](http://localhost:5500)
- [Listado paginado](http://localhost:5500/productos.html)
- [Nuevo producto](http://localhost:5500/nuevo-producto.html)
- [Swagger de la API](http://127.0.0.1:8000/docs)

**No abrir el HTML con doble clic**: los módulos ES deben servirse por HTTP. CORS permite solamente los orígenes de la web en el puerto 5500.

## Funcionalidades

- Tarjetas de productos creadas desde los datos de `GET /productos/`.
- Categorías consultadas desde `GET /categorias/` y filtro remoto con `categoria_id`.
- Carga, lista vacía, error y botón Reintentar.
- Tabla de administración con paginado real por `skip` y `limit`.
- **Formulario de alta en página independiente** con `POST /productos/` y validaciones HTML, JavaScript y servidor (409, 404 y 422).
- Después de un alta exitosa, redirección con el ID y recarga de la lista desde la API.
- Las **28 fotos gourmet aprobadas** se recortan del catálogo gráfico original, conservando una estética cálida y consistente. Cada producto tiene un WebP único: `web/img/gourmet-01.webp` a `gourmet-28.webp`.
- Interfaz responsive, módulos JavaScript y textos creados mediante `textContent`.

## Si ya habías ejecutado una versión anterior

La base `api/foodstore.db` no se incluye en GitHub (y **no hay que borrarla**). Si ya tenías productos cargados, para actualizar sus imágenes sin perder productos, precios ni stock, ejecutá **una vez**, desde la carpeta `api`:

```powershell
py actualizar_imagenes.py
```

Después recargá el catálogo con **Ctrl + F5**. Si descargás el proyecto de cero, la API inicializa automáticamente los 28 productos con las fotos nuevas.

## Pruebas y entrega

La suite original `api/probar_api.py` permanece en el repositorio. **Resultado confirmado: 128/128 pruebas superadas** en GitHub Actions, con Python 3.11 y dependencias de `api/requirements.txt`. El workflow está en `.github/workflows/tests.yml`.

Para verificar localmente:

```powershell
cd api
py probar_api.py
py probar_api.py --ver-base
```

[Ver una ejecución exitosa de las 128 pruebas](https://github.com/brianrampone1-code/TPI-FoodStore-Programacion-III/actions/runs/43123562985).

El video de defensa obligatorio dura entre 5 y 10 minutos y debe demostrar un alta real en la base de datos, las tres capas de validación, filtro y paginado, errores y CORS.

GitHub Pages publica sitios estáticos pero no ejecuta una API Python ni una base SQLite. Para probar la aplicación completa, mantené encendidos ambos servidores.

## Créditos de imágenes

Las nuevas fotos provienen del catálogo gourmet original generado y aprobado en esta conversación. El archivo comprimido de origen se guarda en `assets/catalogo_gourmet_aprobado.avif` y se recorta con `scripts/recortar_catalogo_aprobado.py`.

### Orden y actualización de imágenes
El catálogo muestra las secciones **Pizzas → Hamburguesas → Bebidas → Postres**. 
Si ya tenés una base de datos creada, sin borrarla, ejecutá desde `api/`: `py actualizar_imagenes.py`. 
Ese script conserva precios, stock, pedidos y productos nuevos.
