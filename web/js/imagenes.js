// Convierte una URL de imagen en una vista segura con alternativa Sin imagen.
export function agregarImagen(contenedor, url, nombre) {
  const caja = document.createElement('div'); caja.className = 'media';
  const reemplazar = () => {
    const alternativo = document.createElement('div');
    alternativo.className = 'no-image'; alternativo.textContent = 'Sin imagen';
    caja.replaceChildren(alternativo);
  };
  if (!url) { reemplazar(); contenedor.append(caja); return; }
  const imagen = document.createElement('img'); imagen.alt = nombre || 'Imagen de producto';
  imagen.loading = 'lazy'; imagen.addEventListener('error', reemplazar, { once: true });
  imagen.src = url; caja.append(imagen); contenedor.append(caja);
}
