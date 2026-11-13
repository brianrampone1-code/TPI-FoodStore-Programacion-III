"""Recupera las 28 fotografías del catálogo gourmet EXACTO aprobado por el usuario.

No sustituye comidas ni usa imágenes de stock: recorta la composición original
guardada en assets/catalogo_gourmet_aprobado.avif.
Para mejorar la nitidez evita deformaciones y el agrandamiento excesivo:
conserva la proporción de cada recorte, aplica un enfoque moderado y limita la
salida a 200 KB. Las tarjetas de la web se ajustan a este encuadre panorámico.

Uso: python -m pip install Pillow
     python scripts/restaurar_imagenes_aprobadas.py
"""
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets/catalogo_gourmet_aprobado.avif"
DEST = ROOT / "web/img"

PIZZAS_X = [(25,287),(300,550),(559,813),(824,1085)]
BEBIDAS_X = [(22,198),(208,379),(389,555),(561,733),(743,913),(919,1085)]
POSTRES_X = [(22,205),(216,379),(387,555),(560,729),(734,901),(909,1085)]

def regiones():
    z = []
    for arriba, abajo in [(119,241),(286,409),(520,654),(690,823)]:
        for izquierda, derecha in PIZZAS_X:
            z.append((izquierda,arriba,derecha,abajo))
    for izquierda,derecha in BEBIDAS_X:
        z.append((izquierda,937,derecha,1059))
    for izquierda,derecha in POSTRES_X:
        z.append((izquierda,1180,derecha,1310))
    assert len(z) == 28
    return z

def main():
    with Image.open(SOURCE) as original:
        imagen = original.convert("RGB")
    esc_x = imagen.width / 1122
    esc_y = imagen.height / 1402
    DEST.mkdir(parents=True,exist_ok=True)
    for numero,(x0,y0,x1,y1) in enumerate(regiones(),1):
        caja = (round(x0*esc_x),round(y0*esc_y),round(x1*esc_x),round(y1*esc_y))
        foto = imagen.crop(caja)
        # No forzar todas las fotos a un lienzo 960x720:
        # eso había ampliado detalle no existente y generado borrosidad.
        # Una ampliación leve con LANCZOS mantiene la foto original.
        max_w = 520 if numero <= 16 else 440
        if foto.width > max_w:
            max_w = foto.width
        nuevo_h = round(foto.height * max_w / foto.width)
        if max_w != foto.width:
            foto = foto.resize((max_w,nuevo_h),Image.Resampling.LANCZOS)
        foto = ImageEnhance.Contrast(foto).enhance(1.06)
        foto = foto.filter(ImageFilter.UnsharpMask(radius=0.85,percent=135,threshold=2))
        destino = DEST / f"gourmet-{numero:02d}.webp"
        datos = None
        for calidad in (91,87,82,76,68,60):
            buf = BytesIO()
            foto.save(buf,"WEBP",quality=calidad,method=6)
            if buf.tell() < 195_000:
                datos=buf.getvalue()
                break
        if datos is None: raise RuntimeError(f"Imagen demasiado grande: {destino.name}")
        destino.write_bytes(datos)
        print(f"{numero:02d} Foto gourmet ORIGINAL: {foto.width}x{foto.height} · {len(datos)} bytes",flush=True)
    print("28/28 imágenes originales restauradas y enfocadas sin cambiar su contenido.",flush=True)

if __name__ == "__main__":
    main()
