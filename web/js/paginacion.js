// Paginación real por skip y limit. No recorta listas locales.
export function calcularPaginacion(total, pagina, limite) {
  const paginas = Math.max(1, Math.ceil(total / limite));
  const actual = Math.max(1, Math.min(pagina, paginas));
  return { paginas, actual, skip: (actual - 1) * limite, anterior: actual > 1, siguiente: actual < paginas };
}
