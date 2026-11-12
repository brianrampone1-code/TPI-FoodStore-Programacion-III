"""Actualiza imágenes gourmet en una base existente sin borrar información.
Ejecutar desde api/: py actualizar_imagenes.py
"""
from sqlmodel import Session, select
from database import engine, crear_tablas
from models import Producto

IMAGENES = {
    'Pizza muzzarella': 'img/gourmet-01.webp',
    'Pizza napolitana': 'img/gourmet-02.webp',
    'Pizza fugazzeta': 'img/gourmet-03.webp',
    'Pizza especial': 'img/gourmet-04.webp',
    'Pizza cuatro quesos': 'img/gourmet-05.webp',
    'Pizza calabresa': 'img/gourmet-06.webp',
    'Pizza de rúcula': 'img/gourmet-07.webp',
    'Pizza margarita': 'img/gourmet-08.webp',
    'Hamburguesa clásica': 'img/gourmet-09.webp',
    'Hamburguesa doble': 'img/gourmet-10.webp',
    'Hamburguesa veggie': 'img/gourmet-11.webp',
    'Hamburguesa picante': 'img/gourmet-12.webp',
    'Hamburguesa BBQ': 'img/gourmet-13.webp',
    'Hamburguesa cheddar': 'img/gourmet-14.webp',
    'Hamburguesa criolla': 'img/gourmet-15.webp',
    'Hamburguesa con panceta': 'img/gourmet-16.webp',
    'Agua mineral': 'img/gourmet-17.webp',
    'Gaseosa cola': 'img/gourmet-18.webp',
    'Limonada casera': 'img/gourmet-19.webp',
    'Jugo de naranja': 'img/gourmet-20.webp',
    'Agua con gas': 'img/gourmet-21.webp',
    'Té frío': 'img/gourmet-22.webp',
    'Flan casero': 'img/gourmet-23.webp',
    'Brownie': 'img/gourmet-24.webp',
    'Cheesecake': 'img/gourmet-25.webp',
    'Helado artesanal': 'img/gourmet-26.webp',
    'Chocotorta': 'img/gourmet-27.webp',
    'Ensalada de frutas': 'img/gourmet-28.webp',
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
