"""Pruebas integrales de la web TPI usando navegador real (Playwright).
Corre con la API en 8000 y el servidor HTTP web en 5500.
No necesita ninguna base existente; el workflow crea una base temporal descartable.
"""
import re
import time
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parent.parent

def api_ready():
    for intento in range(40):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/categorias/", timeout=2) as r:
                if r.status == 200:
                    return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("API no disponible")

def main():
    api_ready()
    scripts = list((ROOT / "web" / "js").glob("*.js"))
    prohibidos = ["innerHTML", "alert(", "confirm(", "prompt(", ".style."]
    for path in scripts:
        texto = path.read_text(encoding="utf-8")
        for termino in prohibidos:
            assert termino not in texto, f"{path}: prohibido {termino}"
        if path.name != "api.js":
            assert "fetch(" not in texto, f"fetch debe estar solo en api.js: {path}"

    errores = []
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page(viewport={"width": 1366, "height": 900})
        pagina.on("pageerror", lambda err: errores.append(str(err)))

        # Catálogo: todas las categorías, 28 productos e imágenes cargadas.
        pagina.goto("http://localhost:5500/", wait_until="networkidle")
        expect(pagina.locator("article.product")).to_have_count(28, timeout=15000)
        expect(pagina.locator(".grupo-titulo")).to_have_text(
            ["Pizzas", "Hamburguesas", "Bebidas", "Postres"]
        )
        imagenes = pagina.locator("article.product img")
        expect(imagenes).to_have_count(28)
        for foto in imagenes.all():
            # Las imágenes usan loading='lazy': una foto fuera de pantalla
            # todavía no se descarga hasta que el navegador la necesite.
            ancho = foto.evaluate("(img) => { img.loading = 'eager'; return img.decode().then(() => img.naturalWidth); }")
            assert ancho >= 800, foto.get_attribute("src")
        assert "Explorá nuestras especialidades. Productos frescos" not in pagina.locator("body").inner_text()
        print("[OK] Catálogo de 28 tarjetas con fotos nítidas", flush=True)

        # Filtro: se obtiene desde el servidor.
        respuestas = []
        pagina.on("response", lambda r: respuestas.append(r.url))
        pagina.get_by_role("button", name="Pizzas", exact=True).click()
        expect(pagina.locator("article.product")).to_have_count(8)
        assert any("categoria_id=" in u for u in respuestas), respuestas
        pagina.get_by_role("button", name="Todas", exact=True).click()
        expect(pagina.locator("article.product")).to_have_count(28)
        print("[OK] Filtro remoto con categoria_id", flush=True)

        # Tabla: 28 productos, tres páginas y botones extremos.
        pagina.goto("http://localhost:5500/productos.html", wait_until="networkidle")
        expect(pagina.locator("#total-productos")).to_have_text("28")
        expect(pagina.locator("#filas tr")).to_have_count(10)
        expect(pagina.locator("#pagina")).to_have_text("Página 1 de 3")
        assert pagina.locator("#anterior").is_disabled()
        pagina.get_by_role("button", name="Siguiente").click()
        expect(pagina.locator("#pagina")).to_have_text("Página 2 de 3")
        pagina.get_by_role("button", name="Siguiente").click()
        expect(pagina.locator("#pagina")).to_have_text("Página 3 de 3")
        expect(pagina.locator("#filas tr")).to_have_count(8)
        assert pagina.locator("#siguiente").is_disabled()
        print("[OK] Paginación desde API", flush=True)

        # Validaciones HTML, JS y API 409.
        pagina.goto("http://localhost:5500/nuevo-producto.html", wait_until="networkidle")
        pagina.locator("#guardar").click()
        assert pagina.locator("#nombre").evaluate("(el) => !el.validity.valid")
        pagina.locator("#nombre").fill("   ")
        pagina.locator("#precio").fill("8900")
        pagina.locator("#stock").fill("4")
        pagina.locator("#categoria_id").select_option(index=1)
        pagina.locator("#guardar").click()
        expect(pagina.locator("#error-nombre")).to_contain_text("espacios")
        print("[OK] Validación HTML y JavaScript", flush=True)

        pagina.locator("#nombre").fill("Pizza muzzarella")
        pagina.locator("#guardar").click()
        expect(pagina.locator("#error-nombre")).to_contain_text("nombre", timeout=10000)
        print("[OK] Error 409 mostrado en Nombre", flush=True)

        # Creación de punta a punta y persistencia (base temporal de CI).
        codigo = "TPI Demo Gourmet Verificado"
        pagina.locator("#nombre").fill(codigo)
        pagina.locator("#descripcion").fill("Creado automáticamente desde la web")
        pagina.locator("#guardar").click()
        expect(pagina).to_have_url(re.compile(r"productos\.html\?creado="), timeout=15000)
        expect(pagina.locator("#estado-accion")).to_contain_text("creado correctamente", timeout=15000)
        expect(pagina.locator("#total-productos")).to_have_text("29")
        pagina.goto("http://localhost:5500/", wait_until="networkidle")
        expect(pagina.get_by_role("heading", name=codigo)).to_be_visible()
        print("[OK] Alta 201, persistencia, lista y catálogo", flush=True)

        # Ancho móvil, sin desbordes globales (tabla se puede desplazar).
        pagina.set_viewport_size({"width": 375, "height": 812})
        pagina.goto("http://localhost:5500/productos.html", wait_until="networkidle")
        assert pagina.locator(".table-wrap").count() == 1
        assert pagina.locator(".table-wrap").evaluate("(e) => e.scrollWidth > e.clientWidth")
        print("[OK] Móvil 375px y tabla desplazable", flush=True)

        # Mensaje de conexión caída con botón Reintentar.
        pagina.route("http://127.0.0.1:8000/**", lambda ruta: ruta.abort())
        pagina.goto("http://localhost:5500/", wait_until="networkidle")
        expect(pagina.get_by_role("button", name="Reintentar")).to_be_visible()
        pagina.unroute_all()
        pagina.get_by_role("button", name="Reintentar").click()
        expect(pagina.locator("article.product")).to_have_count(29)
        print("[OK] Caída de API y reintento", flush=True)

        assert not errores, "Errores en consola: " + "; ".join(errores)
        print("PRUEBAS WEB COMPLETAS: OK", flush=True)
        navegador.close()

if __name__ == "__main__":
    main()
