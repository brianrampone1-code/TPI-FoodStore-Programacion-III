"""Recorta las 28 fotografías individuales de la imagen gourmet aprobada.

La composición original (1122×1402) tiene cuatro secciones: pizzas,
hamburguesas, bebidas y postres. Esta versión comprimida mantiene
exactamente el mismo encuadre y se incluye en assets/.

Uso desde la raíz:
    python -m pip install pillow
    python scripts/recortar_catalogo_aprobado.py
"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "catalogo_gourmet_aprobado.avif"
DEST = ROOT / "web" / "img"

PIZZAS_X = [(25, 287), (300, 550), (559, 813), (824, 1085)]
BEBIDAS_X = [(22, 198), (208, 379), (389, 555), (561, 733), (743, 913), (919, 1085)]
POSTRES_X = [(22, 205), (216, 379), (387, 555), (560, 729), (734, 901), (909, 1085)]

def preparar():
    registros = []
    def sumar(nombres, xs, arriba, abajo):
        for nombre, (izq, der) in zip(nombres, xs):
            registros.append((nombre, (izq, arriba, der, abajo)))

    sumar(["Pizza muzzarella", "Pizza napolitana", "Pizza fugazzeta", "Pizza especial"], PIZZAS_X, 119, 241)
    sumar(["Pizza cuatro quesos", "Pizza calabresa", "Pizza de rúcula", "Pizza margarita"], PIZZAS_X, 286, 409)
    sumar(["Hamburguesa clásica", "Hamburguesa doble", "Hamburguesa veggie", "Hamburguesa picante"], PIZZAS_X, 520, 654)
    sumar(["Hamburguesa BBQ", "Hamburguesa cheddar", "Hamburguesa criolla", "Hamburguesa con panceta"], PIZZAS_X, 690, 823)
    sumar(["Agua mineral", "Gaseosa cola", "Limonada casera", "Jugo de naranja", "Agua con gas", "Té frío"], BEBIDAS_X, 937, 1059)
    sumar(["Flan casero", "Brownie", "Cheesecake", "Helado artesanal", "Chocotorta", "Ensalada de frutas"], POSTRES_X, 1180, 1310)
    return registros

def main():
    imagen = Image.open(SOURCE).convert("RGB")
    sx, sy = imagen.width / 1122, imagen.height / 1402
    DEST.mkdir(parents=True, exist_ok=True)
    registros = preparar()
    assert len(registros) == 28
    for numero, (nombre, (x0, y0, x1, y1)) in enumerate(registros, 1):
        caja = tuple(round(coord * factor) for coord, factor in zip((x0, y0, x1, y1), (sx, sy, sx, sy)))
        foto = imagen.crop(caja)
        foto = ImageOps.fit(foto, (600, 400), method=Image.Resampling.LANCZOS)
        salida = DEST / f"gourmet-{numero:02d}.webp"
        calidad = 82
        foto.save(salida, "WEBP", quality=calidad, method=6)
        while salida.stat().st_size > 190000 and calidad > 50:
            calidad -= 8
            foto.save(salida, "WEBP", quality=calidad, method=6)
        print(f"{numero:02d}: {nombre} → {salida.name} ({salida.stat().st_size} bytes)", flush=True)

if __name__ == "__main__":
    main()
