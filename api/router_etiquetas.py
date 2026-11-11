from fastapi import APIRouter, Depends, Response
from sqlmodel import Session
from database import get_session
from schemas import EtiquetaCreate, EtiquetaRead
import service as s
router = APIRouter(prefix='/etiquetas', tags=['Etiquetas'])
@router.get('/', response_model=list[EtiquetaRead])
def listar(session: Session = Depends(get_session)): return s.etiquetas(session)
@router.post('/', response_model=EtiquetaRead, status_code=201)
def crear(data: EtiquetaCreate, session: Session = Depends(get_session)): return s.crear_etiqueta(session, data)
@router.delete('/{id}', status_code=204)
def borrar(id: int, session: Session = Depends(get_session)):
    s.borrar_etiqueta(session, id)
    return Response(status_code=204)
