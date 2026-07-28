import { useEffect, useState } from "react";
import {
  listarEstudiantesDeGrado,
  obtenerPromediosEstudiantes,
  obtenerPromedioGrupal
} from "../services/calificacionService";
import { claseBadge, formatearNota } from "../utils/notas";
import CardPromedio from "./CardPromedio";

/**
 * Promedios de la materia para el docente: HU8 (promedio de cada estudiante) y
 * HU9 (promedio grupal).
 *
 * El promedio ponderado lo calcula el backend por materia y periodo, con los
 * porcentajes de cada sección; aquí solo se cruza con los estudiantes del grado para
 * ponerle nombre a cada id. El grupal es la media de la columna que se muestra, así
 * que ambos números son consistentes entre sí.
 */
export default function PanelPromediosMateria({ curso }) {
  const [promedios, setPromedios] = useState([]);
  const [grupal, setGrupal] = useState(null);
  const [estudiantes, setEstudiantes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const idMateria = curso?.id_materia;
  const idPeriodo = curso?.id_periodo;
  const idGrado = curso?.id_grado;
  const anio = curso?.periodo?.anio;

  useEffect(() => {
    if (!idMateria || !idPeriodo) return undefined;

    let vigente = true;

    // No se reinicia aquí el estado de carga: la vista del docente monta este panel con
    // key={curso.id_curso}, así que al cambiar de curso el componente se remonta y los
    // valores iniciales ya son los correctos.
    // Las tres consultas son independientes; en serie sumarían sus latencias.
    Promise.all([
      obtenerPromediosEstudiantes(idMateria, idPeriodo),
      obtenerPromedioGrupal(idMateria, idPeriodo),
      idGrado ? listarEstudiantesDeGrado(idGrado, anio) : Promise.resolve([])
    ])
      .then(([listaPromedios, datosGrupal, listaEstudiantes]) => {
        if (!vigente) return;
        setPromedios(listaPromedios);
        setGrupal(datosGrupal.promedio_grupal);
        setEstudiantes(listaEstudiantes);
      })
      .catch((err) => {
        if (vigente) setError(err.detail || "No se pudieron cargar los promedios de la materia");
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });

    return () => {
      vigente = false;
    };
  }, [idMateria, idPeriodo, idGrado, anio]);

  if (cargando) {
    return <p className="cal-hint">Calculando promedios de la materia...</p>;
  }

  if (error) {
    return <p className="cal-error">{error}</p>;
  }

  const promedioPorEstudiante = new Map(promedios.map((fila) => [fila.id_estudiante, fila.promedio]));

  // Se listan todos los matriculados y no solo los que ya tienen nota: al docente le
  // sirve ver quién sigue sin calificar. Si la lista del grado no llega, se cae a los
  // ids que devolvió el promedio para no dejar la tabla vacía.
  const filas =
    estudiantes.length > 0
      ? estudiantes.map((estudiante) => ({
          id_estudiante: estudiante.id_estudiante,
          nombre: `${estudiante.nombre ?? ""} ${estudiante.apellido ?? ""}`.trim(),
          promedio: promedioPorEstudiante.get(estudiante.id_estudiante) ?? null
        }))
      : promedios.map((fila) => ({
          id_estudiante: fila.id_estudiante,
          nombre: `Estudiante ${fila.id_estudiante}`,
          promedio: fila.promedio
        }));

  const calificados = filas.filter((fila) => fila.promedio !== null).length;

  return (
    <>
      <div className="cal-promedios-resumen">
        <CardPromedio titulo="Promedio grupal" valor={grupal} />
        <p className="cal-hint">
          {calificados} de {filas.length} estudiantes con nota en esta materia.
        </p>
      </div>

      {filas.length === 0 ? (
        <p className="cal-empty">Todavía no hay estudiantes ni notas en esta materia.</p>
      ) : (
        <div className="cal-table-wrap">
          <table className="cal-table">
            <thead>
              <tr>
                <th>Estudiante</th>
                <th>Promedio ponderado</th>
              </tr>
            </thead>
            <tbody>
              {filas.map((fila) => (
                <tr key={fila.id_estudiante}>
                  <td>{fila.nombre || `Estudiante ${fila.id_estudiante}`}</td>
                  <td>
                    <span className={`cal-badge ${claseBadge(fila.promedio)}`}>
                      {formatearNota(fila.promedio)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
