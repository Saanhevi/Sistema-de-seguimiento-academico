import { useEffect, useState } from "react";
import { useAuth } from "../../../../context/AuthContext";
import { misAsistencias } from "../../../asistencias/services/asistenciaService";
import "../../../asistencias/styles/Asistencia.css";

export default function EstudianteAsistencia() {
  const { user } = useAuth();
  const [asistencias, setAsistencias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mensaje, setMensaje] = useState({ type: "", text: "" });

  useEffect(() => {
    async function cargarAsistencias() {
      try {
        setLoading(true);
        const data = await misAsistencias();
        setAsistencias(data ?? []);
        setMensaje({ type: "", text: "" });
      } catch (err) {
        console.error(err);
        setMensaje({
          type: "error",
          text: "No fue posible cargar tus inasistencias."
        });
      } finally {
        setLoading(false);
      }
    }

    if (user) {
      cargarAsistencias();
    }
  }, [user]);

  return (
    <section className="asistencia-container">
      <h2>Mis inasistencias</h2>

      {mensaje.text && <p className={`message ${mensaje.type}`}>{mensaje.text}</p>}

      {loading ? (
        <p>Cargando...</p>
      ) : asistencias.length === 0 ? (
        <div className="asistencia-card">
          <p>No tienes inasistencias registradas.</p>
        </div>
      ) : (
        <div className="asistencia-card">
          <table className="tabla-asistencia">
            <thead>
              <tr>
                <th>Materia</th>
                <th>Fecha</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {asistencias.map((registro, index) => (
                <tr key={`${registro.fecha}-${registro.materia}-${index}`}>
                  <td>{registro.materia}</td>
                  <td>{registro.fecha}</td>
                  <td>
                    <span className={`badge ${registro.estado?.toLowerCase?.() || "presente"}`}>
                      {registro.estado}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
