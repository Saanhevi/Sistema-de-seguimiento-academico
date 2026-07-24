/**
 * Etiqueta legible de un curso: "Matemáticas · 3°A · Primer Periodo".
 * Con BE-2 el backend devuelve grado/materia/periodo anidados; si faltaran,
 * se cae a los IDs planos para no romper la vista.
 */
export function etiquetaCurso(curso) {
  const materia = curso.materia?.nombre || `Materia ${curso.id_materia}`;
  const grado = curso.grado?.nombre || `Grado ${curso.id_grado}`;
  const periodo = curso.periodo?.nombre || `Periodo ${curso.id_periodo}`;
  return `${materia} · ${grado} · ${periodo}`;
}
