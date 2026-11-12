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
    'Pizza muzzarella': 'img/pizza-muzzarella.webp',
    'Pizza napolitana': 'img/pizza-napolitana.webp',
    'Pizza fugazzeta': 'img/pizza-fugazzeta.webp',
    'Pizza especial': 'img/pizza-especial.webp',
    'Hamburguesa clásica': 'img/hamburguesa-clasica.webp',
    'Hamburguesa doble': 'img/hamburguesa-doble.webp',
    'Hamburguesa veggie': 'img/hamburguesa-veggie.webp',
    'Hamburguesa picante': 'img/hamburguesa-picante.webp',
    'Agua mineral': 'img/agua-mineral.webp',
    'Gaseosa cola': 'img/gaseosa-cola.webp',
    'Flan casero': 'img/flan-casero.webp',
    'Brownie': 'img/brownie.webp',
    'Pizza cuatro quesos': 'img/pizza-cuatro-quesos.webp',
    'Pizza calabresa': 'img/pizza-calabresa.webp',
    'Pizza de rúcula': 'img/pizza-rucula.webp',
    'Pizza margarita': 'img/pizza-margarita.webp',
    'Hamburguesa BBQ': 'img/hamburguesa-bbq.webp',
    'Hamburguesa cheddar': 'img/hamburguesa-cheddar.webp',
    'Hamburguesa criolla': 'img/hamburguesa-criolla.webp',
    'Hamburguesa con panceta': 'img/hamburguesa-panceta.webp',
    'Limonada casera': 'img/limonada-casera.webp',
    'Jugo de naranja': 'img/jugo-naranja.webp',
    'Agua con gas': 'img/agua-con-gas.webp',
    'Té frío': 'img/te-frio.webp',
    'Cheesecake': 'img/cheesecake.webp',
    'Helado artesanal': 'img/helado-artesanal.webp',
    'Chocotorta': 'img/chocotorta.webp',
    'Ensalada de frutas': 'img/ensalada-frutas.webp',
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
