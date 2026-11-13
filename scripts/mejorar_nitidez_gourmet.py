"""Reemplaza los 28 recortes borrosos por fotografías individuales de mayor detalle.

Las fotos originales están en web/img y ya se seleccionaron por producto. Esta
tarea NO amplía los recortes antiguos: toma las fotografías originales 800x600,
les aplica la misma corrección gourmet cálida y las exporta como WebP de 960x720.
Conserva los nombres gourmet-01.webp ... gourmet-28.webp para no tocar la API
ni las bases de datos de quienes ya descargaron el proyecto.
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import sys

ROOT = Path(__file__).resolve().parent.parent
CARPETA = ROOT / "web" / "img"

ORIGINALES = [
    ("Pizza muzzarella", "pizza-muzzarella.webp"),
    ("Pizza napolitana", "pizza-napolitana.webp"),
    ("Pizza fugazzeta", "pizza-fugazzeta.webp"),
    ("Pizza especial", "pizza-especial.webp"),
    ("Pizza cuatro quesos", "pizza-cuatro-quesos.webp"),
    ("Pizza calabresa", "pizza-calabresa.webp"),
    ("Pizza de rúcula", "pizza-rucula.webp"),
    ("Pizza margarita", "pizza-margarita.webp"),
    ("Hamburguesa clásica", "hamburguesa-clasica.webp"),
    ("Hamburguesa doble", "hamburguesa-doble.webp"),
    ("Hamburguesa veggie", "hamburguesa-veggie.webp"),
    ("Hamburguesa picante", "hamburguesa-picante.webp"),
    ("Hamburguesa BBQ", "hamburguesa-bbq.webp"),
    ("Hamburguesa cheddar", "hamburguesa-cheddar.webp"),
    ("Hamburguesa criolla", "hamburguesa-criolla.webp"),
    ("Hamburguesa con panceta", "hamburguesa-panceta.webp"),
    ("Agua mineral", "agua-mineral.webp"),
    ("Gaseosa cola", "gaseosa-cola.webp"),
    ("Limonada casera", "limonada-casera.webp"),
    ("Jugo de naranja", "jugo-naranja.webp"),
    ("Agua con gas", "agua-con-gas.webp"),
    ("Té frío", "te-frio.webp"),
    ("Flan casero", "flan-casero.webp"),
    ("Brownie", "brownie.webp"),
    ("Cheesecake", "cheesecake.webp"),
    ("Helado artesanal", "helado-artesanal.webp"),
    ("Chocotorta", "chocotorta.webp"),
    ("Ensalada de frutas", "ensalada-frutas.webp"),
]

def gourmet(origen: Path) -> Image.Image:
    with Image.open(origen) as src:
        imagen = ImageOps.exif_transpose(src).convert("RGB")
    if min(imagen.size) < 400:
        raise ValueError(f"Fuente demasiado pequeña: {origen.name}: {imagen.size}")
    imagen = ImageOps.fit(imagen, (960, 720), method=Image.Resampling.LANCZOS, centering=(0.5, 0.46))
    # Ajustes moderados y uniformes: el detalle original permanece intacto.
    imagen = ImageEnhance.Contrast(imagen).enhance(1.055)
    imagen = ImageEnhance.Color(imagen).enhance(1.085)
    # Temperatura ligeramente cálida, sin teñir las comidas de naranja.
    r, g, b = imagen.split()
    r = r.point(lambda v: min(255, round(v * 1.018)))
    b = b.point(lambda v: max(0, round(v * 0.985)))
    imagen = Image.merge("RGB", (r, g, b))
    imagen = imagen.filter(ImageFilter.UnsharpMask(radius=1.15, percent=115, threshold=3))
    return imagen

def exportar(img: Image.Image, destino: Path) -> int:
    from io import BytesIO
    for calidad in (86, 82, 78, 74, 70, 65, 60, 55, 50):
        output = BytesIO()
        img.save(output, format="WEBP", quality=calidad, method=6)
        if output.tell() < 195_000:
            destino.write_bytes(output.getvalue())
            return output.tell()
    raise ValueError(f"No se pudo llegar al límite de 200 KB: {destino}")

def main():
    errores = []
    for numero, (nombre, archivo) in enumerate(ORIGINALES, 1):
        src = CARPETA / archivo
        dest = CARPETA / f"gourmet-{numero:02}.webp"
        if not src.is_file():
            errores.append(f"{nombre}: no existe {src.name}")
            continue
        try:
            bytes_n = exportar(gourmet(src), dest)
            with Image.open(dest) as prueba:
                assert prueba.size == (960, 720)
            print(f"{numero:02}: {nombre} -> {dest.name}, 960x720, {bytes_n/1024:.1f} KB", flush=True)
        except Exception as exc:
            errores.append(f"{nombre}: {exc}")
    if errores:
        print("\n".join(errores), file=sys.stderr)
        raise SystemExit(1)
    assert len(ORIGINALES) == 28
    print("28/28 fotografías renovadas, nítidas y con formato gourmet uniforme.")

if __name__ == "__main__":
    main()
