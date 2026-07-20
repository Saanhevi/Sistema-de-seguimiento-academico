export default function ProfesorCard({ profesor, onEdit, onToggleStatus }) {
  const initials = `${profesor.nombres?.[0] || ""}${profesor.apellidos?.[0] || ""}`.toUpperCase();

  return (
    <article className="profesor-card">
      <div className="profesor-card__header">
        <div className="avatar">{initials || "P"}</div>
        <div>
          <h3>{`${profesor.nombres} ${profesor.apellidos}`}</h3>
          <p>{profesor.correo}</p>
        </div>
      </div>

      <div className="profesor-card__meta">
        <span className={`status-pill ${profesor.estado ? "active" : "inactive"}`}>
          {profesor.estado ? "Activo" : "Inactivo"}
        </span>
        <span className="meta-text">Rol: Docente</span>
      </div>

      <div className="profesor-card__actions">
        <button type="button" className="ghost-btn" onClick={() => onEdit(profesor)}>
          Editar
        </button>
        <button
          type="button"
          className={`status-btn ${profesor.estado ? "desactivar-btn" : "activar-btn"}`}
          onClick={() => onToggleStatus(profesor)}
        >
          {profesor.estado ? "Desactivar" : "Activar"}
        </button>
      </div>
    </article>
  );
}
