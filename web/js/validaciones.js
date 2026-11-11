// Validaciones independientes del DOM; siguen api/schemas.py.
export function validarProducto(datos) {
  const errores = {};
  if (datos.nombre.trim().length < 3 || datos.nombre.trim().length > 60) errores.nombre = 'El nombre debe tener entre 3 y 60 caracteres y no puede estar formado solo por espacios.';
  if (datos.descripcion.length > 200) errores.descripcion = 'La descripción admite hasta 200 caracteres.';
  if (!Number.isFinite(datos.precio) || datos.precio <= 0) errores.precio = 'El precio debe ser mayor a 0.';
  if (!Number.isInteger(datos.stock) || datos.stock < 0) errores.stock = 'El stock debe ser un entero mayor o igual a 0.';
  if (!Number.isInteger(datos.categoria_id) || datos.categoria_id <= 0) errores.categoria_id = 'Seleccioná una categoría válida.';
  if (datos.imagen_url !== null && datos.imagen_url.length > 255) errores.imagen_url = 'La URL admite hasta 255 caracteres.';
  return errores;
}
