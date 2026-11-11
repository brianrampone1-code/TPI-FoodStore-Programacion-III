"""Actualiza imágenes de los productos existentes sin borrar la base de datos.

Ejecutar desde la carpeta api/ con:
    py actualizar_imagenes.py

No cambia nombres, precios ni stock. Solo actualiza imagen_url de los 28
productos iniciales, si se encuentran por nombre. Conserva productos creados
manualmente y no interviene en las 128 pruebas de API.
"""
from sqlmodel import Session, select
from database import engine, crear_tablas
from models import Producto

IMAGENES = {
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

def main():
    crear_tablas()
    actualizados = 0
    with Session(engine) as sesion:
        for producto in sesion.exec(select(Producto)).all():
            nueva = IMAGENES.get(producto.nombre)
            if nueva and nueva != producto.imagen_url:
                producto.imagen_url = nueva
                sesion.add(producto)
                actualizados += 1
        sesion.commit()
    print(f'Imágenes actualizadas: {actualizados}. No se borró ningún producto.')

if __name__ == '__main__':
    main()
