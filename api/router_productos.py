from fastapi import APIRouter, Depends, Query, Response
from sqlmodel import Session
from database import get_session
from schemas import ProductoCreate, ProductoUpdate, ProductoRead, ProductosPaginados
import service as s
router = APIRouter(prefix='/productos', tags=['Productos'])
@router.get('/', response_model=ProductosPaginados)
def listar(q: str | None = Query(default=None, min_length=1, max_length=50),
           categoria_id: int | None = Query(default=None, gt=0),
           etiqueta_id: int | None = Query(default=None, gt=0),
           solo_con_stock: bool = False, skip: int = Query(default=0, ge=0),
           limit: int = Query(default=10, ge=1, le=50), session: Session = Depends(get_session)):
    return s.listar_productos(session, q, categoria_id, etiqueta_id, solo_con_stock, skip, limit)
@router.get('/{id}', response_model=ProductoRead)
def detalle(id: int, session: Session = Depends(get_session)): return s.producto_detalle(session, id)
@router.post('/', response_model=ProductoRead, status_code=201)
def crear(data: ProductoCreate, session: Session = Depends(get_session)): return s.crear_producto(session, data)
@router.patch('/{id}', response_model=ProductoRead)
def editar(id: int, data: ProductoUpdate, session: Session = Depends(get_session)): return s.editar_producto(session, id, data)
@router.delete('/{id}', response_model=ProductoRead)
def borrar(id: int, session: Session = Depends(get_session)): return s.borrar_producto(session, id)
@router.post('/{id}/etiquetas/{etiqueta_id}', response_model=ProductoRead, status_code=201)
def asociar(id: int, etiqueta_id: int, session: Session = Depends(get_session)): return s.asociar_etiqueta(session, id, etiqueta_id)
@router.delete('/{id}/etiquetas/{etiqueta_id}', status_code=204)
def quitar(id: int, etiqueta_id: int, session: Session = Depends(get_session)):
    s.quitar_etiqueta(session, id, etiqueta_id)
    return Response(status_code=204)
