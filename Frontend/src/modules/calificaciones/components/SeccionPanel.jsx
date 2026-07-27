import { useEffect, useRef, useState } from "react";
import { crearSeccion, listarSecciones, eliminarActividad, eliminarSeccion } from "../services/calificacionService";
import { claseBadge, formatearNota } from "../utils/notas";
import ActividadModal from "./ActividadModal";

/**
 * Acordeón de secciones de porcentaje de un curso.
 * La sección expandida es la sección activa: el padre la recibe por onSeleccionarSeccion
 * y es quien carga sus actividades (una sola llamada compartida con TablaNotas).
 *
 * En modo readOnly (vista Estudiante) se ocultan los formularios de creación y, si se
 * pasa notaPorActividad, cada actividad muestra la nota del estudiante.
 */
export default function SeccionPanel({
  idCurso,
  periodoAbierto = true,
  readOnly = false,
  seccionActiva,
  onSeleccionarSeccion,
  actividades = [],
  cargandoActividades = false,
  onActividadCreada,
  notaPorActividad
}) {
  const [secciones, setSecciones] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [form, setForm] = useState({ nombre_seccion: "", porcentaje: "" });
  const [guardando, setGuardando] = useState(false);
  const [errorForm, setErrorForm] = useState("");
  const [modalActividad, setModalActividad] = useState(null);
  const [comentarioModal, setComentarioModal] = useState(null);
  const closeComentarioButtonRef = useRef(null);

  const puedeEditar = !readOnly && periodoAbierto;

  // Refresco manual tras crear una sección (se dispara desde un handler, no desde el efecto).
  const cargarSecciones = async () => {
    setCargando(true);
    setError("");
    try {
      setSecciones(await listarSecciones(idCurso));
    } catch (err) {
      setError(err.detail || "No se pudieron cargar las secciones");
    } finally {
      setCargando(false);
    }
  };

  // El padre monta este panel con key={id_curso}, así que la carga inicial
  // basta con el estado `cargando` arrancando en true.
  useEffect(() => {
    if (!idCurso) return undefined;

    let vigente = true;

    listarSecciones(idCurso)
      .then((data) => {
        if (vigente) setSecciones(data);
      })
      .catch((err) => {
        if (vigente) setError(err.detail || "No se pudieron cargar las secciones");
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });

    return () => {
      vigente = false;
    };
  }, [idCurso]);

  useEffect(() => {
    if (!comentarioModal) return undefined;

    const handleEscape = (event) => {
      if (event.key === "Escape") {
        setComentarioModal(null);
      }
    };

    document.addEventListener("keydown", handleEscape);
    closeComentarioButtonRef.current?.focus();

    return () => {
      document.removeEventListener("keydown", handleEscape);
    };
  }, [comentarioModal]);

  const handleCrearSeccion = async (e) => {
    e.preventDefault();
    setErrorForm("");
    setGuardando(true);
    try {
      await crearSeccion({
        nombre_seccion: form.nombre_seccion.trim(),
        porcentaje: Number(form.porcentaje),
        id_curso: idCurso
      });
      setForm({ nombre_seccion: "", porcentaje: "" });
      setMostrarFormulario(false);
      await cargarSecciones();
    } catch (err) {
      setErrorForm(err.detail || "No se pudo crear la sección");
    } finally {
      setGuardando(false);
    }
  };

  const handleEliminarSeccion = async (seccion) => {
    if (!window.confirm(`¿Eliminar la sección "${seccion.nombre_seccion}" y todas sus actividades?`)) {
      return;
    }
    setError("");
    try {
      await eliminarSeccion(seccion.id_seccion);
      await cargarSecciones();
      if (seccionActiva?.id_seccion === seccion.id_seccion) {
        onSeleccionarSeccion(null);
      }
    } catch (err) {
      setError(err.detail || "No se pudo eliminar la sección");
    }
  };

  const handleEliminarActividad = async (actividad) => {
    if (!window.confirm(`¿Eliminar la actividad "${actividad.nombre}"?`)) {
      return;
    }
    setError("");
    try {
      await eliminarActividad(actividad.id_actividad);
      onActividadCreada?.();
    } catch (err) {
      setError(err.detail || "No se pudo eliminar la actividad");
    }
  };

  const alternarSeccion = (seccion) => {
    const misma = seccionActiva?.id_seccion === seccion.id_seccion;
    onSeleccionarSeccion(misma ? null : seccion);
  };

  if (cargando) return <p className="cal-hint">Cargando secciones...</p>;

  return (
    <>
      <div className="cal-card-head">
        <h3 className="cal-section-title">Secciones de porcentaje</h3>
        {puedeEditar && (
          <div className="cal-card-head-actions">
            <button
              type="button"
              className="cal-btn secondary small"
              onClick={() => setMostrarFormulario((valor) => !valor)}
            >
              {mostrarFormulario ? "Cancelar" : "Nueva sección"}
            </button>
            {seccionActiva && (
              <button
                type="button"
                className="cal-btn danger small"
                onClick={() => handleEliminarSeccion(seccionActiva)}
              >
                Eliminar sección
              </button>
            )}
          </div>
        )}
      </div>

      {error && <p className="cal-error">{error}</p>}

      {puedeEditar && mostrarFormulario && (
        <form className="cal-inline-form" onSubmit={handleCrearSeccion}>
          <div className="cal-field nombre">
            <label htmlFor="seccion-nombre">Nombre de la sección</label>
            <input
              id="seccion-nombre"
              value={form.nombre_seccion}
              onChange={(e) => setForm({ ...form, nombre_seccion: e.target.value })}
              maxLength={50}
              placeholder="Primer corte"
              required
            />
          </div>
          <div className="cal-field pct">
            <label htmlFor="seccion-porcentaje">Porcentaje</label>
            <input
              id="seccion-porcentaje"
              type="number"
              min="0.01"
              max="100"
              step="0.01"
              value={form.porcentaje}
              onChange={(e) => setForm({ ...form, porcentaje: e.target.value })}
              placeholder="30"
              required
            />
          </div>
          <button type="submit" className="cal-btn primary" disabled={guardando}>
            {guardando ? "Guardando..." : "Crear"}
          </button>
        </form>
      )}

      {errorForm && <p className="cal-error">{errorForm}</p>}

      {secciones.length === 0 ? (
        <p className="cal-empty">Este curso todavía no tiene secciones de porcentaje.</p>
      ) : (
        secciones.map((seccion) => {
          const activa = seccionActiva?.id_seccion === seccion.id_seccion;
          return (
            <div className="cal-seccion" key={seccion.id_seccion}>
              <div
                className={`cal-seccion-header ${activa ? "selected" : ""}`}
                onClick={() => alternarSeccion(seccion)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    alternarSeccion(seccion);
                  }
                }}
              >
                <span className="cal-seccion-name">{seccion.nombre_seccion}</span>
                <span className="cal-seccion-pct">{Number(seccion.porcentaje).toFixed(2)}%</span>
              </div>

              {activa && (
                <div className="cal-seccion-body">
                  {seccion.advertencia && (
                    <p className="cal-warn-msg">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                        <line x1="12" y1="9" x2="12" y2="13" />
                        <line x1="12" y1="17" x2="12.01" y2="17" />
                      </svg>
                      {seccion.advertencia}
                    </p>
                  )}

                  {cargandoActividades ? (
                    <p className="cal-hint">Cargando actividades...</p>
                  ) : actividades.length === 0 ? (
                    <p className="cal-hint">Esta sección aún no tiene actividades.</p>
                  ) : (
                    <ul className="cal-actividad-list">
                      {actividades.map((actividad) => {
                        const nota = notaPorActividad?.[actividad.id_actividad];
                        return (
                          <li className={`cal-actividad-item${readOnly ? "" : " docente"}`} key={actividad.id_actividad}>
                            <div className="cal-actividad-item-main">
                              <span>{actividad.nombre}</span>
                              <span className="cal-actividad-fecha">{actividad.fecha}</span>
                            </div>
                            {readOnly ? (
                              <div className="cal-actividad-comment-cell">
                                {nota?.comentario ? (
                                  <p
                                    className={`cal-actividad-comment${readOnly ? " read-only" : ""}`}
                                    onClick={readOnly ? () => setComentarioModal(nota.comentario) : undefined}
                                    role={readOnly ? "button" : undefined}
                                    tabIndex={readOnly ? 0 : undefined}
                                    onKeyDown={readOnly ? (e) => {
                                      if (e.key === "Enter" || e.key === " ") {
                                        e.preventDefault();
                                        setComentarioModal(nota.comentario);
                                      }
                                    } : undefined}
                                  >
                                    {nota.comentario}
                                  </p>
                                ) : (
                                  <div className="cal-actividad-comment-spacer" />
                                )}
                              </div>
                            ) : nota && nota.comentario ? (
                              <p
                                className={`cal-actividad-comment${readOnly ? " read-only" : ""}`}
                                onClick={readOnly ? () => setComentarioModal(nota.comentario) : undefined}
                                role={readOnly ? "button" : undefined}
                                tabIndex={readOnly ? 0 : undefined}
                                onKeyDown={readOnly ? (e) => {
                                  if (e.key === "Enter" || e.key === " ") {
                                    e.preventDefault();
                                    setComentarioModal(nota.comentario);
                                  }
                                } : undefined}
                              >
                                {nota.comentario}
                              </p>
                            ) : (
                              <div className="cal-actividad-comment-spacer" />
                            )}
                            {readOnly && (
                              <span className={`cal-badge ${claseBadge(nota?.calificacion)} `}>
                                {formatearNota(nota?.calificacion)}
                              </span>
                            )}
                            {puedeEditar && (
                              <button
                                type="button"
                                className="cal-btn danger icon"
                                aria-label={`Eliminar actividad ${actividad.nombre}`}
                                onClick={() => handleEliminarActividad(actividad)}
                              >
                                ×
                              </button>
                            )}
                          </li>
                        );
                      })}
                    </ul>
                  )}

                  {puedeEditar && (
                    <div className="cal-seccion-actions">
                      <button
                        type="button"
                        className="cal-btn secondary small"
                        onClick={() => setModalActividad(seccion)}
                      >
                        Nueva actividad
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })
      )}

      {modalActividad && (
        <ActividadModal
          seccion={modalActividad}
          onCerrar={() => setModalActividad(null)}
          onCreada={onActividadCreada}
        />
      )}

      {comentarioModal && (
        <div className="cal-modal-overlay" onClick={() => setComentarioModal(null)}>
          <div
            className="cal-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="cal-comment-dialog-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="cal-modal-header">
              <span className="cal-modal-title" id="cal-comment-dialog-title">Comentario completo</span>
              <button
                ref={closeComentarioButtonRef}
                type="button"
                className="cal-modal-close"
                onClick={() => setComentarioModal(null)}
                aria-label="Cerrar comentario"
              >
                ×
              </button>
            </div>
            <p>{comentarioModal}</p>
          </div>
        </div>
      )}
    </>
  );
}
