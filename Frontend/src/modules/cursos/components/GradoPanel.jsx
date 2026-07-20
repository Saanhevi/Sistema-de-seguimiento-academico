import { useEffect, useState } from "react";
import { crearGrado, listarGrados } from "../services/cursoService";

export default function GradoPanel() {
  const [nombre, setNombre] = useState("");
  const [grados, setGrados] = useState([]);
  const [loading, setLoading] = useState(false);

  const cargarGrados = async () => {
    setLoading(true);
    try {
      const data = await listarGrados();
      setGrados(data);
    } catch (error) {
      alert(error.detail || error.message || "No se pudieron cargar los grados");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarGrados();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await crearGrado(nombre);
      setNombre("");
      await cargarGrados();
    } catch (error) {
      alert(error.detail || error.message || "No se pudo crear el grado");
    }
  };

  return (
    <section className="panel">
      <div className="panel-header">
        <h3 className="panel-title">Gestión de grados</h3>
      </div>

      <form className="curso-form" onSubmit={handleSubmit}>
        <label>
          Nombre del grado
          <input
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            placeholder="Ej. 10°"
            required
          />
        </label>
        <button type="submit">Crear grado</button>
      </form>

      <div className="curso-lista">
        {loading ? (
          <p>Cargando grados...</p>
        ) : (
          <table className="curso-tabla">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre</th>
              </tr>
            </thead>
            <tbody>
              {grados.map((grado) => (
                <tr key={grado.id_grado}>
                  <td>{grado.id_grado}</td>
                  <td>{grado.nombre}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
