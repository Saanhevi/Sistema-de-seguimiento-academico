// eslint-disable-next-line no-unused-vars
import React, { useEffect, useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import Greeting from "../../components/Greeting";
import { listarAlertas } from "../../../alertas/services/alertaService";
import AlertasPanel from "../../../alertas/components/AlertasPanel";
import { listarCursosDocente, listarEstudiantesPorCurso } from "../../../cursos/services/cursoService";
import { obtenerPromedioGrupal } from "../../../calificaciones/services/calificacionService";
import { formatearNota } from "../../../calificaciones/utils/notas";

// PortalDocente: componente funcional para docentes que muestra
// métricas clave, secciones activas y alertas de riesgo usando
// datos reales de cursos y alertas desde los endpoints del backend.
export default function PortalDocente() {
  const location = useLocation();
  const isHomeView = location.pathname === '/dashboard/docente';
  const [alertas, setAlertas] = useState([]);
  const [cursos, setCursos] = useState([]);
  const [loadingAlertas, setLoadingAlertas] = useState(false);
  const [loadingCursos, setLoadingCursos] = useState(false);
  const [errorAlertas, setErrorAlertas] = useState(null);
  const [errorCursos, setErrorCursos] = useState(null);

  useEffect(() => {
    if (!isHomeView) return;

    const cargarAlertas = async () => {
      setLoadingAlertas(true);
      setErrorAlertas(null);
      try {
        const res = await listarAlertas();
        setAlertas(res || []);
      } catch (err) {
        setErrorAlertas('No se pudieron cargar las alertas');
        setAlertas([]);
      } finally {
        setLoadingAlertas(false);
      }
    };

    const cargarCursos = async () => {
      setLoadingCursos(true);
      setErrorCursos(null);
      try {
        const cursosRes = await listarCursosDocente();
        const cursosConTotales = await Promise.all(
          (cursosRes || []).map(async (curso) => {
            // Las dos consultas de un curso son independientes y cada una absorbe su
            // propio error, para que un curso sin notas no vacíe la lista entera.
            const [total, promedioGrupal] = await Promise.all([
              listarEstudiantesPorCurso(curso.id_curso)
                .then((estudiantes) =>
                  (estudiantes.estudiantes_disponibles?.length || 0) + (estudiantes.estudiantes_asociados?.length || 0)
                )
                .catch(() => 0),
              // HU9: promedio grupal real de la materia y periodo del curso.
              obtenerPromedioGrupal(curso.id_materia, curso.id_periodo)
                .then((data) => data.promedio_grupal)
                .catch(() => null)
            ]);

            return { ...curso, total_estudiantes: total, promedio_grupal: promedioGrupal };
          })
        );
        setCursos(cursosConTotales);
      } catch (err) {
        setErrorCursos('No se pudieron cargar los cursos');
        setCursos([]);
      } finally {
        setLoadingCursos(false);
      }
    };

    cargarAlertas();
    cargarCursos();
  }, [isHomeView]);

  const cursosIds = new Set(cursos.map((curso) => curso.id_curso));
  const alertasVisibles = alertas.filter((alerta) => alerta.id_curso && cursosIds.has(alerta.id_curso));

  const cursosConRiesgo = alertasVisibles.reduce((set, alerta) => {
    set.add(alerta.id_curso);
    return set;
  }, new Set());

  const estudiantesEnRiesgo = new Set(
    alertasVisibles
      .filter((alerta) => alerta.nivel === 'Medio' || alerta.nivel === 'Alto')
      .map((alerta) => alerta.id_estudiante)
  ).size;

  const cursosMostrados = cursos.map((curso) => {
    const riesgo = cursosConRiesgo.has(curso.id_curso) ? 'en riesgo' : 'estable';
    const estudiantesRiesgoCount = new Set(
      alertasVisibles
        .filter((alerta) => alerta.id_curso === curso.id_curso && (alerta.nivel === 'Medio' || alerta.nivel === 'Alto'))
        .map((alerta) => alerta.id_estudiante)
    ).size;
    const progreso = curso.total_estudiantes ? Math.round((estudiantesRiesgoCount / curso.total_estudiantes) * 100) : 0;
    return {
      ...curso,
      riesgo,
      estudiantesRiesgoCount,
      progreso,
    };

  });

  if (!isHomeView) {
    return <Outlet />;
  }

  return (
    <>
      <main className="main">
        {/* Contenido principal dividido en tres paneles: secciones*/}
        <div className="content-grid">
          <div className="panel">
            <div className="panel-header">
              <span className="panel-title">Mis secciones</span>
              <Link to="/dashboard/docente/calificaciones" className="panel-link">Ver notas →</Link>
            </div>

            {loadingCursos ? (
              <div className="pending-item normal">Cargando cursos...</div>
            ) : errorCursos ? (
              <div className="pending-item normal">{errorCursos}</div>
            ) : cursosMostrados.length === 0 ? (
              <div className="pending-item normal">No hay cursos disponibles</div>
            ) : (
              cursosMostrados.map((curso) => (
                <div key={curso.id_curso} className="section-row">
                  <div className="section-badge">{curso.grado}</div>
                  <div className="section-info">
                    <div className="section-title">{curso.materia}</div>
                    <div className="label">{curso.total_estudiantes ?? 0} estudiantes</div>
                    <div className={`risk-tag ${curso.riesgo === 'en riesgo' ? 'mid' : 'low'}`}>{curso.estudiantesRiesgoCount}</div>
                    <div className="progress-bar" style={{ marginTop: '6px' }}><div className="fill" style={{ width: `${curso.progreso}%` }}></div></div>
                  </div>
                  <div className="section-avg" title="Promedio grupal de la materia">
                    {formatearNota(curso.promedio_grupal)}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Panel de distribución de notas - pendiente */}    
          

          

          <div className="panel">
            <div className="panel-header">
              <span className="panel-title">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ verticalAlign: '-2px', marginRight: '6px' }}>
                  <rect x="9" y="2" width="6" height="4" rx="1"/><path d="M5 4h-2a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2"/>
                  <line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="13" y2="16"/>
                </svg>
                Alertas
              </span>
            </div>

            <AlertasPanel
              alertas={alertasVisibles}
              loading={loadingAlertas}
              error={errorAlertas}
              emptyMessage="No hay alertas"
            />
          </div>
        </div>

      </main>
    </>
  );
}