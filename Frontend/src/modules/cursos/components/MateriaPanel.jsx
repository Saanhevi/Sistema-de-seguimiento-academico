import { useEffect, useState } from "react";
import { crearMateria, listarMaterias } from "../services/cursoService";

export default function MateriaPanel() {
  const [nombre, setNombre] = useState("");
  const [materias, setMaterias] = useState([]);
  const [loading, setLoading] = useState(false);

  const cargarMaterias = async () => {
    setLoading(true);
    try {
      const data = await listarMaterias();
      setMaterias(data);
    } catch (error) {
      alert(error.detail || error.message || "No se pudieron cargar las materias");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarMaterias();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await crearMateria(nombre);
      setNombre("");
      await cargarMaterias();
    } catch (error) {
      alert(error.detail || error.message || "No se pudo crear la materia");
    }
  };

  return (
    <section className="panel">
      <div className="panel-header">
        <h3 className="panel-title">Gestión de materias</h3>
      </div>

      <form className="curso-form" onSubmit={handleSubmit}>
        <label>
          Nombre de la materia
          <input
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            placeholder="Ej. Historia"
            required
          />
        </label>
        <button type="submit">Crear materia</button>
      </form>

      <div className="curso-lista">
        {loading ? (
          <p>Cargando materias...</p>
        ) : (
          <table className="curso-tabla">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre</th>
              </tr>
            </thead>
            <tbody>
              {materias.map((materia) => (
                <tr key={materia.id_materia}>
                  <td>{materia.id_materia}</td>
                  <td>{materia.nombre}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
