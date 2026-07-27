import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../../context/AuthContext';
import { obtenerPerfilEstudiante } from '../../../auth/services/authService';

export default function EstudiantePerfil() {
  const { user } = useAuth();
  const [perfil, setPerfil] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let activo = true;

    obtenerPerfilEstudiante()
      .then((data) => {
        if (!activo) return;
        setPerfil(data);
        setError('');
      })
      .catch((err) => {
        if (!activo) return;
        setError(err.detail || 'No se pudo cargar tu perfil');
      })
      .finally(() => {
        if (activo) setCargando(false);
      });

    return () => {
      activo = false;
    };
  }, []);

  const nombreCompleto = [perfil?.nombres || user?.nombres, perfil?.apellidos || user?.apellidos].filter(Boolean).join(' ');
  const gradoActual = perfil?.grado_actual || 'Sin matrícula registrada';

  return (
    <main className="main">
      <div className="hero">
        <p className="hero-eyebrow">Perfil del estudiante</p>
        <h2 className="hero-name">{nombreCompleto || 'Estudiante'}</h2>
        <p className="hero-sub">Consulta tus datos personales y administra tu cuenta desde el dashboard.</p>
        <Link className="cal-btn secondary small" to="/dashboard/estudiante/cambiar-password">
          Cambiar contraseña
        </Link>
      </div>

      <section className="profile-summary">
        <div className="profile-summary-main">
          <span className="profile-kicker">Identidad académica</span>
          <h3 className="profile-title">Tus datos registrados</h3>
          <p className="profile-text">
            Esta información se obtiene desde tu sesión activa y tu matrícula más reciente.
          </p>
        </div>
        <div className="profile-summary-badge">
          <span className="profile-badge-label">Grado actual</span>
          <strong className="profile-badge-value">{gradoActual}</strong>
        </div>
      </section>

      <section className="profile-grid">
        <article className="profile-card profile-card-main">
          <h3 className="cal-section-title">Datos personales</h3>
          {cargando && <p className="cal-hint">Cargando tu información...</p>}
          {error && <p className="cal-error">{error}</p>}
          {!cargando && !error && (
            <div className="profile-details">
              <div className="profile-field">
                <span className="profile-field-label">Nombres</span>
                <strong className="profile-field-value">{perfil?.nombres || user?.nombres || 'N/D'}</strong>
              </div>
              <div className="profile-field">
                <span className="profile-field-label">Apellidos</span>
                <strong className="profile-field-value">{perfil?.apellidos || user?.apellidos || 'N/D'}</strong>
              </div>
              <div className="profile-field">
                <span className="profile-field-label">Correo</span>
                <strong className="profile-field-value">{perfil?.correo || 'N/D'}</strong>
              </div>
              <div className="profile-field">
                <span className="profile-field-label">Grado actual</span>
                <strong className="profile-field-value">{gradoActual}</strong>
              </div>
            </div>
          )}
        </article>
      </section>

    </main>
  );
}
