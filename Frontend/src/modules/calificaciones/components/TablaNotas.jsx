import { useEffect, useMemo, useState } from "react";
import { listarEstudiantesDeGrado, listarNotas, registrarNota } from "../services/calificacionService";
import { claseBadge, formatearNota, promedioSimple } from "../utils/notas";
import CargaMasivaModal from "./CargaMasivaModal";

const claveNota = (idActividad, idEstudiante) => `${idActividad}-${idEstudiante}`;

/**
 * Tabla de notas de la sección activa.
 * Filas: estudiantes del grado del curso. Columnas: actividades de la sección.
 * Las actividades llegan por prop desde la vista padre para no repetir el GET
 * que ya hace SeccionPanel.
 */
export default function TablaNotas({ seccionActiva, idGrado, anio, periodoAbierto, actividades = [] }) {
  const [estudiantes, setEstudiantes] = useState([]);
  const [notas, setNotas] = useState({});
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [editando, setEditando] = useState(null);
  const [borrador, setBorrador] = useState({ calificacion: "", comentario: "" });
  const [errorCelda, setErrorCelda] = useState("");
  const [modalMasiva, setModalMasiva] = useState(null);

  // Estudiantes del grado: solo cambian si cambia el curso.
  useEffect(() => {
    if (!idGrado) return;

    let vigente = true;
    listarEstudiantesDeGrado(idGrado, anio)
      .then((data) => {
        if (vigente) setEstudiantes(data);
      })
      .catch((err) => {
        if (vigente) setError(err.detail || "No se pudieron cargar los estudiantes del grado");
      });

    return () => {
      vigente = false;
    };
  }, [idGrado, anio]);

  // Una llamada por actividad; con la lista vacía Promise.all resuelve de inmediato
  // y deja el mapa de notas limpio.
  useEffect(() => {
    let vigente = true;

    Promise.all(actividades.map((actividad) => listarNotas(actividad.id_actividad)))
      .then((respuestas) => {
        if (!vigente) return;
        const mapa = {};
        respuestas.flat().forEach((nota) => {
          mapa[claveNota(nota.id_actividad, nota.id_estudiante)] = nota;
        });
        setNotas(mapa);
        setEditando(null);
      })
      .catch((err) => {
        if (vigente) setError(err.detail || "No se pudieron cargar las notas");
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });

    return () => {
      vigente = false;
    };
  }, [actividades]);

  const promediosPorActividad = useMemo(() => {
    const resultado = {};
    actividades.forEach((actividad) => {
      const valores = estudiantes.map(
        (estudiante) => notas[claveNota(actividad.id_actividad, estudiante.id_estudiante)]?.calificacion ?? null
      );
      resultado[actividad.id_actividad] = promedioSimple(valores);
    });
    return resultado;
  }, [actividades, estudiantes, notas]);

  const abrirEditor = (idActividad, idEstudiante) => {
    if (!periodoAbierto) return;
    const actual = notas[claveNota(idActividad, idEstudiante)];
    setBorrador({
      calificacion: actual ? String(actual.calificacion) : "",
      comentario: actual?.comentario || ""
    });
    setErrorCelda("");
    setEditando(claveNota(idActividad, idEstudiante));
  };

  const guardarNota = async (idActividad, idEstudiante) => {
    const calificacion = Number(borrador.calificacion);
    if (borrador.calificacion === "" || Number.isNaN(calificacion)) {
      setErrorCelda("Escribe una calificación entre 0.00 y 5.00");
      return;
    }
    try {
      const nota = await registrarNota({
        id_actividad: idActividad,
        id_estudiante: idEstudiante,
        calificacion,
        comentario: borrador.comentario.trim() || null
      });
      setNotas((previas) => ({ ...previas, [claveNota(idActividad, idEstudiante)]: nota }));
      setEditando(null);
      setErrorCelda("");
    } catch (err) {
      setErrorCelda(err.detail || "No se pudo guardar la nota");
    }
  };

  if (!seccionActiva) {
    return <p className="cal-empty">Selecciona una sección para ver las notas.</p>;
  }

  if (actividades.length === 0) {
    return <p className="cal-empty">Crea una actividad en esta sección para empezar a calificar.</p>;
  }

  if (estudiantes.length === 0) {
    return <p className="cal-empty">No hay estudiantes matriculados en el grado de este curso.</p>;
  }

  return (
    <>
      {error && <p className="cal-error">{error}</p>}
      {errorCelda && <p className="cal-error">{errorCelda}</p>}
      {cargando && <p className="cal-hint">Cargando notas...</p>}

      <div className="cal-table-wrap">
        <table className="cal-table">
          <thead>
            <tr>
              <th>Estudiante</th>
              {actividades.map((actividad) => (
                <th key={actividad.id_actividad}>
                  {actividad.nombre}
                  <small>{actividad.fecha}</small>
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {estudiantes.map((estudiante) => (
              <tr key={estudiante.id_estudiante}>
                <td>
                  {estudiante.nombre} {estudiante.apellido}
                </td>
                {actividades.map((actividad) => {
                  const clave = claveNota(actividad.id_actividad, estudiante.id_estudiante);
                  const nota = notas[clave];
                  const enEdicion = editando === clave;

                  if (enEdicion) {
                    return (
                      <td key={actividad.id_actividad}>
                        <div className="cal-grade-editor">
                          <input
                            type="number"
                            min="0"
                            max="5"
                            step="0.01"
                            autoFocus
                            value={borrador.calificacion}
                            onChange={(e) => setBorrador({ ...borrador, calificacion: e.target.value })}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") guardarNota(actividad.id_actividad, estudiante.id_estudiante);
                              if (e.key === "Escape") setEditando(null);
                            }}
                          />
                          <input
                            type="text"
                            maxLength={100}
                            placeholder="Comentario (opcional)"
                            value={borrador.comentario}
                            onChange={(e) => setBorrador({ ...borrador, comentario: e.target.value })}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") guardarNota(actividad.id_actividad, estudiante.id_estudiante);
                              if (e.key === "Escape") setEditando(null);
                            }}
                          />
                          <div className="cal-grade-actions">
                            <button
                              type="button"
                              className="save"
                              onClick={() => guardarNota(actividad.id_actividad, estudiante.id_estudiante)}
                            >
                              Guardar
                            </button>
                            <button type="button" className="cancel" onClick={() => setEditando(null)}>
                              Cancelar
                            </button>
                          </div>
                        </div>
                      </td>
                    );
                  }

                  return (
                    <td key={actividad.id_actividad}>
                      <button
                        type="button"
                        className="cal-cell-btn"
                        disabled={!periodoAbierto}
                        title={periodoAbierto ? "Editar nota" : "Periodo cerrado"}
                        onClick={() => abrirEditor(actividad.id_actividad, estudiante.id_estudiante)}
                      >
                        <span className={`cal-badge ${claseBadge(nota?.calificacion)}`}>
                          {periodoAbierto ? "" : "🔒 "}
                          {formatearNota(nota?.calificacion)}
                        </span>
                        {nota?.comentario && <span className="cal-cell-comment">{nota.comentario}</span>}
                      </button>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>

          <tfoot>
            <tr>
              <td>Promedio</td>
              {actividades.map((actividad) => (
                <td key={actividad.id_actividad}>
                  <span className={`cal-badge ${claseBadge(promediosPorActividad[actividad.id_actividad])}`}>
                    {formatearNota(promediosPorActividad[actividad.id_actividad])}
                  </span>
                  {periodoAbierto && (
                    <div>
                      <button
                        type="button"
                        className="cal-btn secondary small"
                        style={{ marginTop: "8px" }}
                        onClick={() => setModalMasiva(actividad)}
                      >
                        Carga masiva
                      </button>
                    </div>
                  )}
                </td>
              ))}
            </tr>
          </tfoot>
        </table>
      </div>

      {modalMasiva && (
        <CargaMasivaModal
          actividad={modalMasiva}
          estudiantes={estudiantes}
          notas={notas}
          onCerrar={() => setModalMasiva(null)}
          onGuardadas={(nuevas) =>
            setNotas((previas) => {
              const copia = { ...previas };
              nuevas.forEach((nota) => {
                copia[claveNota(nota.id_actividad, nota.id_estudiante)] = nota;
              });
              return copia;
            })
          }
        />
      )}
    </>
  );
}
