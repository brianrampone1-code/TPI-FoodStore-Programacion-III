"""Sustituye fotos demasiado genéricas por imágenes exactas de Wikimedia Commons."""
from io import BytesIO
from pathlib import Path
import html
import json
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "web" / "img"
CREDITOS = ROOT / "FOTOS_CREDITOS.md"

# Nombre del producto, archivo destino, imagen exacta en Wikimedia Commons.
CURADAS = [
    ("Pizza muzzarella", "pizza-muzzarella.webp", "Pizza argentina con mozzarella, aceitunas mendocinas y orégano.jpg"),
    ("Pizza cuatro quesos", "pizza-cuatro-quesos.webp", "Four cheese pizza.jpg"),
    ("Jugo de naranja", "jugo-naranja.webp", "Glass of Fresh Orange Juice.jpg"),
    ("Chocotorta", "chocotorta.webp", "Chocotorta.jpg"),
]

def consultar(nombre):
    api = "https://commons.wikimedia.org/w/api.php?" + urlencode({
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iiurlwidth": "960",
        "titles": "File:" + nombre,
    })
    req = Request(api, headers={"User-Agent": "FoodStoreEducationalProject/1.0 (coursework; email: noreply@example.com)"})
    with urlopen(req, timeout=40) as resp:
        data = json.load(resp)
    pagina = next(iter(data["query"]["pages"].values()))
    if "imageinfo" not in pagina:
        raise ValueError("No existe la fotografía: " + nombre)
    info = pagina["imageinfo"][0]
    return info

def descargar(info, destino):
    url = info.get("thumburl") or info["url"]
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; FoodStoreCoursework/1.0)"})
    with urlopen(req, timeout=45) as resp:
        imagen = Image.open(BytesIO(resp.read(15_000_000))).convert("RGB")
    imagen = ImageOps.fit(imagen, (800, 600), method=Image.Resampling.LANCZOS)
    for calidad in [76, 65, 54, 42]:
        salida = BytesIO()
        imagen.save(salida, "WEBP", quality=calidad, method=5)
        if salida.tell() < 195_000:
            destino.write_bytes(salida.getvalue())
            return
    raise ValueError("Imagen demasiado pesada")

def main():
    lineas = CREDITOS.read_text(encoding="utf-8").splitlines()
    for producto, archivo, nombre_foto in CURADAS:
        print("Corrigiendo", producto, "con", nombre_foto, flush=True)
        info = consultar(nombre_foto)
        descargar(info, DEST / archivo)
        meta = info.get("extmetadata", {})
        autor = meta.get("Artist", {}).get("value", "Autor de Wikimedia Commons")
        # Artist puede contener etiquetas HTML simples: evitamos inyectarlas en el Markdown.
        import re
        autor = html.unescape(re.sub(r"<[^>]+>", "", autor)).strip() or "Autor de Wikimedia Commons"
        licencia = meta.get("LicenseShortName", {}).get("value", "CC")
        pagina = "https://commons.wikimedia.org/wiki/File:" + quote(nombre_foto.replace(" ", "_"))
        nueva = f"- **{producto}:** [{nombre_foto}]({pagina}) — {autor} — {licencia}. Imagen adaptada y reducida a WebP."
        prefijo = f"- **{producto}:**"
        lineas = [nueva if linea.startswith(prefijo) else linea for linea in lineas]
        print(f"  OK {archivo}: {(DEST / archivo).stat().st_size} bytes", flush=True)
    CREDITOS.write_text("\n".join(lineas) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
