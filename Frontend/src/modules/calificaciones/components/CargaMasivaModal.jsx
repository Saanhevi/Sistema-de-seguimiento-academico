import { useState } from "react";
import { cargaMasiva } from "../services/calificacionService";

/**
 * Carga las notas de toda la clase para una actividad en una sola llamada.
 * La lista de estudiantes y las notas actuales llegan por prop desde TablaNotas:
 * no se vuelve a consultar al backend para abrir el modal.
 */
export default function CargaMasivaModal({ actividad, estudiantes, notas, onCerrar, onGuardadas }) {
  const [valores, setValores] = useState(() => {
    const inicial = {};
    estudiantes.forEach((estudiante) => {
      const nota = notas[`${actividad.id_actividad}-${estudiante.id_estudiante}`];
      inicial[estudiante.id_estudiante] = nota ? String(nota.calificacion) : "";
    });
    return inicial;
  });
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [exito, setExito] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setExito("");

    // Los campos vacíos se omiten: solo se envían las notas realmente escritas.
    const payload = estudiantes
      .filter((estudiante) => String(valores[estudiante.id_estudiante] ?? "").trim() !== "")
      .map((estudiante) => ({
        id_estudiante: estudiante.id_estudiante,
        calificacion: Number(valores[estudiante.id_estudiante])
      }));

    if (payload.length === 0) {
      setError("Escribe al menos una nota antes de guardar");
      return;
    }

    setGuardando(true);
    try {
      const guardadas = await cargaMasiva({ id_actividad: actividad.id_actividad, notas: payload });
      onGuardadas(guardadas);
      setExito(`Se guardaron ${guardadas.length} notas.`);
    } catch (err) {
      setError(err.detail || "No se pudo completar la carga masiva");
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div className="cal-modal-overlay" onClick={onCerrar}>
      <div className="cal-modal" onClick={(e) => e.stopPropagation()}>
        <div className="cal-modal-header">
          <span className="cal-modal-title">Carga masiva · {actividad.nombre}</span>
          <button type="button" className="cal-modal-close" onClick={onCerrar} aria-label="Cerrar">
            ×
          </button>
        </div>

        <p className="cal-hint">Escala 0.00 – 5.00. Los campos vacíos no se envían.</p>

        <form onSubmit={handleSubmit}>
          <div className="cal-masiva-list">
            {estudiantes.map((estudiante) => (
              <div className="cal-masiva-row" key={estudiante.id_estudiante}>
                <span>
                  {estudiante.nombre} {estudiante.apellido}
                </span>
                <input
                  type="number"
                  min="0"
                  max="5"
                  step="0.01"
                  value={valores[estudiante.id_estudiante] ?? ""}
                  onChange={(e) =>
                    setValores({ ...valores, [estudiante.id_estudiante]: e.target.value })
                  }
                />
              </div>
            ))}
          </div>

          {error && <p className="cal-error">{error}</p>}
          {exito && <p className="cal-success">{exito}</p>}

          <div className="cal-modal-actions">
            <button type="button" className="cal-btn secondary" onClick={onCerrar}>
              Cerrar
            </button>
            <button type="submit" className="cal-btn primary" disabled={guardando}>
              {guardando ? "Guardando..." : "Guardar notas"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
