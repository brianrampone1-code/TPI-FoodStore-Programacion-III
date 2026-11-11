import { obtenerProductos } from './api.js';
import { aviso, mensajeError } from './avisos.js';
import { calcularPaginacion } from './paginacion.js';

const filas = document.querySelector('#filas');
const estadoAccion = document.querySelector('#estado-accion');
const estadoLista = document.querySelector('#estado-lista');
const anterior = document.querySelector('#anterior');
const siguiente = document.querySelector('#siguiente');
const paginaTexto = document.querySelector('#pagina');
const totalTexto = document.querySelector('#total-productos');
const moneda = new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 2 });
const limite = 10;
let pagina = 1;
let total = 0;
let solicitud = 0;

function celda(fila, valor) {
  const td = document.createElement('td');
  td.textContent = String(valor);
  fila.append(td);
}

function pintarPaginacion() {
  const p = calcularPaginacion(total, pagina, limite);
  paginaTexto.textContent = `Página ${p.actual} de ${p.paginas}`;
  anterior.disabled = !p.anterior;
  siguiente.disabled = !p.siguiente;
  totalTexto.textContent = String(total);
}

function mostrarMensajeCreacion() {
  const params = new URLSearchParams(window.location.search);
  const creado = params.get('creado');
  if (!creado) return;
  aviso(estadoAccion, `Producto #${creado} creado correctamente. La lista se pidió nuevamente a la API.`, 'success');
  params.delete('creado');
  const nueva = `${window.location.pathname}${params.toString() ? `?${params.toString()}` : ''}`;
  window.history.replaceState({}, '', nueva);
}

async function cargarLista() {
  const token = ++solicitud;
  aviso(estadoLista, 'Cargando productos…');
  filas.replaceChildren();
  anterior.disabled = true;
  siguiente.disabled = true;

  try {
    const respuesta = await obtenerProductos({ skip: (pagina - 1) * limite, limit: limite });
    if (token !== solicitud) return;
    total = respuesta.total;
    const maximo = Math.max(1, Math.ceil(total / limite));
    if (pagina > maximo) {
      pagina = maximo;
      await cargarLista();
      return;
    }
    estadoLista.replaceChildren();
    if (!respuesta.items.length) aviso(estadoLista, 'Todavía no hay productos.');
    for (const producto of respuesta.items) {
      const fila = document.createElement('tr');
      celda(fila, producto.id);
      celda(fila, producto.nombre);
      celda(fila, producto.categoria?.nombre || 'Sin categoría');
      celda(fila, moneda.format(producto.precio));
      celda(fila, producto.stock);
      filas.append(fila);
    }
    pintarPaginacion();
    mostrarMensajeCreacion();
  } catch (error) {
    if (token === solicitud) aviso(estadoLista, mensajeError(error), 'error', cargarLista);
  }
}

anterior.addEventListener('click', () => {
  if (pagina > 1) {
    pagina -= 1;
    cargarLista();
  }
});

siguiente.addEventListener('click', () => {
  if (pagina * limite < total) {
    pagina += 1;
    cargarLista();
  }
});

cargarLista();
