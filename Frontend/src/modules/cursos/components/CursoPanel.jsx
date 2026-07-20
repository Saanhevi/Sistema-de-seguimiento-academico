import { useEffect, useMemo, useState } from "react";
import { crearCurso, listarCursos, listarGrados, listarMaterias, listarPeriodos } from "../services/cursoService";

export default function CursoPanel() {
  const [grados, setGrados] = useState([]);
  const [materias, setMaterias] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [cursos, setCursos] = useState([]);
  const [gradoSeleccionado, setGradoSeleccionado] = useState("");
  const [form, setForm] = useState({
    id_docente: "",
    id_grado: "",
    id_materia: "",
    id_periodo: ""
  });
  const [loading, setLoading] = useState(false);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      const [gradosData, materiasData, periodosData, cursosData] = await Promise.all([
        listarGrados(),
        listarMaterias(),
        listarPeriodos(),
        listarCursos(gradoSeleccionado || undefined)
      ]);
      setGrados(gradosData);
      setMaterias(materiasData);
      setPeriodos(periodosData);
      setCursos(cursosData);
    } catch (error) {
      alert(error.detail || error.message || "No se pudieron cargar los datos de cursos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  useEffect(() => {
    if (gradoSeleccionado) {
      listarCursos(gradoSeleccionado).then(setCursos).catch(() => setCursos([]));
    } else {
      setCursos([]);
    }
  }, [gradoSeleccionado]);

  const cursosDelGrado = useMemo(() => {
    if (!gradoSeleccionado) return [];
    return cursos.filter((curso) => String(curso.id_grado) === String(gradoSeleccionado));
  }, [cursos, gradoSeleccionado]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await crearCurso({
        id_docente: Number(form.id_docente),
        id_grado: Number(form.id_grado || gradoSeleccionado),
        id_materia: Number(form.id_materia),
        id_periodo: Number(form.id_periodo)
      });
      setForm({ id_docente: "", id_grado: "", id_materia: "", id_periodo: "" });
      await cargarDatos();
    } catch (error) {
      alert(error.detail || error.message || "No se pudo crear el curso");
    }
  };

  return (
    <section className="panel">
      <div className="panel-header">
        <h3 className="panel-title">Gestión de cursos</h3>
      </div>

      <div className="curso-layout">
        <div className="curso-col">
          <h4 className="curso-subtitle">Grado seleccionado</h4>
          <label>
            Grado
            <select value={gradoSeleccionado} onChange={(e) => setGradoSeleccionado(e.target.value)}>
              <option value="">Seleccione un grado</option>
              {grados.map((grado) => (
                <option key={grado.id_grado} value={grado.id_grado}>
                  {grado.nombre}
                </option>
              ))}
            </select>
          </label>

          <div className="curso-lista">
            {loading ? (
              <p>Cargando cursos...</p>
            ) : (
              <>
                <p className="curso-helper">Cursos ya creados para este grado</p>
                {cursosDelGrado.length === 0 ? (
                  <p className="curso-empty">Aún no hay cursos para este grado.</p>
                ) : (
                  <ul className="curso-chip-list">
                    {cursosDelGrado.map((curso) => (
                      <li key={curso.id_curso} className="curso-chip">
                        Curso #{curso.id_curso} · Materia {curso.id_materia} · Docente {curso.id_docente}
                      </li>
                    ))}
                  </ul>
                )}
              </>
            )}
          </div>
        </div>

        <div className="curso-col">
          <h4 className="curso-subtitle">Crear curso</h4>
          <form className="curso-form" onSubmit={handleSubmit}>
            <label>
              ID del docente
              <input
                value={form.id_docente}
                onChange={(e) => setForm({ ...form, id_docente: e.target.value })}
                placeholder="ID del profesor (temporal)"
                required
              />
              <span className="curso-note">TODO: reemplazar por select cuando exista endpoint de docentes.</span>
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
              Materia
              <select value={form.id_materia} onChange={(e) => setForm({ ...form, id_materia: e.target.value })}>
                <option value="">Seleccione una materia</option>
                {materias.map((materia) => (
                  <option key={materia.id_materia} value={materia.id_materia}>
                    {materia.nombre}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Periodo
              <select value={form.id_periodo} onChange={(e) => setForm({ ...form, id_periodo: e.target.value })}>
                <option value="">Seleccione un periodo</option>
                {periodos.map((periodo) => (
                  <option key={periodo.id_periodo} value={periodo.id_periodo}>
                    {periodo.nombre} ({periodo.anio})
                  </option>
                ))}
              </select>
            </label>
            <button type="submit">Crear curso</button>
          </form>
        </div>
      </div>
    </section>
  );
}
