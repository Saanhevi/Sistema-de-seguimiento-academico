import "../styles/Alertas.css";
import AlertaItem from "./AlertaItem";

export default function AlertasPanel({ alertas = [], loading = false, error = "", emptyMessage = "No hay alertas" }) {
  return (
    <div className="alertas-panel">
      {loading ? (
        <div className="pending-item normal">Cargando alertas...</div>
      ) : error ? (
        <div className="pending-item normal">{error}</div>
      ) : !alertas || alertas.length === 0 ? (
        <div className="pending-item normal">{emptyMessage}</div>
      ) : (
        <div className="pending-list">
          {alertas.map((alerta) => (
            <AlertaItem key={alerta.id_alerta} alerta={alerta} />
          ))}
        </div>
      )}
    </div>
  );
}
