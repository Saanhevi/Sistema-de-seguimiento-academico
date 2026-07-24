import { useEffect, useState } from "react";
import { useAuth } from "../../../../context/AuthContext";
import SeccionPanel from "../../../calificaciones/components/SeccionPanel";
import { etiquetaCurso } from "../../../calificaciones/utils/cursos";
import {
  listarActividades,
  listarCursosDeGrado,
  listarMisMatriculas,
  listarNotas
} from "../../../calificaciones/services/calificacionService";

/**
 * Acordeón de un curso del estudiante. Solo consulta secciones, actividades y notas
 * cuando el estudiante lo expande, para no disparar todas las llamadas de golpe.
 */
function CursoAcordeon({ curso }) {
  const [abierto, setAbierto] = useState(false);
  const [seccionActiva, setSeccionActiva] = useState(null);
  const [actividades, setActividades] = useState([]);
  const [notaPorActividad, setNotaPorActividad] = useState({});
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!seccionActiva) return undefined;

    let vigente = true;

    listarActividades(seccionActiva.id_seccion)
      .then(async (lista) => {
        if (!vigente) return;
        setActividades(lista);
        // El backend ya filtra la nota del estudiante autenticado (RN-04).
        const respuestas = await Promise.all(lista.map((act) => listarNotas(act.id_actividad)));
        if (!vigente) return;
        const mapa = {};
        respuestas.flat().forEach((nota) => {
          mapa[nota.id_actividad] = nota.calificacion;
        });
        setNotaPorActividad(mapa);
        setError("");
      })
      .catch((err) => {
        if (vigente) setError(err.detail || "No se pudieron cargar tus notas");
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });

    return () => {
      vigente = false;
    };
  }, [seccionActiva]);

  const handleSeleccionarSeccion = (seccion) => {
    setSeccionActiva(seccion);
    setCargando(Boolean(seccion));
    setActividades([]);
    setNotaPorActividad({});
  };

  return (
    <div className="cal-seccion">
      <div
        className={`cal-seccion-header ${abierto ? "selected" : ""}`}
        role="button"
        tabIndex={0}
        onClick={() => setAbierto((valor) => !valor)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            setAbierto((valor) => !valor);
          }
        }}
      >
        <span className="cal-seccion-name">{etiquetaCurso(curso)}</span>
        <span className="cal-seccion-pct">{abierto ? "▲" : "▼"}</span>
      </div>

      {abierto && (
        <div className="cal-seccion-body">
          {error && <p className="cal-error">{error}</p>}
          <SeccionPanel
            idCurso={curso.id_curso}
            readOnly
            seccionActiva={seccionActiva}
            onSeleccionarSeccion={handleSeleccionarSeccion}
            actividades={actividades}
            cargandoActividades={cargando}
            notaPorActividad={notaPorActividad}
          />
        </div>
      )}
    </div>
  );
}

/** Vista de solo lectura: el estudiante consulta sus propias calificaciones. */
export default function EstudianteCalificaciones() {
  const { user } = useAuth();

  const [cursos, setCursos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user?.id_usuario) return undefined;

    let vigente = true;

    listarMisMatriculas(user.id_usuario)
      .then(async (matriculas) => {
        if (!vigente) return;
        // Un estudiante puede tener matrícula en varios años; se juntan sus cursos.
        const porGrado = await Promise.all(
          matriculas.map((matricula) => listarCursosDeGrado(matricula.id_grado))
        );
        if (!vigente) return;
        const unicos = new Map();
        porGrado.flat().forEach((curso) => unicos.set(curso.id_curso, curso));
        setCursos([...unicos.values()]);
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
  }, [user?.id_usuario]);

  return (
    <main className="main">
      <header className="cal-header">
        <h1>Mis calificaciones</h1>
        <p>Consulta tus notas por curso, sección y actividad.</p>
      </header>

      <section className="cal-card">
        {!user?.id_usuario && (
          <p className="cal-error">
            No se encontró tu identificador de usuario. Cierra sesión y vuelve a iniciarla.
          </p>
        )}
        {cargando && user?.id_usuario && <p className="cal-hint">Cargando tus cursos...</p>}
        {error && <p className="cal-error">{error}</p>}

        {!cargando && !error && cursos.length === 0 && user?.id_usuario && (
          <p className="cal-empty">Todavía no tienes cursos matriculados.</p>
        )}

        {cursos.map((curso) => (
          <CursoAcordeon key={curso.id_curso} curso={curso} />
        ))}
      </section>
    </main>
  );
}
