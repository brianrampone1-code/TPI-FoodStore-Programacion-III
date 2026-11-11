"""Descarga fotos gourmet de Unsplash y las optimiza como WebP livianas.

Uso: python scripts/descargar_imagenes.py
Requiere Pillow y acceso a Internet. Solo se ejecuta en CI para dejar las
fotografías guardadas en web/img; la página no depende de Internet al abrirse.
"""
from pathlib import Path
from io import BytesIO
from urllib.request import Request, urlopen
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "web" / "img"
DEST.mkdir(parents=True, exist_ok=True)

# Fotos gastronómicas con composición editorial, servidas por Unsplash.
FOTOS = {
    "pizza-margherita.webp": "photo-1574071318508-1cdbab80d002",
    "pizza-napolitana.webp": "photo-1513104890138-7c749659a591",
    "pizza-cuatro-quesos.webp": "photo-1565299624946-b28f40a0ae38",
    "pizza-rucula.webp": "photo-1593560708920-61dd98c46a4e",
    "hamburguesa-clasica.webp": "photo-1568901346375-23c9450c58cd",
    "hamburguesa-doble.webp": "photo-1550547660-d9450f859349",
    "hamburguesa-veggie.webp": "photo-1520072959219-c595dc870360",
    "bebidas-artesanales.webp": "photo-1544145945-f90425340c7e",
    "postres-cremosos.webp": "photo-1488477181946-6428a0291777",
    "postres-chocolate.webp": "photo-1551024506-0bccd828d307",
}

def main():
    for archivo, codigo in FOTOS.items():
        url = f"https://images.unsplash.com/{codigo}?auto=format&fit=crop&w=960&h=720&q=85"
        req = Request(url, headers={"User-Agent": "FoodStore-UTN/1.0"})
        with urlopen(req, timeout=35) as response:
            datos = response.read()
        imagen = Image.open(BytesIO(datos)).convert("RGB")
        imagen = ImageOps.fit(imagen, (960, 720), method=Image.Resampling.LANCZOS)
        destino = DEST / archivo
        imagen.save(destino, "WEBP", quality=78, method=6)
        print(f"{archivo}: {destino.stat().st_size} bytes", flush=True)

if __name__ == "__main__":
    main()
