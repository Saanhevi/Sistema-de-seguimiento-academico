import { useEffect, useMemo, useState } from "react";
import { crearMatricula, listarEstudiantesDeGrado, listarGrados, listarMatriculas } from "../services/cursoService";

export default function MatriculaPanel() {
  const [grados, setGrados] = useState([]);
  const [matriculas, setMatriculas] = useState([]);
  const [gradoSeleccionado, setGradoSeleccionado] = useState("");
  const [anio, setAnio] = useState(2026);
  const [form, setForm] = useState({ id_estudiante: "", id_grado: "", anio: 2026 });
  const [estudiantes, setEstudiantes] = useState([]);
  const [loading, setLoading] = useState(false);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      const [gradosData, matriculasData] = await Promise.all([
        listarGrados(),
        listarMatriculas(gradoSeleccionado || undefined, anio || undefined)
      ]);
      setGrados(gradosData);
      setMatriculas(matriculasData);
      if (gradoSeleccionado) {
        const estudiantesData = await listarEstudiantesDeGrado(gradoSeleccionado, anio);
        setEstudiantes(estudiantesData);
      } else {
        setEstudiantes([]);
      }
    } catch (error) {
      alert(error.detail || error.message || "No se pudieron cargar las matrículas");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  useEffect(() => {
    if (gradoSeleccionado) {
      listarMatriculas(gradoSeleccionado, anio || undefined).then(setMatriculas).catch(() => setMatriculas([]));
      listarEstudiantesDeGrado(gradoSeleccionado, anio).then(setEstudiantes).catch(() => setEstudiantes([]));
    } else {
      setMatriculas([]);
      setEstudiantes([]);
    }
  }, [gradoSeleccionado, anio]);

  const matriculasFiltradas = useMemo(() => {
    return matriculas.filter((matricula) => {
      const coincideGrado = !gradoSeleccionado || String(matricula.id_grado) === String(gradoSeleccionado);
      const coincideAnio = !anio || Number(matricula.anio) === Number(anio);
      return coincideGrado && coincideAnio;
    });
  }, [matriculas, gradoSeleccionado, anio]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await crearMatricula({
        id_estudiante: Number(form.id_estudiante),
        id_grado: Number(form.id_grado || gradoSeleccionado),
        anio: Number(form.anio || anio)
      });
      setForm({ id_estudiante: "", id_grado: "", anio: 2026 });
      await cargarDatos();
    } catch (error) {
      alert(error.detail || error.message || "No se pudo crear la matrícula");
    }
  };

  return (
    <section className="panel">
      <div className="panel-header">
        <h3 className="panel-title">Gestión de matrículas</h3>
      </div>

      <div className="curso-layout">
        <div className="curso-col">
          <h4 className="curso-subtitle">Filtro</h4>
          <label>
            Grado
            <select value={gradoSeleccionado} onChange={(e) => setGradoSeleccionado(e.target.value)}>
              <option value="">Todos</option>
              {grados.map((grado) => (
                <option key={grado.id_grado} value={grado.id_grado}>
                  {grado.nombre}
                </option>
              ))}
            </select>
          </label>
          <label>
            Año
            <input type="number" value={anio} onChange={(e) => setAnio(e.target.value)} />
          </label>

          <div className="curso-lista">
            {loading ? (
              <p>Cargando matrículas...</p>
            ) : (
              <>
                <p className="curso-helper">Estudiantes matriculados</p>
                {estudiantes.length === 0 ? (
                  <p className="curso-empty">No hay estudiantes matriculados para este filtro.</p>
                ) : (
                  <div className="curso-chip-list">
                    {estudiantes.map((estudiante) => (
                      <span key={estudiante.id_estudiante} className="curso-chip">
                        {estudiante.nombre} {estudiante.apellido}
                      </span>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        <div className="curso-col">
          <h4 className="curso-subtitle">Crear matrícula</h4>
          <form className="curso-form" onSubmit={handleSubmit}>
            <label>
              ID del estudiante
              <input
                value={form.id_estudiante}
                onChange={(e) => setForm({ ...form, id_estudiante: e.target.value })}
                placeholder="ID del estudiante (temporal)"
                required
              />
              <span className="curso-note">TODO: reemplazar por select cuando exista endpoint de estudiantes.</span>
            </label>
            <label>
              Grado
              <select value={form.id_grado || gradoSeleccionado} onChange={(e) => setForm({ ...form, id_grado: e.target.value })}>
                <option value="">Seleccione un grado</option>
                {grados.map((grado) => (
                  <option key={grado.id_grado} value={grado.id_grado}>
                    {grado.nombre}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Año
              <input
                type="number"
                value={form.anio || anio}
                onChange={(e) => setForm({ ...form, anio: e.target.value })}
                required
              />
            </label>
            <button type="submit">Crear matrícula</button>
          </form>

          <div className="curso-lista">
            <p className="curso-helper">Matrículas recientes</p>
            {matriculasFiltradas.length === 0 ? (
              <p className="curso-empty">No hay matrículas para este filtro.</p>
            ) : (
              <ul className="curso-chip-list">
                {matriculasFiltradas.map((matricula) => (
                  <li key={matricula.id_matricula} className="curso-chip">
                    Estudiante #{matricula.id_estudiante} · Grado #{matricula.id_grado} · Año {matricula.anio}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
