import { useEffect, useMemo, useState } from "react";
import { listarEstudiantes, retirarEstudiante } from "../../../estudiantes/services/estudianteService";

const FILTERS = [
  { key: "todos", label: "Todos" },
  { key: "activos", label: "Activos" },
  { key: "retirados", label: "Retirados" }
];

export default function AdminEstudiantes() {
  const [estudiantes, setEstudiantes] = useState([]);
  const [filtro, setFiltro] = useState("todos");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargar = async () => {
      try {
        setLoading(true);
        setError("");
        const data = await listarEstudiantes(true);
        setEstudiantes(data);
      } catch (err) {
        setError(err?.response?.data?.detail || "No se pudieron cargar los estudiantes");
      } finally {
        setLoading(false);
      }
    };

    cargar();
  }, []);

  const estudiantesFiltrados = useMemo(() => {
    if (filtro === "activos") return estudiantes.filter((item) => item.estado);
    if (filtro === "retirados") return estudiantes.filter((item) => !item.estado);
    return estudiantes;
  }, [estudiantes, filtro]);

  const resumen = useMemo(() => {
    const activos = estudiantes.filter((item) => item.estado).length;
    const retirados = estudiantes.length - activos;
    return {
      total: estudiantes.length,
      activos,
      retirados
    };
  }, [estudiantes]);

  const handleRetirar = async (estudiante) => {
    if (!estudiante.estado) return;
    const confirmar = window.confirm(`¿Confirmas retirar a ${estudiante.nombres} ${estudiante.apellidos}?`);
    if (!confirmar) return;

    try {
      const actualizado = await retirarEstudiante(estudiante.id);
      setEstudiantes((prev) => prev.map((item) => (item.id === estudiante.id ? actualizado : item)));
    } catch (err) {
      alert(err?.response?.data?.detail || "No se pudo retirar el estudiante");
    }
  };

  return (
    <div className="estudiantes-shell">
      <section className="panel">
        <div className="panel-header">
          <div>
            <h2 className="panel-title">Estudiantes</h2>
            <p className="modal-caption">Gestiona el retiro lógico de estudiantes para mantener la base actualizada.</p>
          </div>
        </div>

        <div className="estudiantes-summary">
          <div className="summary-card">
            <h3>Total</h3>
            <strong>{resumen.total}</strong>
          </div>
          <div className="summary-card active-card">
            <h3>Activos</h3>
            <strong>{resumen.activos}</strong>
          </div>
          <div className="summary-card inactive-card">
            <h3>Retirados</h3>
            <strong>{resumen.retirados}</strong>
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="estudiantes-toolbar">
          <div className="filter-group">
            {FILTERS.map((filter) => (
              <button
                key={filter.key}
                type="button"
                className={`filter-btn ${filtro === filter.key ? "active" : ""}`}
                onClick={() => setFiltro(filter.key)}
              >
                {filter.label}
              </button>
            ))}
          </div>
          <p className="meta-text">{loading ? "Cargando estudiantes..." : `${estudiantesFiltrados.length} registros visibles`}</p>
        </div>

        {error ? <p className="estudiantes-error">{error}</p> : null}

        <div className="estudiantes-table-wrapper">
          <table className="estudiantes-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Correo</th>
                <th>Estado</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              {estudiantesFiltrados.map((estudiante) => (
                <tr key={estudiante.id}>
                  <td>{estudiante.nombres} {estudiante.apellidos}</td>
                  <td>{estudiante.correo}</td>
                  <td>
                    <span className={`status-pill ${estudiante.estado ? "active" : "inactive"}`}>
                      {estudiante.estado ? "Activo" : "Retirado"}
                    </span>
                  </td>
                  <td>
                    <button
                      type="button"
                      className="secondary-btn"
                      onClick={() => handleRetirar(estudiante)}
                      disabled={!estudiante.estado}
                    >
                      Retirar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
