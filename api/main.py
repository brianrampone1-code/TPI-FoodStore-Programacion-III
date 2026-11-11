from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session
from database import crear_tablas, engine
from service import DomainError, cargar_datos_de_ejemplo
from router_categorias import router as categorias
from router_etiquetas import router as etiquetas
from router_productos import router as productos
from router_pedidos import router as pedidos

@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_tablas()
    with Session(engine) as session:
        cargar_datos_de_ejemplo(session)
    yield

app = FastAPI(title='Food Store API', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5500', 'http://127.0.0.1:5500'],
    allow_methods=['*'],
    allow_headers=['*'],
)
@app.exception_handler(DomainError)
async def error_de_dominio(request: Request, exc: DomainError):
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.message})
app.include_router(categorias)
app.include_router(etiquetas)
app.include_router(productos)
app.include_router(pedidos)
