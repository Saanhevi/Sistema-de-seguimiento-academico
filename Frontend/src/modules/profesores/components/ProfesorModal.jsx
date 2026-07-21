import { useEffect, useState } from "react";

const initialForm = () => ({
  nombres: "",
  apellidos: "",
  correo: "",
  password: "",
  estado: true,
});

export default function ProfesorModal({ isOpen, profesor, onClose, onSave }) {
  const [formData, setFormData] = useState(initialForm());

  useEffect(() => {
    if (profesor) {
      setFormData({
        nombres: profesor.nombres || "",
        apellidos: profesor.apellidos || "",
        correo: profesor.correo || "",
        password: profesor.password || "",
        estado: profesor.estado ?? true,
      });
      return;
    }

    setFormData(initialForm());
  }, [profesor, isOpen]);

  if (!isOpen) return null;

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    const nextValue = type === "checkbox" ? checked : value;
    setFormData((prev) => ({ ...prev, [name]: nextValue }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSave(formData);
  };

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div className="modal-card" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
        <div className="panel-header modal-header">
          <div>
            <p className="panel-title">{profesor ? "Editar profesor" : "Nuevo profesor"}</p>
            <p className="modal-caption">Complete los datos básicos del docente para registrarlo en el sistema.</p>
          </div>
          <button type="button" className="ghost-btn" onClick={onClose}>
            Cerrar
          </button>
        </div>

        <form className="profesor-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <label className="field">
              <span>Nombres</span>
              <input
                type="text"
                name="nombres"
                value={formData.nombres}
                onChange={handleChange}
                required
              />
            </label>

            <label className="field">
              <span>Apellidos</span>
              <input
                type="text"
                name="apellidos"
                value={formData.apellidos}
                onChange={handleChange}
                required
              />
            </label>

            <label className="field field-full">
              <span>Correo institucional</span>
              <input
                type="email"
                name="correo"
                value={formData.correo}
                onChange={handleChange}
                required
              />
            </label>

            <label className="field field-full">
              <span>Contraseña inicial</span>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required={!profesor}
                placeholder={profesor ? "Mantener la actual si no se cambia" : "Ingrese una contraseña temporal"}
              />
            </label>

            <label className="field field-full switch-field">
              <span>Estado de acceso</span>
              <div className="switch-row">
                <input
                  type="checkbox"
                  name="estado"
                  checked={formData.estado}
                  onChange={handleChange}
                />
                <span>{formData.estado ? "Activo" : "Inactivo"}</span>
              </div>
            </label>
          </div>

          <div className="modal-actions">
            <button type="button" className="ghost-btn" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="primary-btn">
              {profesor ? "Guardar cambios" : "Crear profesor"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
