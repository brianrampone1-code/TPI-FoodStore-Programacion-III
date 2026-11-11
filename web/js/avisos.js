// Unifica los mensajes visuales; siempre usa textContent.
export function aviso(contenedor, mensaje, tipo = 'info', reintentar = null) {
  contenedor.replaceChildren();
  if (!mensaje) return;
  const caja = document.createElement('div');
  caja.className = `notice ${tipo}`;
  caja.setAttribute('role', tipo === 'error' ? 'alert' : 'status');
  const texto = document.createElement('span');
  texto.textContent = mensaje;
  caja.append(texto);
  if (reintentar) {
    const boton = document.createElement('button');
    boton.type = 'button'; boton.className = 'btn btn-secondary';
    boton.textContent = 'Reintentar'; boton.addEventListener('click', reintentar);
    caja.append(boton);
  }
  contenedor.append(caja);
}
export function mensajeError(error) {
  if (error.status === 0) return error.message;
  if (typeof error.detail === 'string') return error.detail;
  return error.message || 'Ocurrió un error inesperado.';
}
