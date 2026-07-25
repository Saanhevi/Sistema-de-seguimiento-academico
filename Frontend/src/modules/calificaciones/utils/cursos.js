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

/**
 * Nombre completo del docente del curso, o null si el backend no lo envió.
 * Se arma campo por campo (como etiquetaCurso) porque el backend puede mandar
 * el docente con nombre/apellido en null si la fila Usuario está incompleta:
 * interpolar directo produciría el literal "null null" en pantalla.
 */
export function nombreDocente(curso) {
  const docente = curso?.docente;
  if (!docente) return null;
  return [docente.nombre, docente.apellido].filter(Boolean).join(" ") || null;
}
