import { obtenerCategorias, crearProducto } from './api.js';
import { aviso, mensajeError } from './avisos.js';
import { validarProducto } from './validaciones.js';

const estadoForm = document.querySelector('#estado-form');
const formulario = document.querySelector('#form-producto');
const guardar = document.querySelector('#guardar');
const selector = document.querySelector('#categoria_id');

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
  campo.setAttribute('aria-invalid', 'true');
  salida.textContent = mensaje;
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
    formulario.elements.namedItem('nombre').focus();
    return;
  }
  if (error.status === 404) {
    errorCampo('categoria_id', convertirDetalle(error.detail) || 'La categoría no está disponible.');
    selector.focus();
    return;
  }
  if (error.status === 422 && Array.isArray(error.detail)) {
    const nombres = ['nombre', 'descripcion', 'precio', 'stock', 'imagen_url', 'categoria_id'];
    const errores = {};
    for (const entrada of error.detail) {
      const campo = entrada.loc?.find(x => nombres.includes(x));
      if (campo) errores[campo] = entrada.msg;
    }
    if (Object.keys(errores).length) {
      pintarErrores(errores);
      return;
    }
  }
  aviso(estadoForm, mensajeError(error), 'error');
}

async function cargarCategorias() {
  const categorias = await obtenerCategorias();
  selector.replaceChildren();
  const inicial = document.createElement('option');
  inicial.value = '';
  inicial.textContent = 'Seleccioná una categoría';
  selector.append(inicial);
  for (const categoria of categorias) {
    const opcion = document.createElement('option');
    opcion.value = String(categoria.id);
    opcion.textContent = categoria.nombre;
    selector.append(opcion);
  }
}

for (const campo of formulario.elements) {
  if (!campo.name) continue;
  const limpiar = () => {
    campo.removeAttribute('aria-invalid');
    const texto = document.getElementById(`error-${campo.name}`);
    if (texto) texto.textContent = '';
  };
  campo.addEventListener('input', limpiar);
  campo.addEventListener('change', limpiar);
}

formulario.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  erroresLimpiar();
  aviso(estadoForm, '');

  const datos = {
    nombre: formulario.elements.namedItem('nombre').value.trim(),
    descripcion: formulario.elements.namedItem('descripcion').value.trim(),
    precio: Number(formulario.elements.namedItem('precio').value),
    stock: Number(formulario.elements.namedItem('stock').value),
    categoria_id: Number(selector.value),
    imagen_url: formulario.elements.namedItem('imagen_url').value.trim() || null,
  };

  const errores = validarProducto(datos);
  if (Object.keys(errores).length) {
    pintarErrores(errores);
    return;
  }

  guardar.disabled = true;
  guardar.textContent = 'Guardando…';
  try {
    const creado = await crearProducto(datos);
    aviso(estadoForm, `Producto #${creado.id} creado correctamente. Redirigiendo a la lista actualizada…`, 'success');
    setTimeout(() => {
      window.location.href = `productos.html?creado=${encodeURIComponent(creado.id)}`;
    }, 500);
  } catch (error) {
    manejarErrorApi(error);
  } finally {
    guardar.disabled = false;
    guardar.textContent = 'Guardar producto';
  }
});

async function iniciar() {
  try {
    await cargarCategorias();
  } catch (error) {
    aviso(estadoForm, mensajeError(error), 'error', iniciar);
  }
}

iniciar();
