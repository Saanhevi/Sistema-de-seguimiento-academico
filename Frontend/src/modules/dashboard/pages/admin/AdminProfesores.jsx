import { useEffect, useMemo, useState } from "react";
import ProfesorModal from "../../../profesores/components/ProfesorModal";
import ProfesorCard from "../../../profesores/components/ProfesorCard";
import { listarProfesores, crearProfesor, actualizarProfesor, activarDesactivarProfesor } from "../../../profesores/services/profesorService";

const FILTERS = [
  { key: "todos", label: "Todos" },
  { key: "activos", label: "Activos" },
  { key: "inactivos", label: "Inactivos" },
];

export const AdminProfesores = () => {
  const [profesores, setProfesores] = useState([]);
  const [filtro, setFiltro] = useState("todos");
  const [modalOpen, setModalOpen] = useState(false);
  const [profesorSeleccionado, setProfesorSeleccionado] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const cargarProfesores = async () => {
      try {
        setLoading(true);
        const data = await listarProfesores();
        setProfesores(data);
      } finally {
        setLoading(false);
      }
    };

    cargarProfesores();
  }, []);

  const profesoresFiltrados = useMemo(() => {
    if (filtro === "activos") return profesores.filter((item) => item.estado);
    if (filtro === "inactivos") return profesores.filter((item) => !item.estado);
    return profesores;
  }, [filtro, profesores]);

  const resumen = useMemo(() => {
    const activos = profesores.filter((item) => item.estado).length;
    const inactivos = profesores.length - activos;
    return {
      total: profesores.length,
      activos,
      inactivos,
    };
  }, [profesores]);

  const openCreateModal = () => {
    setProfesorSeleccionado(null);
    setModalOpen(true);
  };

  const openEditModal = (profesor) => {
    setProfesorSeleccionado(profesor);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setProfesorSeleccionado(null);
  };

  const handleSave = async (formData) => {
    if (profesorSeleccionado) {
      const actualizado = await actualizarProfesor(profesorSeleccionado.id, formData);
      setProfesores((prev) => prev.map((item) => (item.id === profesorSeleccionado.id ? { ...item, ...actualizado } : item)));
    } else {
      const creado = await crearProfesor(formData);
      setProfesores((prev) => [creado, ...prev]);
    }

    closeModal();
  };

  const handleToggleStatus = async (profesor) => {
    const nuevoEstado = !profesor.estado;
    await activarDesactivarProfesor(profesor.id, nuevoEstado);
    setProfesores((prev) => prev.map((item) => (item.id === profesor.id ? { ...item, estado: nuevoEstado } : item)));
  };

  return (
    <div className="profesores-shell">
      <section className="panel">
        <div className="panel-header">
          <div>
            <h2 className="panel-title">Profesores</h2>
            <p className="modal-caption">Gestiona la información básica de los docentes del sistema.</p>
          </div>
          <button type="button" className="primary-btn" onClick={openCreateModal}>
            Nuevo profesor
          </button>
        </div>

        <div className="profesores-summary">
          <div className="summary-card">
            <h3>Total</h3>
            <strong>{resumen.total}</strong>
          </div>
          <div className="summary-card active-card">
            <h3>Activos</h3>
            <strong>{resumen.activos}</strong>
          </div>
          <div className="summary-card inactive-card">
            <h3>Inactivos</h3>
            <strong>{resumen.inactivos}</strong>
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="profesores-toolbar">
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
          <p className="meta-text">{loading ? "Cargando profesores..." : `${profesoresFiltrados.length} registros visibles`}</p>
        </div>

        <div className="profesores-list">
          {profesoresFiltrados.map((profesor) => (
            <ProfesorCard key={profesor.id} profesor={profesor} onEdit={openEditModal} onToggleStatus={handleToggleStatus} />
          ))}
        </div>
      </section>

      <ProfesorModal isOpen={modalOpen} profesor={profesorSeleccionado} onClose={closeModal} onSave={handleSave} />
    </div>
  );
};

