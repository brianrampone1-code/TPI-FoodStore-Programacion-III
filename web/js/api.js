// Solo este módulo conoce la URL de la API y llama a fetch.
const API_URL = 'http://127.0.0.1:8000';
export class ApiError extends Error {
  constructor(status, detail, message) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}
async function solicitar(ruta, opciones = {}) {
  let respuesta;
  try {
    respuesta = await fetch(`${API_URL}${ruta}`, opciones);
  } catch {
    throw new ApiError(0, null, 'No se pudo conectar con la API. Verificá que uvicorn esté encendido en el puerto 8000.');
  }
  if (!respuesta.ok) {
    let detail = null;
    try { detail = (await respuesta.json()).detail ?? null; } catch { /* Respuesta sin JSON */ }
    throw new ApiError(respuesta.status, detail, `La API respondió con el código ${respuesta.status}.`);
  }
  return respuesta.status === 204 ? null : respuesta.json();
}
export function obtenerCategorias() {
  return solicitar('/categorias/');
}
export function obtenerProductos({ categoriaId = null, skip = 0, limit = 10 } = {}) {
  const parametros = new URLSearchParams({ skip: String(skip), limit: String(limit) });
  if (categoriaId !== null && categoriaId !== '') parametros.set('categoria_id', String(categoriaId));
  return solicitar(`/productos/?${parametros.toString()}`);
}
export function crearProducto(datos) {
  return solicitar('/productos/', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(datos),
  });
}
