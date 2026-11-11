from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from schemas import CategoriaCreate, CategoriaUpdate, CategoriaRead, CategoriaDetalle
import service as s
router = APIRouter(prefix='/categorias', tags=['Categorías'])
@router.get('/', response_model=list[CategoriaRead])
def listar(session: Session = Depends(get_session)): return s.categorias(session)
@router.get('/{id}', response_model=CategoriaDetalle)
def detalle(id: int, session: Session = Depends(get_session)): return s.categoria_detalle(session, id)
@router.post('/', response_model=CategoriaRead, status_code=201)
def crear(data: CategoriaCreate, session: Session = Depends(get_session)): return s.crear_categoria(session, data)
@router.put('/{id}', response_model=CategoriaRead)
def editar(id: int, data: CategoriaUpdate, session: Session = Depends(get_session)): return s.editar_categoria(session, id, data)
@router.delete('/{id}', response_model=CategoriaRead)
def borrar(id: int, session: Session = Depends(get_session)): return s.borrar_categoria(session, id)
