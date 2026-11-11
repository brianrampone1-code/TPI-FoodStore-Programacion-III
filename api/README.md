# Food Store API — Parcial 2

API REST con FastAPI y SQLModel. Incluye seis tablas, relación N:N con tabla intermedia, categorías, etiquetas, productos, pedidos con varias líneas, transacciones, stock, estados y datos de ejemplo.

## Instalación (Python 3.10+)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate
pip install -r requirements.txt
python probar_api.py
python probar_api.py --transaccion
uvicorn main:app --reload
```

Documentación interactiva: http://127.0.0.1:8000/docs

Para ver la base real: `python probar_api.py --ver-base`.

**IMPORTANTE:** El código fue revisado sintácticamente, pero NO fue posible ejecutar las 128 pruebas en el entorno de preparación porque SQLModel no estaba instalado. Ejecutar `python probar_api.py` en el equipo de entrega, revisar los resultados y corregir cualquier fallo antes de presentar. No modificar `probar_api.py`.

## Arquitectura
- `models.py`: entidades SQLModel y relaciones.
- `schemas.py`: validaciones de entrada y salida.
- `service.py`: reglas de negocio, consultas, transacciones y datos de ejemplo.
- `router_*.py`: rutas HTTP, sin commits.
- `database.py`: motor, tablas y sesiones.
- `main.py`: aplicación y manejador de errores.

La creación de pedidos valida primero todas las líneas, guarda el pedido y los detalles, descuenta stock y ejecuta un solo `commit`. Ante una excepción ejecuta `rollback`.

## Entrega
No incluir `venv`, `__pycache__` ni `.db`. El video de defensa y su enlace público deben prepararse por separado.
