import { obtenerCategorias, obtenerProductos } from './api.js';
import { aviso, mensajeError } from './avisos.js';
import { agregarImagen } from './imagenes.js';
const botones = document.querySelector('#categorias');
const contenedor = document.querySelector('#productos');
const estado = document.querySelector('#estado');
const contador = document.querySelector('#contador');
let categoriaSeleccionada = null;
let idSolicitud = 0;
const moneda = new Intl.NumberFormat('es-AR', { style:'currency', currency:'ARS', maximumFractionDigits:2 });
function texto(tag, clase, contenido) {
  const elemento = document.createElement(tag); elemento.className = clase;
  elemento.textContent = contenido; return elemento;
}
function tarjeta(producto) {
  const articulo = document.createElement('article'); articulo.className = 'product';
  agregarImagen(articulo, producto.imagen_url, producto.nombre);
  const body = texto('div', 'body', '');
  body.append(texto('p', 'tag', producto.categoria?.nombre || 'Categoría sin nombre'));
  body.append(texto('h3', '', producto.nombre));
  body.append(texto('p', 'desc', producto.descripcion || 'Especialidad de Food Store.'));
  const linea = texto('div', 'price-line', '');
  linea.append(texto('strong', 'price', moneda.format(producto.precio)));
  linea.append(texto('span', producto.stock > 0 ? 'stock' : 'stock empty', producto.stock > 0 ? `${producto.stock} disponibles` : 'Sin stock'));
  body.append(linea); articulo.append(body); return articulo;
}
const ORDEN_CATEGORIAS = ['Pizzas', 'Hamburguesas', 'Bebidas', 'Postres'];
function grupoCategoria(nombre, productos) {
  const seccion = document.createElement('section');
  seccion.className = 'grupo-menu';
  const cabecera = document.createElement('div');
  cabecera.className = 'grupo-cabecera';
  const titulo = texto('h3', 'grupo-titulo', nombre);
  cabecera.append(titulo, texto('span', 'grupo-cantidad', `${productos.length} variedades`));
  const grilla = document.createElement('div');
  grilla.className = 'grid-products';
  for (const producto of productos) grilla.append(tarjeta(producto));
  seccion.append(cabecera, grilla);
  return seccion;
}
async function cargarCatalogo() {
  const solicitud = ++idSolicitud;
  contenedor.replaceChildren(); contador.textContent = '';
  aviso(estado, 'Cargando productos…');
  try {
    const datos = await obtenerProductos({ categoriaId: categoriaSeleccionada, skip: 0, limit: 50 });
    if (solicitud !== idSolicitud) return;
    estado.replaceChildren();
    contador.textContent = `${datos.total} productos`;
    if (!datos.items.length) {
      aviso(estado, 'No hay productos en esta categoría.');
      return;
    }
    const grupos = new Map();
    for (const producto of datos.items) {
      const nombre = producto.categoria?.nombre || 'Otros';
      if (!grupos.has(nombre)) grupos.set(nombre, []);
      grupos.get(nombre).push(producto);
    }
    const nombres = [...grupos.keys()].sort((a, b) => {
      const indiceA = ORDEN_CATEGORIAS.indexOf(a);
      const indiceB = ORDEN_CATEGORIAS.indexOf(b);
      return (indiceA < 0 ? 100 : indiceA) - (indiceB < 0 ? 100 : indiceB) || a.localeCompare(b, 'es');
    });
    const fragmento = document.createDocumentFragment();
    for (const nombre of nombres) fragmento.append(grupoCategoria(nombre, grupos.get(nombre)));
    contenedor.append(fragmento);
  } catch (error) {
    if (solicitud !== idSolicitud) return;
    aviso(estado, mensajeError(error), 'error', cargarCatalogo);
  }
}
function dibujarCategorias(categorias) {
  botones.replaceChildren();
  for (const categoria of [{ id:null, nombre:'Todas' }, ...categorias]) {
    const b = document.createElement('button'); b.type = 'button';
    b.className = `filter${categoria.id === categoriaSeleccionada ? ' active' : ''}`;
    b.textContent = categoria.nombre;
    b.setAttribute('aria-pressed', String(categoria.id === categoriaSeleccionada));
    b.addEventListener('click', () => {
      categoriaSeleccionada = categoria.id;
      [...botones.children].forEach(x => { x.classList.remove('active'); x.setAttribute('aria-pressed','false'); });
      b.classList.add('active'); b.setAttribute('aria-pressed', 'true');
      cargarCatalogo();
    });
    botones.append(b);
  }
}
async function iniciar() {
  try {
    const categorias = await obtenerCategorias(); dibujarCategorias(categorias);
    await cargarCatalogo();
  } catch (error) { aviso(estado, mensajeError(error), 'error', iniciar); }
}
iniciar();
