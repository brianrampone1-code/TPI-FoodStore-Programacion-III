from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from database import get_session
from models import EstadoPedido
from schemas import PedidoCreate, PedidoRead, PedidosPaginados, EstadoUpdate, ResumenRead
import service as s
router = APIRouter(prefix='/pedidos', tags=['Pedidos'])
@router.post('/', response_model=PedidoRead, status_code=201)
def crear(data: PedidoCreate, session: Session = Depends(get_session)): return s.crear_pedido(session, data)
@router.get('/', response_model=PedidosPaginados)
def listar(estado: EstadoPedido | None = None, skip: int = Query(default=0, ge=0),
           limit: int = Query(default=10, ge=1, le=50), session: Session = Depends(get_session)):
    return s.listar_pedidos(session, estado, skip, limit)
@router.get('/resumen', response_model=ResumenRead)
def resumen(session: Session = Depends(get_session)): return s.resumen(session)
@router.get('/{id}', response_model=PedidoRead)
def detalle(id: int, session: Session = Depends(get_session)): return s.pedido_detalle(session, id)
@router.patch('/{id}/estado', response_model=PedidoRead)
def estado(id: int, data: EstadoUpdate, session: Session = Depends(get_session)):
    return s.cambiar_estado(session, id, data.estado)
