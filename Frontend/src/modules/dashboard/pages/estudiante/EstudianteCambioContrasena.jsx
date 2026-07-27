import { Link } from 'react-router-dom';
import ChangePasswordForm from '../../../auth/components/changePasswordForm';

export default function EstudianteCambioContrasena() {
  return (
    <main className="main">
      <div className="hero">
        <p className="hero-eyebrow">Cuenta del estudiante</p>
        <h2 className="hero-name">Cambiar contraseña</h2>
        <p className="hero-sub">Actualiza tu clave sin salir de tu sesión del dashboard.</p>
        <Link className="cal-btn secondary small" to="/dashboard/estudiante/perfil">
          Volver al perfil
        </Link>
      </div>

      <section className="password-shell">
        <div className="password-card">
          <h3 className="cal-section-title">Formulario de cambio</h3>
          <p className="cal-hint">
            Usa tu contraseña actual para autorizar la actualización de la nueva clave.
          </p>
          <ChangePasswordForm />
        </div>
      </section>
    </main>
  );
}