from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from models import Categoria, Etiqueta, Producto, ProductoEtiqueta, Pedido, DetallePedido, EstadoPedido

class DomainError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code, self.message = status_code, message
        super().__init__(message)

def fallo(code, message):
    raise DomainError(code, message)

def unico(session, model, nombre, excluir=None):
    stmt = select(model).where(func.lower(model.nombre) == nombre.lower())
    if excluir is not None:
        stmt = stmt.where(model.id != excluir)
    if session.exec(stmt).first():
        fallo(409, 'El nombre ya existe')

def obtener(session, model, id):
    item = session.get(model, id)
    if item is None:
        fallo(404, 'No encontrado')
    return item

def categoria_activa(session, id):
    cat = obtener(session, Categoria, id)
    if not cat.activo:
        fallo(404, 'Categoría no disponible')
    return cat

def categorias(session):
    return session.exec(select(Categoria).where(Categoria.activo == True).order_by(Categoria.id)).all()

def categoria_detalle(session, id):
    stmt = select(Categoria).where(Categoria.id == id).options(selectinload(Categoria.productos))
    cat = session.exec(stmt).first()
    if not cat:
        fallo(404, 'Categoría no encontrada')
    return cat

def crear_categoria(session, data):
    unico(session, Categoria, data.nombre)
    item = Categoria(**data.model_dump())
    session.add(item); session.commit(); session.refresh(item)
    return item

def editar_categoria(session, id, data):
    item = obtener(session, Categoria, id)
    unico(session, Categoria, data.nombre, id)
    for k, v in data.model_dump().items(): setattr(item, k, v)
    session.add(item); session.commit(); session.refresh(item)
    return item

def borrar_categoria(session, id):
    item = obtener(session, Categoria, id)
    if not item.activo: fallo(409, 'Ya está dada de baja')
    if session.exec(select(Producto).where(Producto.categoria_id == id, Producto.activo == True)).first():
        fallo(409, 'La categoría tiene productos activos')
    item.activo = False
    session.add(item); session.commit(); session.refresh(item)
    return item

def etiquetas(session):
    return session.exec(select(Etiqueta).order_by(Etiqueta.id)).all()

def crear_etiqueta(session, data):
    unico(session, Etiqueta, data.nombre)
    item = Etiqueta(**data.model_dump())
    session.add(item); session.commit(); session.refresh(item)
    return item

def borrar_etiqueta(session, id):
    item = obtener(session, Etiqueta, id)
    if session.exec(select(ProductoEtiqueta).where(ProductoEtiqueta.etiqueta_id == id)).first():
        fallo(409, 'Etiqueta en uso')
    session.delete(item); session.commit()

def producto_detalle(session, id):
    stmt = select(Producto).where(Producto.id == id).options(selectinload(Producto.categoria), selectinload(Producto.etiquetas))
    item = session.exec(stmt).first()
    if not item: fallo(404, 'Producto no encontrado')
    return item

def crear_producto(session, data):
    categoria_activa(session, data.categoria_id)
    unico(session, Producto, data.nombre)
    item = Producto(**data.model_dump())
    session.add(item); session.commit(); session.refresh(item)
    return producto_detalle(session, item.id)

def editar_producto(session, id, data):
    item = obtener(session, Producto, id)
    cambios = data.model_dump(exclude_unset=True)
    if 'categoria_id' in cambios: categoria_activa(session, cambios['categoria_id'])
    if 'nombre' in cambios: unico(session, Producto, cambios['nombre'], id)
    for k, v in cambios.items(): setattr(item, k, v)
    session.add(item); session.commit()
    return producto_detalle(session, id)

def borrar_producto(session, id):
    item = obtener(session, Producto, id)
    if not item.activo: fallo(409, 'Ya está dado de baja')
    item.activo = False
    session.add(item); session.commit()
    return producto_detalle(session, id)

def listar_productos(session, q, categoria_id, etiqueta_id, solo_con_stock, skip, limit):
    stmt = select(Producto).where(Producto.activo == True)
    if q: stmt = stmt.where(or_(Producto.nombre.ilike(f'%{q}%'), Producto.descripcion.ilike(f'%{q}%')))
    if categoria_id: stmt = stmt.where(Producto.categoria_id == categoria_id)
    if etiqueta_id: stmt = stmt.join(ProductoEtiqueta, Producto.id == ProductoEtiqueta.producto_id).where(ProductoEtiqueta.etiqueta_id == etiqueta_id)
    if solo_con_stock: stmt = stmt.where(Producto.stock > 0)
    total = session.exec(select(func.count()).select_from(stmt.subquery())).one()
    items = session.exec(stmt.options(selectinload(Producto.categoria), selectinload(Producto.etiquetas)).order_by(Producto.id).offset(skip).limit(limit)).all()
    return {'total': total, 'items': items}

def asociar_etiqueta(session, id, etiqueta_id):
    producto_detalle(session, id)
    obtener(session, Etiqueta, etiqueta_id)
    if session.get(ProductoEtiqueta, (id, etiqueta_id)):
        fallo(409, 'Etiqueta repetida')
    session.add(ProductoEtiqueta(producto_id=id, etiqueta_id=etiqueta_id)); session.commit()
    return producto_detalle(session, id)

def quitar_etiqueta(session, id, etiqueta_id):
    producto_detalle(session, id)
    link = session.get(ProductoEtiqueta, (id, etiqueta_id))
    if not link: fallo(404, 'Asociación no encontrada')
    session.delete(link); session.commit()

def pedido_detalle(session, id):
    stmt = select(Pedido).where(Pedido.id == id).options(selectinload(Pedido.detalles))
    item = session.exec(stmt).first()
    if not item: fallo(404, 'Pedido no encontrado')
    return item

def crear_pedido(session, data):
    # Primera pasada: validar todas las líneas sin cambiar nada.
    vistos, lineas, total = set(), [], 0.0
    for detalle in data.detalles:
        if detalle.producto_id in vistos: fallo(409, 'Producto repetido en el pedido')
        vistos.add(detalle.producto_id)
        producto = session.get(Producto, detalle.producto_id)
        if not producto or not producto.activo: fallo(404, 'Producto no disponible')
        if producto.stock < detalle.cantidad: fallo(409, 'Stock insuficiente')
        subtotal = round(producto.precio * detalle.cantidad, 2)
        lineas.append((producto, detalle.cantidad, subtotal))
        total += subtotal
    # Segunda pasada: todo se guarda en la misma transacción.
    pedido = Pedido(**data.model_dump(exclude={'detalles'}), total=round(total, 2))
    try:
        session.add(pedido)
        session.flush()
        for producto, cantidad, subtotal in lineas:
            producto.stock -= cantidad
            session.add(producto)
            session.add(DetallePedido(pedido_id=pedido.id, producto_id=producto.id,
                       nombre_producto=producto.nombre, precio_unitario=producto.precio,
                       cantidad=cantidad, subtotal=subtotal))
        session.commit()
    except Exception:
        session.rollback()
        raise
    return pedido_detalle(session, pedido.id)

def listar_pedidos(session, estado, skip, limit):
    stmt = select(Pedido)
    if estado is not None: stmt = stmt.where(Pedido.estado == estado)
    total = session.exec(select(func.count()).select_from(stmt.subquery())).one()
    items = session.exec(stmt.options(selectinload(Pedido.detalles)).order_by(Pedido.id.desc()).offset(skip).limit(limit)).all()
    return {'total': total, 'items': items}

def cambiar_estado(session, id, nuevo):
    pedido = pedido_detalle(session, id)
    validos = {EstadoPedido.PENDIENTE: {EstadoPedido.EN_PREPARACION, EstadoPedido.CANCELADO},
               EstadoPedido.EN_PREPARACION: {EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO}}
    if nuevo not in validos.get(pedido.estado, set()): fallo(409, 'Transición inválida')
    try:
        if nuevo == EstadoPedido.CANCELADO:
            for detalle in pedido.detalles:
                producto = obtener(session, Producto, detalle.producto_id)
                producto.stock += detalle.cantidad
                session.add(producto)
        pedido.estado = nuevo
        session.add(pedido); session.commit()
    except Exception:
        session.rollback(); raise
    return pedido_detalle(session, id)

def resumen(session):
    pedidos = session.exec(select(Pedido)).all()
    return {'pendientes': sum(p.estado == EstadoPedido.PENDIENTE for p in pedidos),
            'en_preparacion': sum(p.estado == EstadoPedido.EN_PREPARACION for p in pedidos),
            'entregados': sum(p.estado == EstadoPedido.ENTREGADO for p in pedidos),
            'cancelados': sum(p.estado == EstadoPedido.CANCELADO for p in pedidos),
            'ingresos_entregados': round(sum(p.total for p in pedidos if p.estado == EstadoPedido.ENTREGADO), 2)}

def cargar_datos_de_ejemplo(session):
    if session.exec(select(Categoria)).first(): return
    categorias_seed = [Categoria(nombre=n, descripcion=d) for n,d in [
        ('Pizzas','Pizzas artesanales'),('Hamburguesas','Hamburguesas caseras'),
        ('Bebidas','Bebidas frías'),('Postres','Dulces y postres')]]
    etiquetas_seed = [Etiqueta(nombre=n) for n in ('Vegetariano','Sin TACC','Picante')]
    session.add_all(categorias_seed + etiquetas_seed); session.flush()
    datos = [
        ('Pizza muzzarella', 9200, 8, 0, [0]),('Pizza napolitana', 10500, 5, 0, [0]),
        ('Pizza fugazzeta', 11200, 6, 0, [0]),('Pizza especial', 12900, 0, 0, []),
        ('Hamburguesa clásica', 7800, 12, 1, []),('Hamburguesa doble', 9900, 7, 1, []),
        ('Hamburguesa veggie', 8500, 4, 1, [0]),('Hamburguesa picante', 9300, 3, 1, [2]),
        ('Agua mineral', 1800, 25, 2, [1]),('Gaseosa cola', 2300, 20, 2, []),
        ('Flan casero', 4100, 9, 3, [0]),('Brownie', 4900, 0, 3, []),
        ('Pizza cuatro quesos', 13200, 8, 0, [0]),
        ('Pizza calabresa', 12600, 4, 0, []),
        ('Pizza de rúcula', 13500, 5, 0, [0]),
        ('Pizza margarita', 11500, 7, 0, [0]),
        ('Hamburguesa BBQ', 10800, 10, 1, []),
        ('Hamburguesa cheddar', 10700, 6, 1, []),
        ('Hamburguesa criolla', 11400, 5, 1, []),
        ('Hamburguesa con panceta', 11900, 3, 1, []),
        ('Limonada casera', 2800, 14, 2, []),
        ('Jugo de naranja', 3100, 12, 2, []),
        ('Agua con gas', 1900, 18, 2, []),
        ('Té frío', 2500, 11, 2, []),
        ('Cheesecake', 5600, 7, 3, []),
        ('Helado artesanal', 4600, 13, 3, []),
        ('Chocotorta', 5900, 9, 3, []),
        ('Ensalada de frutas', 4400, 8, 3, [0])]
    imagenes = {
        'Pizza muzzarella': 'img/pizza-margherita.webp',
        'Pizza napolitana': 'img/pizza-napolitana.webp',
        'Pizza fugazzeta': 'img/pizza-cuatro-quesos.webp',
        'Pizza especial': 'img/pizza-cuatro-quesos.webp',
        'Hamburguesa clásica': 'img/hamburguesa-clasica.webp',
        'Hamburguesa doble': 'img/hamburguesa-doble.webp',
        'Hamburguesa veggie': 'img/hamburguesa-veggie.webp',
        'Hamburguesa picante': 'img/hamburguesa-doble.webp',
        'Agua mineral': 'img/bebidas-artesanales.webp',
        'Gaseosa cola': 'img/bebidas-artesanales.webp',
        'Flan casero': 'img/postres-cremosos.webp',
        'Brownie': 'img/postres-chocolate.webp',
        'Pizza cuatro quesos': 'img/pizza-cuatro-quesos.webp',
        'Pizza calabresa': 'img/pizza-napolitana.webp',
        'Pizza de rúcula': 'img/pizza-rucula.webp',
        'Pizza margarita': 'img/pizza-margherita.webp',
        'Hamburguesa BBQ': 'img/hamburguesa-doble.webp',
        'Hamburguesa cheddar': 'img/hamburguesa-doble.webp',
        'Hamburguesa criolla': 'img/hamburguesa-clasica.webp',
        'Hamburguesa con panceta': 'img/hamburguesa-doble.webp',
        'Limonada casera': 'img/bebidas-artesanales.webp',
        'Jugo de naranja': 'img/bebidas-artesanales.webp',
        'Agua con gas': 'img/bebidas-artesanales.webp',
        'Té frío': 'img/bebidas-artesanales.webp',
        'Cheesecake': 'img/postres-cremosos.webp',
        'Helado artesanal': 'img/postres-chocolate.webp',
        'Chocotorta': 'img/postres-chocolate.webp',
        'Ensalada de frutas': 'img/postres-cremosos.webp',
    }
    for n, precio, stock, cat, tags in datos:
        p = Producto(nombre=n, descripcion=f'Elaboración propia: {n.lower()}', precio=precio,
                     stock=stock, categoria_id=categorias_seed[cat].id,
                     imagen_url=imagenes.get(n))
        p.etiquetas = [etiquetas_seed[i] for i in tags]
        session.add(p)
    session.commit()
