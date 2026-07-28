import { useEffect, useMemo, useState } from "react";
import { Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../../../../context/AuthContext";
import { listarProfesores } from "../../../profesores/services/profesorService";
import { listarEstudiantes } from "../../../estudiantes/services/estudianteService";
import {
  listarCursos,
  listarGrados,
  listarMatriculas,
  listarMaterias,
  listarPeriodos,
} from "../../../cursos/services/cursoService";

const HOME_PATH = "/dashboard/admin";
const numberFormatter = new Intl.NumberFormat("es-EC");

function formatCount(value) {
  return numberFormatter.format(value);
}

function getInitials(nombres = "", apellidos = "") {
  return `${nombres.trim()[0] ?? ""}${apellidos.trim()[0] ?? ""}`.toUpperCase();
}

function getErrorMessage(error) {
  return error?.response?.data?.detail || error?.detail || "No se pudo cargar el resumen administrativo.";
}

function compareByName(a, b) {
  return `${a.nombres} ${a.apellidos}`.localeCompare(`${b.nombres} ${b.apellidos}`, "es");
}

function getNestedText(value) {
  if (typeof value === "string") {
    return value;
  }

  if (typeof value === "number") {
    return String(value);
  }

  return value?.nombre || value?.name || value?.titulo || "";
}

function getCourseLabel(course, field) {
  return getNestedText(course?.[field]).trim();
}

export default function PortalAdmin() {
  const location = useLocation();
  const isHomeView = location.pathname === HOME_PATH;
  const { user } = useAuth();

  const [loading, setLoading] = useState(isHomeView);
  const [error, setError] = useState("");
  const [profesores, setProfesores] = useState([]);
  const [estudiantes, setEstudiantes] = useState([]);
  const [grados, setGrados] = useState([]);
  const [materias, setMaterias] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [cursos, setCursos] = useState([]);
  const [matriculas, setMatriculas] = useState([]);

  useEffect(() => {
    if (!isHomeView) {
      return undefined;
    }

    let isMounted = true;

    const cargarResumen = async () => {
      setLoading(true);
      setError("");

      try {
        const [profesoresData, estudiantesData, gradosData, materiasData, periodosData, cursosData, matriculasData] = await Promise.all([
          listarProfesores(),
          listarEstudiantes(true),
          listarGrados(),
          listarMaterias(),
          listarPeriodos(),
          listarCursos(),
          listarMatriculas(),
        ]);

        if (!isMounted) {
          return;
        }

        setProfesores(profesoresData);
        setEstudiantes(estudiantesData);
        setGrados(gradosData);
        setMaterias(materiasData);
        setPeriodos(periodosData);
        setCursos(cursosData);
        setMatriculas(matriculasData);
      } catch (fetchError) {
        if (isMounted) {
          setError(getErrorMessage(fetchError));
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    cargarResumen();

    return () => {
      isMounted = false;
    };
  }, [isHomeView]);

  const periodosOrdenados = useMemo(
    () => [...periodos].sort((a, b) => b.anio - a.anio || a.nombre.localeCompare(b.nombre, "es")),
    [periodos],
  );

  const periodoActivo = useMemo(
    () => periodosOrdenados.find((item) => item.estado === "Abierto") || periodosOrdenados[0] || null,
    [periodosOrdenados],
  );

  const estudiantesActivos = useMemo(() => estudiantes.filter((item) => item.estado), [estudiantes]);
  const profesoresActivos = useMemo(() => profesores.filter((item) => item.estado), [profesores]);
  const periodosAbiertos = useMemo(() => periodos.filter((item) => item.estado === "Abierto"), [periodos]);

  const cursosPorDocente = useMemo(() => {
    const conteo = new Map();

    cursos.forEach((curso) => {
      conteo.set(curso.id_docente, (conteo.get(curso.id_docente) || 0) + 1);
    });

    return conteo;
  }, [cursos]);

  const gradosConMatriculas = useMemo(() => {
    return grados
      .map((grado) => {
        const matriculasDelGrado = matriculas.filter((item) => item.id_grado === grado.id_grado);
        const cursosDelGrado = cursos.filter((item) => item.id_grado === grado.id_grado);

        return {
          ...grado,
          matriculas: matriculasDelGrado.length,
          cursos: cursosDelGrado.length,
        };
      })
      .sort((a, b) => b.matriculas - a.matriculas || a.nombre.localeCompare(b.nombre, "es"));
  }, [grados, matriculas, cursos]);

  const docentesDestacados = useMemo(() => {
    return profesoresActivos
      .map((profesor) => ({
        ...profesor,
        cursosAsignados: cursosPorDocente.get(profesor.id) || 0,
      }))
      .sort((a, b) => b.cursosAsignados - a.cursosAsignados || compareByName(a, b))
      .slice(0, 5);
  }, [profesoresActivos, cursosPorDocente]);

  const cursosRecientes = useMemo(() => {
    return [...cursos]
      .sort((a, b) => {
        const yearDiff = Number(b.anio ?? 0) - Number(a.anio ?? 0);
        if (yearDiff !== 0) {
          return yearDiff;
        }

        const gradoCompare = getCourseLabel(a, "grado").localeCompare(getCourseLabel(b, "grado"), "es");
        if (gradoCompare !== 0) {
          return gradoCompare;
        }

        return getCourseLabel(a, "materia").localeCompare(getCourseLabel(b, "materia"), "es");
      })
      .slice(0, 6);
  }, [cursos]);

  const periodosRecientes = useMemo(() => periodosOrdenados.slice(0, 4), [periodosOrdenados]);

  const resumenKpis = [
    {
      label: "Estudiantes",
      value: estudiantesActivos.length,
      detail: `${estudiantes.length} registrados`,
      tone: "teal",
      marker: "E",
    },
    {
      label: "Docentes activos",
      value: profesoresActivos.length,
      detail: `${profesores.length} registrados`,
      tone: "blue",
      marker: "D",
    },
    {
      label: "Cursos",
      value: cursos.length,
      detail: `${periodosAbiertos.length} período${periodosAbiertos.length === 1 ? "" : "s"} abierto${periodosAbiertos.length === 1 ? "" : "s"}`,
      tone: "orange",
      marker: "C",
    },
    {
      label: "Grados",
      value: grados.length,
      detail: `${materias.length} materias registradas`,
      tone: "purple",
      marker: "G",
    },
  ];

  const maxMatriculas = Math.max(...gradosConMatriculas.map((item) => item.matriculas), 1);
  const cursosVigentes = periodoActivo
    ? cursos.filter((curso) =>
      Number(curso.anio ?? 0) === Number(periodoActivo.anio) &&
      getCourseLabel(curso, "periodo") === periodoActivo.nombre
    )
    : cursos;

  if (!isHomeView) {
    return <Outlet />;
  }

  return (
    <main className="main admin-home" aria-busy={loading}>
      <section className="admin-hero">
        <div className="admin-hero-copy">
          <p className="admin-kicker">Panel administrativo</p>
          <h1>Resumen institucional</h1>
          <p>
            Hola {user?.nombres ?? "Administrador"}. Esta vista consolida información real del sistema para revisar la
            situación académica sin salir del flujo principal.
          </p>

          <div className="admin-chip-list">
            <span className="admin-chip">
              Periodo activo: {periodoActivo ? `${periodoActivo.nombre} · ${periodoActivo.anio}` : "Sin periodo abierto"}
            </span>
            <span className="admin-chip soft">
              Matriculas vigentes: {formatCount(matriculas.length)}
            </span>
            <span className="admin-chip soft">
              Cursos vigentes: {formatCount(cursosVigentes.length)}
            </span>
          </div>
        </div>

        <aside className="admin-hero-card">
          <span>Estado actual</span>
          <strong>{periodoActivo ? `${periodoActivo.nombre} · ${periodoActivo.anio}` : "Sin periodo abierto"}</strong>
          <p>
            {periodoActivo
              ? `${periodosAbiertos.length} periodo${periodosAbiertos.length === 1 ? "" : "s"} abierto${periodosAbiertos.length === 1 ? "" : "s"} en la base de datos.`
              : "No hay períodos abiertos en la base de datos."}
          </p>
        </aside>
      </section>

      {error ? (
        <section className="panel">
          <p className="admin-error">{error}</p>
        </section>
      ) : null}

      <div className="kpi-grid">
        {resumenKpis.map((item) => (
          <article key={item.label} className={`kpi-card tone-${item.tone}`}>
            <div className={`kpi-icon ${item.tone}`} aria-hidden="true">
              {item.marker}
            </div>
            <p className="kpi-value">{formatCount(item.value)}</p>
            <p className="kpi-label">{item.label}</p>
            <p className="kpi-sub">{item.detail}</p>
          </article>
        ))}
      </div>

      <div className="content-grid">
        <section className="panel admin-panel-wide">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">Matrículas por grado</h2>
              <p className="admin-panel-note">Distribución real según la base de datos del período académico.</p>
            </div>
            <span className="panel-link">{formatCount(gradosConMatriculas.length)} grados</span>
          </div>

          {gradosConMatriculas.length === 0 ? (
            <p className="admin-empty">No hay grados registrados todavía.</p>
          ) : (
            <div className="admin-bar-list">
              {gradosConMatriculas.map((grado) => {
                const porcentaje = Math.round((grado.matriculas / maxMatriculas) * 100);

                return (
                  <div key={grado.id_grado} className="admin-bar-item">
                    <div className="admin-bar-meta">
                      <span>{grado.nombre}</span>
                      <span>
                        {formatCount(grado.matriculas)} matrículas · {formatCount(grado.cursos)} cursos
                      </span>
                    </div>
                    <div className="admin-bar-track" aria-hidden="true">
                      <div className="admin-bar-fill" style={{ width: `${porcentaje}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        <section className="panel admin-panel-stack">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">Estado académico</h2>
              <p className="admin-panel-note">Indicadores generales construidos con datos reales.</p>
            </div>
          </div>

          <div className="admin-mini-stats">
            <article className="admin-mini-stat">
              <span>Estudiantes activos</span>
              <strong>{formatCount(estudiantesActivos.length)}</strong>
            </article>
            <article className="admin-mini-stat">
              <span>Docentes activos</span>
              <strong>{formatCount(profesoresActivos.length)}</strong>
            </article>
            <article className="admin-mini-stat">
              <span>Periodos abiertos</span>
              <strong>{formatCount(periodosAbiertos.length)}</strong>
            </article>
            <article className="admin-mini-stat">
              <span>Cursos vigentes</span>
              <strong>{formatCount(cursosVigentes.length)}</strong>
            </article>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">Docentes activos</h2>
              <p className="admin-panel-note">Listado ordenado por cantidad de cursos asignados.</p>
            </div>
          </div>

          {docentesDestacados.length === 0 ? (
            <p className="admin-empty">No hay docentes activos registrados.</p>
          ) : (
            <div className="admin-list">
              {docentesDestacados.map((docente) => (
                <article key={docente.id} className="admin-list-item">
                  <div className="admin-avatar">{getInitials(docente.nombres, docente.apellidos)}</div>
                  <div className="admin-list-copy">
                    <strong>
                      {docente.nombres} {docente.apellidos}
                    </strong>
                    <span>{docente.correo}</span>
                  </div>
                  <span className="admin-pill active">{formatCount(docente.cursosAsignados)} cursos</span>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>

      <div className="content-grid">
        <section className="panel admin-panel-wide">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">Cursos recientes</h2>
              <p className="admin-panel-note">Cursos ordenados por año y nombre de grado.</p>
            </div>
          </div>

          {cursosRecientes.length === 0 ? (
            <p className="admin-empty">No hay cursos registrados.</p>
          ) : (
            <div className="admin-list">
              {cursosRecientes.map((curso) => (
                <article key={curso.id_curso} className="admin-list-item course-row">
                  <div className="admin-avatar course-avatar">{getCourseLabel(curso, "grado")?.[0] ?? "C"}</div>
                  <div className="admin-list-copy">
                    <strong>{getCourseLabel(curso, "materia")}</strong>
                    <span>
                      {getCourseLabel(curso, "grado")} · {getCourseLabel(curso, "periodo")} · {curso.anio}
                    </span>
                  </div>
                  <span className="admin-pill">ID {formatCount(curso.id_curso)}</span>
                </article>
              ))}
            </div>
          )}
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">Periodos académicos</h2>
              <p className="admin-panel-note">Últimos periodos registrados en el sistema.</p>
            </div>
          </div>

          {periodosRecientes.length === 0 ? (
            <p className="admin-empty">No hay periodos académicos registrados.</p>
          ) : (
            <div className="admin-list">
              {periodosRecientes.map((periodo) => (
                <article key={periodo.id_periodo} className="admin-list-item period-row">
                  <div className={`admin-dot ${periodo.estado === "Abierto" ? "open" : "closed"}`} />
                  <div className="admin-list-copy">
                    <strong>{periodo.nombre}</strong>
                    <span>{periodo.anio}</span>
                  </div>
                  <span className={`admin-pill ${periodo.estado === "Abierto" ? "active" : "inactive"}`}>
                    {periodo.estado}
                  </span>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
