import { useState } from "react";
import { crearActividad } from "../services/calificacionService";

/**
 * Modal para crear una actividad evaluativa.
 * El backend solo acepta { nombre, fecha, id_seccion }: no hay tipo ni porcentaje
 * (el peso vive en la sección de porcentaje, no en la actividad).
 */
export default function ActividadModal({ seccion, onCerrar, onCreada }) {
  const [nombre, setNombre] = useState("");
  const [fecha, setFecha] = useState(() => new Date().toISOString().slice(0, 10));
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setGuardando(true);
    try {
      await crearActividad({ nombre: nombre.trim(), fecha, id_seccion: seccion.id_seccion });
      onCreada();
      onCerrar();
    } catch (err) {
      setError(err.detail || "No se pudo crear la actividad");
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div className="cal-modal-overlay" onClick={onCerrar}>
      <div className="cal-modal" onClick={(e) => e.stopPropagation()}>
        <div className="cal-modal-header">
          <span className="cal-modal-title">Nueva actividad</span>
          <button type="button" className="cal-modal-close" onClick={onCerrar} aria-label="Cerrar">
            ×
          </button>
        </div>

        <p className="cal-hint">Sección: {seccion.nombre_seccion}</p>

        <form onSubmit={handleSubmit}>
          <div className="cal-field">
            <label htmlFor="actividad-nombre">Nombre</label>
            <input
              id="actividad-nombre"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              maxLength={50}
              placeholder="Examen bimestral"
              required
            />
          </div>

          <div className="cal-field">
            <label htmlFor="actividad-fecha">Fecha</label>
            <input
              id="actividad-fecha"
              type="date"
              value={fecha}
              onChange={(e) => setFecha(e.target.value)}
              required
            />
          </div>

          {error && <p className="cal-error">{error}</p>}

          <div className="cal-modal-actions">
            <button type="button" className="cal-btn secondary" onClick={onCerrar}>
              Cancelar
            </button>
            <button type="submit" className="cal-btn primary" disabled={guardando || !nombre.trim()}>
              {guardando ? "Guardando..." : "Agregar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
