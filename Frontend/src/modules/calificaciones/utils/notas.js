/** Utilidades compartidas por las vistas de calificaciones (docente y estudiante). */

/** Clase del badge según la escala 0.00–5.00 definida en el spec. */
export function claseBadge(calificacion) {
  if (calificacion === null || calificacion === undefined || Number.isNaN(calificacion)) return "empty";
  if (calificacion >= 4) return "good";
  if (calificacion >= 3) return "ok";
  return "alert";
}

/** Texto del badge: dos decimales, o un guion si no hay nota. */
export function formatearNota(calificacion) {
  if (calificacion === null || calificacion === undefined || Number.isNaN(calificacion)) return "—";
  return Number(calificacion).toFixed(2);
}

/** Promedio simple de una lista de calificaciones. Devuelve null si no hay ninguna. */
export function promedioSimple(calificaciones) {
  const valores = calificaciones.filter((valor) => valor !== null && valor !== undefined && !Number.isNaN(valor));
  if (valores.length === 0) return null;
  return valores.reduce((suma, valor) => suma + Number(valor), 0) / valores.length;
}

/**
 * Promedio ponderado por sección: Σ(nota_seccion * porcentaje) / Σ(porcentaje).
 * Las actividades no tienen porcentaje propio en el backend; el peso vive en la sección.
 * @param {{promedio: number|null, porcentaje: number}[]} secciones
 */
export function promedioPonderado(secciones) {
  const conNota = secciones.filter((item) => item.promedio !== null && item.promedio !== undefined);
  const sumaPesos = conNota.reduce((suma, item) => suma + Number(item.porcentaje || 0), 0);
  if (sumaPesos === 0) return null;
  const sumaNotas = conNota.reduce((suma, item) => suma + Number(item.promedio) * Number(item.porcentaje || 0), 0);
  return sumaNotas / sumaPesos;
}
