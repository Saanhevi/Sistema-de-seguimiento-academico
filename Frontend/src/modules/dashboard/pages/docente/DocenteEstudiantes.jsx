import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../../../../context/AuthContext";
import { asociarEstudianteACurso, crearMatricula, listarCursosDocente, listarEstudiantesPorCurso } from "../../../cursos/services/cursoService";

function IconRefresh({ className = "" }) {
  return (
    <svg className={className} width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12a9 9 0 1 1-3-6.7" />
      <polyline points="21 3 21 9 15 9" />
    </svg>
  );
}

function IconSearch({ className = "" }) {
  return (
    <svg className={className} width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="7" />
      <path d="m21 21-4.3-4.3" />
    </svg>
  );
}

function IconUsers({ className = "" }) {
  return (
    <svg className={className} width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

function IconUserPlus({ className = "" }) {
  return (
    <svg className={className} width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M15 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="8" cy="7" r="4" />
      <path d="M20 8v6" />
      <path d="M17 11h6" />
    </svg>
  );
}

function IconCheck({ className = "" }) {
  return (
    <svg className={className} width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}

function IconLoader({ className = "" }) {
  return (
    <svg className={className} width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2a10 10 0 1 0 10 10" />
    </svg>
  );
}

export default function DocenteEstudiantes() {
  const { user } = useAuth();
  const [cursos, setCursos] = useState([]);
  const [cursoSeleccionado, setCursoSeleccionado] = useState("");
  const [detalleCurso, setDetalleCurso] = useState(null);
  const [cargandoCursos, setCargandoCursos] = useState(false);
  const [cargandoDetalle, setCargandoDetalle] = useState(false);
  const [agregandoId, setAgregandoId] = useState(null);
  const [matriculando, setMatriculando] = useState(false);
  const [busqueda, setBusqueda] = useState("");
  const [matriculaForm, setMatriculaForm] = useState({
    id_estudiante: "",
    anio: new Date().getFullYear(),
  });
  const [mensaje, setMensaje] = useState({ type: "", text: "" });

  useEffect(() => {
    if (user) {
      cargarCursos();
    }
  }, [user]);

  async function cargarCursos() {
    try {
      setCargandoCursos(true);
      const data = await listarCursosDocente(user.id_usuario);
      setCursos(data);
      setMensaje({ type: "", text: "" });
    } catch (error) {
      console.error(error);
      setMensaje({
        type: "error",
        text: error.detail || "No fue posible cargar los cursos del docente."
      });
    } finally {
      setCargandoCursos(false);
    }
  }

  async function cargarDetalleCurso(idCurso) {
    if (!idCurso) {
      setDetalleCurso(null);
      return;
    }

    try {
      setCargandoDetalle(true);
      const data = await listarEstudiantesPorCurso(idCurso);
      setDetalleCurso(data);
      setMensaje({ type: "", text: "" });
    } catch (error) {
      console.error(error);
      setDetalleCurso(null);
      setMensaje({
        type: "error",
        text: error.detail || "No fue posible cargar los estudiantes del curso."
      });
    } finally {
      setCargandoDetalle(false);
    }
  }

  async function seleccionarCurso(idCurso) {
    setCursoSeleccionado(idCurso);
    setBusqueda("");
    const curso = cursos.find((item) => String(item.id_curso) === String(idCurso));
    setMatriculaForm((prev) => ({
      ...prev,
      anio: curso?.anio || new Date().getFullYear(),
    }));
    await cargarDetalleCurso(idCurso);
  }

  async function matricularEstudiante(e) {
    e.preventDefault();

    if (!cursoActual) {
      setMensaje({ type: "error", text: "Selecciona un curso para matricular estudiantes." });
      return;
    }

    try {
      setMatriculando(true);
      await crearMatricula({
        id_estudiante: Number(matriculaForm.id_estudiante),
        id_grado: Number(cursoActual.id_grado),
        anio: Number(matriculaForm.anio || cursoActual.anio),
      });

      setMensaje({
        type: "success",
        text: `Matrícula creada en ${cursoActual.grado} (${matriculaForm.anio}).`
      });
      setMatriculaForm((prev) => ({ ...prev, id_estudiante: "" }));
      await cargarDetalleCurso(cursoSeleccionado);
    } catch (error) {
      setMensaje({
        type: "error",
        text: error.detail || "No fue posible registrar la matrícula para este estudiante."
      });
    } finally {
      setMatriculando(false);
    }
  }

  async function agregarEstudiante(estudiante) {
    if (!cursoSeleccionado) {
      setMensaje({ type: "error", text: "Selecciona un curso antes de agregar estudiantes." });
      return;
    }

    try {
      setAgregandoId(estudiante.id_estudiante);
      const response = await asociarEstudianteACurso(cursoSeleccionado, estudiante.id_estudiante);
      setMensaje({ type: "success", text: response.mensaje || "Estudiante agregado correctamente." });
      await cargarDetalleCurso(cursoSeleccionado);
    } catch (error) {
      console.error(error);
      setMensaje({
        type: "error",
        text: error.detail || "No fue posible agregar el estudiante al curso."
      });
    } finally {
      setAgregandoId(null);
    }
  }

  const cursoActual = useMemo(
    () => cursos.find((curso) => String(curso.id_curso) === String(cursoSeleccionado)),
    [cursos, cursoSeleccionado]
  );

  const estudiantesDisponibles = useMemo(() => {
    const items = detalleCurso?.estudiantes_disponibles || [];
    const termino = busqueda.trim().toLowerCase();

    if (!termino) return items;

    return items.filter((estudiante) => {
      const nombreCompleto = `${estudiante.nombres} ${estudiante.apellidos}`.toLowerCase();
      return nombreCompleto.includes(termino) || String(estudiante.id_estudiante).includes(termino);
    });
  }, [detalleCurso, busqueda]);

  const estudiantesAsociados = detalleCurso?.estudiantes_asociados || [];

  return (
    <div className="docente-estudiantes">
      <div className="docente-estudiantes-hero">
        <div>
          <p className="docente-kicker">Gestión de estudiantes por materia</p>
          <h2>Añade estudiantes a tu curso</h2>
          <p>
            Selecciona una materia, revisa los estudiantes matriculados en el grado y confirma su asociación desde esta vista.
          </p>
        </div>
        <button className="docente-refresh" type="button" onClick={cargarCursos}>
          {cargandoCursos ? <IconLoader className="docente-spin" /> : <IconRefresh />}
          Actualizar cursos
        </button>
      </div>

      {mensaje.text && <div className={`docente-alert ${mensaje.type}`}>{mensaje.text}</div>}

      <div className="docente-summary-grid">
        <article className="docente-summary-card">
          <span>Cursos asignados</span>
          <strong>{cursos.length}</strong>
          <small>Disponibles para gestión</small>
        </article>
        <article className="docente-summary-card">
          <span>Estudiantes disponibles</span>
          <strong>{detalleCurso?.estudiantes_disponibles?.length ?? "—"}</strong>
          <small>Matriculados en el grado</small>
        </article>
        <article className="docente-summary-card">
          <span>Estudiantes asociados</span>
          <strong>{estudiantesAsociados.length}</strong>
          <small>Guardados en la lista del curso</small>
        </article>
      </div>

      <div className="docente-grid">
        <section className="docente-panel">
          <div className="docente-panel-header">
            <div>
              <h3>Selecciona un curso</h3>
              <p>Docente autenticado · cursos cargados desde el backend</p>
            </div>
            <IconUsers />
          </div>

          <label className="docente-field">
            <span>Curso</span>
            <select
              value={cursoSeleccionado}
              onChange={(e) => seleccionarCurso(e.target.value)}
              disabled={cargandoCursos}
            >
              <option value="">Selecciona un curso</option>
              {cursos.map((curso) => (
                <option key={curso.id_curso} value={curso.id_curso}>
                  {curso.grado} · {curso.materia} · {curso.periodo} ({curso.anio})
                </option>
              ))}
            </select>
          </label>

          {cursoActual && (
            <div className="docente-course-meta">
              <span className="docente-pill">Grado: {cursoActual.grado}</span>
              <span className="docente-pill">Materia: {cursoActual.materia}</span>
              <span className="docente-pill">Periodo: {cursoActual.periodo}</span>
            </div>
          )}

          {cursoActual && (
            <form className="docente-matricula-form" onSubmit={matricularEstudiante}>
              <h4>Matrícula por grado</h4>
              <p>
                Registra la matrícula del estudiante en el grado del curso seleccionado.
              </p>
              <div className="docente-inline-fields">
                <label className="docente-field">
                  <span>ID estudiante</span>
                  <input
                    type="number"
                    min="1"
                    required
                    value={matriculaForm.id_estudiante}
                    onChange={(e) => setMatriculaForm((prev) => ({ ...prev, id_estudiante: e.target.value }))}
                    placeholder="Ej. 15"
                  />
                </label>
                <label className="docente-field">
                  <span>Año académico</span>
                  <input
                    type="number"
                    min="2000"
                    max="2100"
                    required
                    value={matriculaForm.anio}
                    onChange={(e) => setMatriculaForm((prev) => ({ ...prev, anio: e.target.value }))}
                  />
                </label>
              </div>
              <button className="docente-refresh" type="submit" disabled={matriculando}>
                {matriculando ? <IconLoader className="docente-spin" /> : <IconUserPlus />}
                Matricular estudiante
              </button>
            </form>
          )}

          {!cursoSeleccionado && !cargandoCursos && (
            <p className="docente-empty">Elige un curso para ver los estudiantes disponibles.</p>
          )}
        </section>

        <section className="docente-panel">
          <div className="docente-panel-header">
            <div>
              <h3>Estudiantes disponibles</h3>
              <p>{detalleCurso ? `${estudiantesDisponibles.length} estudiantes listos para agregar` : "Selecciona un curso para cargar la lista"}</p>
            </div>
            <IconSearch />
          </div>

          <label className="docente-field">
            <span>Buscar estudiante</span>
            <input
              type="text"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              placeholder="Nombre o documento"
              disabled={!detalleCurso}
            />
          </label>

          {cargandoDetalle ? (
            <div className="docente-loading">
              <IconLoader className="docente-spin" />
              Cargando estudiantes...
            </div>
          ) : estudiantesDisponibles.length === 0 ? (
            <p className="docente-empty">
              {detalleCurso ? "No hay estudiantes disponibles para agregar con este filtro." : "No hay datos para mostrar."}
            </p>
          ) : (
            <div className="docente-student-list">
              {estudiantesDisponibles.map((estudiante) => (
                <article key={estudiante.id_estudiante} className="docente-student-card">
                  <div className="docente-student-avatar">
                    {String(estudiante.nombres || "").charAt(0)}{String(estudiante.apellidos || "").charAt(0)}
                  </div>
                  <div className="docente-student-info">
                    <strong>{estudiante.nombres} {estudiante.apellidos}</strong>
                    <span>ID {estudiante.id_estudiante}</span>
                    <small>{estudiante.correo}</small>
                  </div>
                  <button
                    type="button"
                    className="docente-add-btn"
                    onClick={() => agregarEstudiante(estudiante)}
                    disabled={agregandoId === estudiante.id_estudiante}
                  >
                    {agregandoId === estudiante.id_estudiante ? (
                      <IconLoader className="docente-spin" />
                    ) : (
                      <IconUserPlus />
                    )}
                    Agregar
                  </button>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>

      <section className="docente-panel docente-panel-wide">
        <div className="docente-panel-header">
          <div>
            <h3>Estudiantes asociados al curso</h3>
            <p>Lista visual del curso seleccionado</p>
          </div>
          <IconCheck />
        </div>

        {estudiantesAsociados.length === 0 ? (
          <p className="docente-empty">Todavía no se han agregado estudiantes a este curso.</p>
        ) : (
          <div className="docente-associated-grid">
            {estudiantesAsociados.map((estudiante) => (
              <div key={estudiante.id_estudiante} className="docente-associated-chip">
                <div>
                  <strong>{estudiante.nombres} {estudiante.apellidos}</strong>
                  <span>ID {estudiante.id_estudiante}</span>
                </div>
                <small>Agregado</small>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
