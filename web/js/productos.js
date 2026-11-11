import { obtenerProductos, obtenerCategorias, crearProducto } from './api.js';
import { aviso, mensajeError } from './avisos.js';
import { calcularPaginacion } from './paginacion.js';
import { validarProducto } from './validaciones.js';
const filas = document.querySelector('#filas');
const estadoLista = document.querySelector('#estado-lista');
const estadoForm = document.querySelector('#estado-form');
const anterior = document.querySelector('#anterior');
const siguiente = document.querySelector('#siguiente');
const paginaTexto = document.querySelector('#pagina');
const totalTexto = document.querySelector('#total-productos');
const formulario = document.querySelector('#form-producto');
const guardar = document.querySelector('#guardar');
const selector = document.querySelector('#categoria_id');
const moneda = new Intl.NumberFormat('es-AR', {style:'currency',currency:'ARS',maximumFractionDigits:2});
const limite = 10;
let pagina = 1, total = 0, solicitud = 0;
function celda(fila, valor) { const td = document.createElement('td'); td.textContent = String(valor); fila.append(td); }
function erroresLimpiar() {
  for (const campo of formulario.elements) {
    if (!campo.name) continue;
    campo.removeAttribute('aria-invalid');
    const salida = document.getElementById(`error-${campo.name}`);
    if (salida) salida.textContent = '';
  }
}
function errorCampo(nombre, mensaje) {
  const campo = formulario.elements.namedItem(nombre);
  const salida = document.getElementById(`error-${nombre}`);
  if (!campo || !salida) return false;
  campo.setAttribute('aria-invalid', 'true'); salida.textContent = mensaje;
  return true;
}
function pintarErrores(errores) {
  let primero = null;
  for (const [nombre, mensaje] of Object.entries(errores)) {
    if (errorCampo(nombre, mensaje) && !primero) primero = formulario.elements.namedItem(nombre);
  }
  if (primero) primero.focus();
}
function convertirDetalle(detalle) {
  if (typeof detalle === 'string') return detalle;
  if (Array.isArray(detalle)) return detalle.map(x => x.msg).join(' · ');
  return null;
}
function manejarErrorApi(error) {
  if (error.status === 409) {
    errorCampo('nombre', convertirDetalle(error.detail) || 'Ese nombre ya existe.');
    formulario.elements.namedItem('nombre').focus(); return;
  }
  if (error.status === 404) {
    errorCampo('categoria_id', convertirDetalle(error.detail) || 'La categoría no está disponible.');
    selector.focus(); return;
  }
  if (error.status === 422 && Array.isArray(error.detail)) {
    const nombres = ['nombre','descripcion','precio','stock','imagen_url','categoria_id'];
    const errores = {};
    for (const entrada of error.detail) {
      const campo = entrada.loc?.find(x => nombres.includes(x));
      if (campo) errores[campo] = entrada.msg;
    }
    if (Object.keys(errores).length) { pintarErrores(errores); return; }
  }
  aviso(estadoForm, mensajeError(error), 'error');
}
function pintarPaginacion() {
  const p = calcularPaginacion(total,pagina,limite);
  paginaTexto.textContent = `Página ${p.actual} de ${p.paginas}`;
  anterior.disabled = !p.anterior; siguiente.disabled = !p.siguiente;
  totalTexto.textContent = String(total);
}
async function cargarLista() {
  const token = ++solicitud;
  aviso(estadoLista, 'Cargando productos…');
  filas.replaceChildren();
  anterior.disabled = true; siguiente.disabled = true;
  try {
    const respuesta = await obtenerProductos({skip:(pagina-1)*limite,limit:limite});
    if (token !== solicitud) return;
    total = respuesta.total;
    const maximo = Math.max(1,Math.ceil(total/limite));
    if (pagina > maximo) { pagina = maximo; await cargarLista(); return; }
    estadoLista.replaceChildren();
    if (!respuesta.items.length) aviso(estadoLista,'Todavía no hay productos.');
    for (const producto of respuesta.items) {
      const fila = document.createElement('tr');
      celda(fila, producto.id); celda(fila, producto.nombre);
      celda(fila, producto.categoria?.nombre || 'Sin categoría');
      celda(fila, moneda.format(producto.precio));celda(fila, producto.stock);
      filas.append(fila);
    }
    pintarPaginacion();
  } catch (error) { if (token === solicitud) aviso(estadoLista,mensajeError(error),'error',cargarLista); }
}
async function cargarCategorias() {
  const categorias = await obtenerCategorias();
  selector.replaceChildren();
  const inicial = document.createElement('option'); inicial.value = ''; inicial.textContent = 'Seleccioná una categoría'; selector.append(inicial);
  for (const categoria of categorias) {
    const opcion = document.createElement('option');
    opcion.value = String(categoria.id); opcion.textContent = categoria.nombre; selector.append(opcion);
  }
}
anterior.addEventListener('click', () => { if(pagina>1){pagina--;cargarLista();} });
siguiente.addEventListener('click', () => { if(pagina*limite<total){pagina++;cargarLista();} });
for (const campo of formulario.elements) {
  if (!campo.name) continue;
  const limpiar = () => {
    campo.removeAttribute('aria-invalid');
    const texto = document.getElementById(`error-${campo.name}`);
    if (texto) texto.textContent = '';
  };
  campo.addEventListener('input',limpiar); campo.addEventListener('change',limpiar);
}
formulario.addEventListener('submit', async (evento) => {
  evento.preventDefault(); erroresLimpiar(); aviso(estadoForm,'');
  const datos = {
    nombre: formulario.elements.namedItem('nombre').value.trim(),
    descripcion: formulario.elements.namedItem('descripcion').value.trim(),
    precio: Number(formulario.elements.namedItem('precio').value),
    stock: Number(formulario.elements.namedItem('stock').value),
    categoria_id: Number(selector.value),
    imagen_url: formulario.elements.namedItem('imagen_url').value.trim() || null,
  };
  const errores = validarProducto(datos);
  if (Object.keys(errores).length) { pintarErrores(errores); return; }
  guardar.disabled = true; guardar.textContent = 'Guardando…';
  try {
    const creado = await crearProducto(datos);
    formulario.reset(); erroresLimpiar();
    pagina = 1;
    await cargarLista();
    aviso(estadoForm, `Producto #${creado.id} creado correctamente. Ya aparece en el catálogo y en la base de datos.`, 'success');
  } catch (error) { manejarErrorApi(error); }
  finally { guardar.disabled = false; guardar.textContent = 'Guardar producto'; }
});
async function iniciar() {
  try { await cargarCategorias(); }
  catch (error) { aviso(estadoForm, mensajeError(error),'error',iniciar); }
  await cargarLista();
}
iniciar();
