"""Fotos específicas para los 28 productos de Food Store.

Busca fotografías con licencia abierta en Openverse, guarda archivos WebP
locales (menos de 200 KB) y genera atribuciones. No altera datos de la API.
Se ejecuta en GitHub Actions; no necesita credenciales privadas.
"""
from __future__ import annotations

import json
import re
import time
import unicodedata
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "web" / "img"
DEST.mkdir(parents=True, exist_ok=True)
HEADERS = {
    "User-Agent": "FoodStoreTPI/1.0 (educational university project; photographs for catalog)",
    "Accept": "application/json",
}

# Nombre exacto (en la API), archivo individual, descripción de la foto buscada.
PRODUCTOS = [
    ("Pizza muzzarella", "pizza-muzzarella.webp", "mozzarella cheese pizza"),
    ("Pizza napolitana", "pizza-napolitana.webp", "neapolitan pizza tomato slices"),
    ("Pizza fugazzeta", "pizza-fugazzeta.webp", "onion pizza"),
    ("Pizza especial", "pizza-especial.webp", "ham red pepper olive pizza"),
    ("Hamburguesa clásica", "hamburguesa-clasica.webp", "cheeseburger"),
    ("Hamburguesa doble", "hamburguesa-doble.webp", "double beef cheeseburger"),
    ("Hamburguesa veggie", "hamburguesa-veggie.webp", "vegetarian veggie burger"),
    ("Hamburguesa picante", "hamburguesa-picante.webp", "spicy jalapeno burger"),
    ("Agua mineral", "agua-mineral.webp", "glass still mineral water bottle"),
    ("Gaseosa cola", "gaseosa-cola.webp", "cola soda drink glass with ice"),
    ("Flan casero", "flan-casero.webp", "caramel flan creme caramel dessert"),
    ("Brownie", "brownie.webp", "chocolate brownie dessert"),
    ("Pizza cuatro quesos", "pizza-cuatro-quesos.webp", "four cheese pizza"),
    ("Pizza calabresa", "pizza-calabresa.webp", "pepperoni salami pizza"),
    ("Pizza de rúcula", "pizza-rucula.webp", "arugula rocket pizza"),
    ("Pizza margarita", "pizza-margarita.webp", "margherita pizza basil"),
    ("Hamburguesa BBQ", "hamburguesa-bbq.webp", "barbecue sauce burger"),
    ("Hamburguesa cheddar", "hamburguesa-cheddar.webp", "cheddar cheese burger"),
    ("Hamburguesa criolla", "hamburguesa-criolla.webp", "burger fried egg chimichurri"),
    ("Hamburguesa con panceta", "hamburguesa-panceta.webp", "bacon cheeseburger"),
    ("Limonada casera", "limonada-casera.webp", "fresh lemonade glass lemon mint"),
    ("Jugo de naranja", "jugo-naranja.webp", "fresh orange juice glass oranges"),
    ("Agua con gas", "agua-con-gas.webp", "sparkling water glass bubbles"),
    ("Té frío", "te-frio.webp", "iced tea glass lemon"),
    ("Cheesecake", "cheesecake.webp", "cheesecake slice berry dessert"),
    ("Helado artesanal", "helado-artesanal.webp", "ice cream"),
    ("Chocotorta", "chocotorta.webp", "chocolate layered biscuit cake dessert"),
    ("Ensalada de frutas", "ensalada-frutas.webp", "fresh fruit salad bowl"),
]

def api_json(url: str) -> dict:
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=35) as resp:
        return json.load(resp)

def normalizar(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    return "".join(c for c in value if not unicodedata.combining(c))

def candidatos_openverse(query: str) -> list[dict]:
    url = "https://api.openverse.org/v1/images/?" + urlencode({
        "q": query, "page_size": 20, "license_type": "commercial",
    })
    data = api_json(url)
    return data.get("results", [])

def elegir(resultados: list[dict], query: str, previas: set[str]):
    palabras = set(normalizar(query).split())
    candidatos = []
    for foto in resultados:
        imagen = foto.get("url") or ""
        if not imagen or imagen in previas:
            continue
        if foto.get("width") and foto.get("height"):
            if foto["width"] < 350 or foto["height"] < 250:
                continue
        titulo = normalizar(foto.get("title") or "")
        tags = " ".join(normalizar(tag.get("name") or "") for tag in (foto.get("tags") or []) if isinstance(tag, dict))
        score = sum(6 if x in titulo else 1 if x in tags else 0 for x in palabras)
        # Preferir material fotográfico con suficiente resolución.
        score += min((foto.get("width") or 900) / 900, 3)
        if any(x in titulo for x in ["logo", "illustration", "vector", "icon", "poster", "menu", "package"]):
            score -= 20
        candidatos.append((score, foto))
    candidatos.sort(key=lambda x: x[0], reverse=True)
    return [f for _, f in candidatos]

def foto_webp(foto: dict, salida: Path) -> bool:
    for url in [foto.get("url"), foto.get("thumbnail")]:
        if not url:
            continue
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0 (Food Store coursework)"})
            with urlopen(req, timeout=35) as resp:
                raw = resp.read(12_000_000)
            imagen = Image.open(BytesIO(raw)).convert("RGB")
            imagen = ImageOps.fit(imagen, (800, 600), method=Image.Resampling.LANCZOS)
            # El máximo de 200 KB recomendado por el docente se respeta.
            for quality in [76, 65, 54, 42]:
                buf = BytesIO()
                imagen.save(buf, "WEBP", quality=quality, method=5)
                if buf.tell() < 195_000:
                    salida.write_bytes(buf.getvalue())
                    return True
        except (HTTPError, URLError, TimeoutError, OSError, UnidentifiedImageError) as error:
            print("  fuente inaccesible:", str(error)[:110], flush=True)
    return False

def main():
    usados = set()
    credito = ["# Fotografías Food Store", "", "Imágenes con licencia abierta obtenidas mediante Openverse:", ""]
    faltantes = []
    for nombre, archivo, consulta in PRODUCTOS:
        salida = DEST / archivo
        print(f"Buscando {nombre}: {consulta}", flush=True)
        try:
            candidatos = elegir(candidatos_openverse(consulta), consulta, usados)
        except Exception as exc:
            print("  Error de búsqueda:", str(exc)[:200], flush=True)
            candidatos = []
        exito = False
        for foto in candidatos[:12]:
            if foto_webp(foto, salida):
                usados.add(foto.get("url", ""))
                credito.append(f"- **{nombre}:** [{foto.get('title') or 'Foto'}]({foto.get('foreign_landing_url') or foto.get('url')}) — {foto.get('creator') or 'autor no especificado'} — {foto.get('license', 'licencia abierta')} [{foto.get('license_version') or ''}].")
                print(f"  OK {archivo}: {salida.stat().st_size} bytes", flush=True)
                exito = True
                break
        if not exito:
            print(f"  SIN FOTO: {nombre}", flush=True)
            faltantes.append(nombre)
        time.sleep(0.12)
    (ROOT / "FOTOS_CREDITOS.md").write_text("\n".join(credito) + "\n", encoding="utf-8")
    print(f"FOTOS COMPLETADAS: {len(PRODUCTOS)-len(faltantes)}/{len(PRODUCTOS)}", flush=True)
    if faltantes:
        raise RuntimeError("Faltan fotografías específicas: " + ", ".join(faltantes))

if __name__ == "__main__":
    main()
