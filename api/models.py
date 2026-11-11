from datetime import datetime, timezone
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

class FormaPago(str, Enum):
    EFECTIVO = 'EFECTIVO'
    TRANSFERENCIA = 'TRANSFERENCIA'

class EstadoPedido(str, Enum):
    PENDIENTE = 'PENDIENTE'
    EN_PREPARACION = 'EN_PREPARACION'
    ENTREGADO = 'ENTREGADO'
    CANCELADO = 'CANCELADO'

class ProductoEtiqueta(SQLModel, table=True):
    producto_id: int | None = Field(default=None, foreign_key='producto.id', primary_key=True)
    etiqueta_id: int | None = Field(default=None, foreign_key='etiqueta.id', primary_key=True)

class Categoria(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True)
    descripcion: str = ''
    activo: bool = True
    productos: list['Producto'] = Relationship(back_populates='categoria')

class Etiqueta(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True)
    productos: list['Producto'] = Relationship(back_populates='etiquetas', link_model=ProductoEtiqueta)

class Producto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True)
    descripcion: str = ''
    precio: float
    stock: int = 0
    imagen_url: str | None = None
    categoria_id: int = Field(foreign_key='categoria.id')
    activo: bool = True
    categoria: Categoria = Relationship(back_populates='productos')
    etiquetas: list[Etiqueta] = Relationship(back_populates='productos', link_model=ProductoEtiqueta)
    detalles: list['DetallePedido'] = Relationship(back_populates='producto')

class Pedido(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    cliente_nombre: str
    direccion_entrega: str
    forma_pago: FormaPago
    notas: str | None = None
    estado: EstadoPedido = EstadoPedido.PENDIENTE
    total: float = 0
    fecha: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    detalles: list['DetallePedido'] = Relationship(back_populates='pedido')

class DetallePedido(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key='pedido.id')
    producto_id: int = Field(foreign_key='producto.id')
    nombre_producto: str
    precio_unitario: float
    cantidad: int
    subtotal: float
    pedido: Pedido = Relationship(back_populates='detalles')
    producto: Producto = Relationship(back_populates='detalles')
