# Food Store — TPI Programación III

**Brian Rampone · UTN Facultad Regional Mendoza**

Proyecto HTML, CSS y JavaScript conectado con una API de productos, categorías, etiquetas y pedidos implementada en FastAPI / SQLModel.

## Ejecutar

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

Abrir http://localhost:5500 para el catálogo, http://localhost:5500/productos.html para el listado y formulario de alta, y http://127.0.0.1:8000/docs para la documentación de API.

**No abrir con doble clic**: los módulos ES deben servirse por HTTP. CORS permite solamente los orígenes de la web en el puerto 5500.

## Funcionalidades

- Tarjetas de productos creadas desde los datos de `GET /productos/`.
- Categorías consultadas desde `GET /categorias/` y filtro remoto con `categoria_id`.
- Carga, lista vacía, error y botón Reintentar.
- Tabla de administración con paginado real por `skip` y `limit`.
- Alta de productos con `POST /productos/` y validaciones HTML, JavaScript y servidor.
- Interfaz responsive, módulos JavaScript y textos creados mediante `textContent`.
- 28 productos iniciales, distribuidos en cuatro categorías.

## Pruebas y entrega

**Pendiente:** incorporar `api/probar_api.py` original y los materiales auxiliares que están incluidos en el ZIP de entrega. No se ha verificado aquí el requisito de 128/128 pruebas, por lo que este repositorio no debe considerarse todavía la entrega final.

El video obligatorio dura entre 5 y 10 minutos y debe demostrar creación real en la base de datos, validaciones, filtro y paginado, errores y CORS.

GitHub Pages publica sitios estáticos pero no ejecuta una API Python ni una base de datos SQLite.
