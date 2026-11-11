from datetime import datetime
from sqlmodel import SQLModel, Field
from models import FormaPago, EstadoPedido

class CategoriaBase(SQLModel):
    nombre: str = Field(min_length=2, max_length=50)
    descripcion: str = Field(default='', max_length=200)
class CategoriaCreate(CategoriaBase): pass
class CategoriaUpdate(CategoriaBase): pass
class CategoriaRead(CategoriaBase):
    id: int
    activo: bool
class CategoriaDetalle(CategoriaRead):
    productos: list['ProductoSimple'] = Field(default_factory=list)

class EtiquetaBase(SQLModel):
    nombre: str = Field(min_length=2, max_length=30)
class EtiquetaCreate(EtiquetaBase): pass
class EtiquetaRead(EtiquetaBase):
    id: int

class ProductoBase(SQLModel):
    nombre: str = Field(min_length=3, max_length=60)
    descripcion: str = Field(default='', max_length=200)
    precio: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    imagen_url: str | None = Field(default=None, max_length=255)
    categoria_id: int = Field(gt=0)
class ProductoCreate(ProductoBase): pass
class ProductoUpdate(SQLModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=60)
    descripcion: str | None = Field(default=None, max_length=200)
    precio: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    imagen_url: str | None = Field(default=None, max_length=255)
    categoria_id: int | None = Field(default=None, gt=0)
class ProductoSimple(ProductoBase):
    id: int
    activo: bool
class ProductoRead(ProductoSimple):
    categoria: CategoriaRead
    etiquetas: list[EtiquetaRead] = Field(default_factory=list)
class ProductosPaginados(SQLModel):
    total: int
    items: list[ProductoRead]

class DetalleCreate(SQLModel):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(ge=1)
class PedidoBase(SQLModel):
    cliente_nombre: str = Field(min_length=3, max_length=80)
    direccion_entrega: str = Field(min_length=5, max_length=200)
    forma_pago: FormaPago
    notas: str | None = Field(default=None, max_length=200)
class PedidoCreate(PedidoBase):
    detalles: list[DetalleCreate] = Field(min_length=1)
class DetalleRead(SQLModel):
    id: int
    producto_id: int
    nombre_producto: str
    precio_unitario: float
    cantidad: int
    subtotal: float
class PedidoRead(PedidoBase):
    id: int
    estado: EstadoPedido
    total: float
    fecha: datetime
    detalles: list[DetalleRead]
class PedidosPaginados(SQLModel):
    total: int
    items: list[PedidoRead]
class EstadoUpdate(SQLModel):
    estado: EstadoPedido
class ResumenRead(SQLModel):
    pendientes: int
    en_preparacion: int
    entregados: int
    cancelados: int
    ingresos_entregados: float
