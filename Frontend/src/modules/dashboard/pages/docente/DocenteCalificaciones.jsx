import { useEffect, useState } from "react";
import { useAuth } from "../../../../context/AuthContext";
import SelectorCurso from "../../../calificaciones/components/SelectorCurso";
import EstadoPeriodo from "../../../calificaciones/components/EstadoPeriodo";
import SeccionPanel from "../../../calificaciones/components/SeccionPanel";
import TablaNotas from "../../../calificaciones/components/TablaNotas";
import { listarActividades } from "../../../calificaciones/services/calificacionService";

/**
 * Vista del docente: elegir curso -> elegir sección -> calificar.
 * Las actividades de la sección activa se cargan aquí y se comparten con
 * SeccionPanel (lista) y TablaNotas (columnas) para no repetir la llamada.
 */
export default function DocenteCalificaciones() {
  const { user } = useAuth();

  const [curso, setCurso] = useState(null);
  const [seccionActiva, setSeccionActiva] = useState(null);
  const [actividades, setActividades] = useState([]);
  const [cargandoActividades, setCargandoActividades] = useState(false);
  const [refrescoActividades, setRefrescoActividades] = useState(0);
  const [error, setError] = useState("");

  const periodoAbierto = curso?.periodo?.estado === "Abierto";
  // Sin sección activa no hay columnas que mostrar, aunque el state conserve las últimas.
  const actividadesVisibles = seccionActiva ? actividades : [];

  // Único punto de carga de actividades: se re-dispara al cambiar de sección o cuando
  // ActividadModal crea una nueva (a través de refrescoActividades).
  useEffect(() => {
    if (!seccionActiva) return undefined;

    let vigente = true;

    listarActividades(seccionActiva.id_seccion)
      .then((lista) => {
        if (!vigente) return;
        setActividades(lista);
        setError("");
      })
      .catch((err) => {
        if (!vigente) return;
        setError(err.detail || "No se pudieron cargar las actividades");
        setActividades([]);
      })
      .finally(() => {
        if (vigente) setCargandoActividades(false);
      });

    return () => {
      vigente = false;
    };
  }, [seccionActiva, refrescoActividades]);

  const handleSeleccionarCurso = (nuevoCurso) => {
    setCurso(nuevoCurso);
    setSeccionActiva(null);
    setActividades([]);
  };

  const handleSeleccionarSeccion = (seccion) => {
    setSeccionActiva(seccion);
    setCargandoActividades(Boolean(seccion));
    if (!seccion) setActividades([]);
  };

  return (
    <main className="main">
      <header className="cal-header">
        <h1>Gestión de calificaciones</h1>
        <p>Selecciona un curso, elige una sección de porcentaje y registra las notas de tus estudiantes.</p>
      </header>

      <section className="cal-card">
        <h3 className="cal-section-title">Mis cursos</h3>
        <SelectorCurso
          idDocente={user?.id_usuario}
          cursoSeleccionado={curso}
          onSeleccionar={handleSeleccionarCurso}
        />
      </section>

      {curso && (
        <>
          <EstadoPeriodo periodo={curso.periodo} />

          <section className="cal-card">
            <SeccionPanel
              key={curso.id_curso}
              idCurso={curso.id_curso}
              periodoAbierto={periodoAbierto}
              seccionActiva={seccionActiva}
              onSeleccionarSeccion={handleSeleccionarSeccion}
              actividades={actividadesVisibles}
              cargandoActividades={cargandoActividades}
              onActividadCreada={() => {
                setCargandoActividades(true);
                setRefrescoActividades((valor) => valor + 1);
              }}
            />
          </section>

          <section className="cal-card">
            <div className="cal-card-head">
              <h3 className="cal-section-title">
                Notas{seccionActiva ? ` · ${seccionActiva.nombre_seccion}` : ""}
              </h3>
            </div>

            {error && <p className="cal-error">{error}</p>}

            <TablaNotas
              key={`${curso.id_curso}-${seccionActiva?.id_seccion ?? "sin-seccion"}`}
              seccionActiva={seccionActiva}
              idGrado={curso.id_grado}
              anio={curso.periodo?.anio}
              periodoAbierto={periodoAbierto}
              actividades={actividadesVisibles}
            />
          </section>
        </>
      )}
    </main>
  );
}
