// eslint-disable-next-line no-unused-vars
import React, { useEffect, useState } from 'react';
import { Outlet, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../../../context/AuthContext';
import { listarMisCursosEstudiante } from '../../../calificaciones/services/calificacionService';
import { etiquetaCurso, nombreDocente } from '../../../calificaciones/utils/cursos';

// PortalEstudiantil: inicio del estudiante.
//
// RN-10b: esta pantalla no inventa datos. Antes mostraba un saludo fijo
// ("Bienvenida, Sofía"), un promedio de 8.7 en escala 0-10 (el sistema es 0-5) y
// entregas/notas de materias y profesores que no existen. Ahora solo muestra lo
// que devuelve el backend, y si no hay nada lo dice.
export default function PortalEstudiantil() {
  const location = useLocation();
  const { user } = useAuth();
  const isHomeView = location.pathname === '/dashboard/estudiante';

  const [cursos, setCursos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isHomeView || !user?.id_usuario) return undefined;

    let vigente = true;

    listarMisCursosEstudiante()
      .then((lista) => {
        if (!vigente) return;
        setCursos(lista);
        setError('');
      })
      .catch((err) => {
        if (vigente) setError(err.detail || 'No se pudieron cargar tus cursos');
      })
      .finally(() => {
        if (vigente) setCargando(false);
      });

    return () => {
      vigente = false;
    };
  }, [isHomeView, user?.id_usuario]);

  if (!isHomeView) {
    return <Outlet />;
  }

  const nombre = [user?.nombres, user?.apellidos].filter(Boolean).join(' ');

  return (
    <main className="main">
      <div className="hero">
        <p className="hero-eyebrow">Seguimiento académico</p>
        <h2 className="hero-name">{nombre ? `Hola, ${nombre}` : 'Hola'}</h2>
        <p className="hero-sub">Consulta tus calificaciones y tu asistencia.</p>
      </div>

      <section className="cal-card">
        <div className="cal-card-head">
          <h3 className="cal-section-title">Mis cursos</h3>
          <Link className="cal-btn secondary small" to="/dashboard/estudiante/calificaciones">
            Ver mis calificaciones
          </Link>
        </div>

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

        {cursos.map((curso) => {
          const docente = nombreDocente(curso);
          return (
            <div className="cal-seccion" key={curso.id_curso}>
              <div className="cal-seccion-header">
                <span className="cal-seccion-title-group">
                  <span className="cal-seccion-name">{etiquetaCurso(curso)}</span>
                  {docente && <span className="cal-seccion-docente">{docente}</span>}
                </span>
                <span className="cal-seccion-pct">{curso.periodo?.estado}</span>
              </div>
            </div>
          );
        })}
      </section>
    </main>
  );
}
