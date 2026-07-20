import { useEffect, useState } from "react";
import { crearPeriodo, listarPeriodos } from "../services/cursoService";

export default function PeriodoPanel() {
  const [nombre, setNombre] = useState("");
  const [anio, setAnio] = useState(2026);
  const [estado, setEstado] = useState("Abierto");
  const [periodos, setPeriodos] = useState([]);
  const [loading, setLoading] = useState(false);

  const cargarPeriodos = async () => {
    setLoading(true);
    try {
      const data = await listarPeriodos();
      setPeriodos(data);
    } catch (error) {
      alert(error.detail || error.message || "No se pudieron cargar los periodos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarPeriodos();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await crearPeriodo(nombre, Number(anio), estado);
      setNombre("");
      setAnio(2026);
      setEstado("Abierto");
      await cargarPeriodos();
    } catch (error) {
      alert(error.detail || error.message || "No se pudo crear el periodo");
    }
  };

  return (
    <section className="panel">
      <div className="panel-header">
        <h3 className="panel-title">Gestión de periodos</h3>
      </div>

      <form className="curso-form" onSubmit={handleSubmit}>
        <label>
          Nombre del periodo
          <input
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            placeholder="Ej. Primer Periodo"
            required
          />
        </label>
        <label>
          Año
          <input
            type="number"
            value={anio}
            onChange={(e) => setAnio(e.target.value)}
            required
          />
        </label>
        <label>
          Estado
          <select value={estado} onChange={(e) => setEstado(e.target.value)}>
            <option value="Abierto">Abierto</option>
            <option value="Cerrado">Cerrado</option>
          </select>
        </label>
        <button type="submit">Crear periodo</button>
      </form>

      <div className="curso-lista">
        {loading ? (
          <p>Cargando periodos...</p>
        ) : (
          <table className="curso-tabla">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Año</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {periodos.map((periodo) => (
                <tr key={periodo.id_periodo}>
                  <td>{periodo.id_periodo}</td>
                  <td>{periodo.nombre}</td>
                  <td>{periodo.anio}</td>
                  <td>{periodo.estado}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
