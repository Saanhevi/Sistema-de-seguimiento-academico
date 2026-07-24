import { useEffect, useState } from "react";
import { listarMisCursos } from "../services/calificacionService";
import { etiquetaCurso } from "../utils/cursos";

/**
 * Lista los cursos del docente autenticado como pills seleccionables.
 * Con BE-2 el backend devuelve grado/materia/periodo anidados, así que el label
 * se arma en una sola llamada, sin cruzar /api/grados ni /api/materias.
 */
export default function SelectorCurso({ idDocente, cursoSeleccionado, onSeleccionar }) {
  const [cursos, setCursos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!idDocente) return undefined;

    let vigente = true;

    listarMisCursos(idDocente)
      .then((data) => {
        if (!vigente) return;
        setCursos(data);
        // Selección automática cuando el docente tiene un único curso.
        if (data.length === 1) onSeleccionar(data[0]);
      })
      .catch((err) => {
        if (vigente) setError(err.detail || "No se pudieron cargar tus cursos");
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });

    return () => {
      vigente = false;
    };
    // onSeleccionar se omite a propósito: solo queremos recargar al cambiar de docente.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [idDocente]);

  if (!idDocente) {
    return (
      <p className="cal-error">
        No se encontró tu identificador de usuario. Cierra sesión y vuelve a iniciarla.
      </p>
    );
  }

  if (cargando) return <p className="cal-hint">Cargando tus cursos...</p>;
  if (error) return <p className="cal-error">{error}</p>;
  if (cursos.length === 0) return <p className="cal-empty">Aún no tienes cursos asignados.</p>;

  return (
    <div className="cal-toolbar">
      {cursos.map((curso) => (
        <button
          key={curso.id_curso}
          type="button"
          className={`cal-pill ${cursoSeleccionado?.id_curso === curso.id_curso ? "active" : ""}`}
          onClick={() => onSeleccionar(curso)}
        >
          {etiquetaCurso(curso)}
        </button>
      ))}
    </div>
  );
}
