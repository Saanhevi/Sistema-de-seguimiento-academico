export default function AlertaItem({ alerta }) {
  const isHigh = alerta.nivel === "Alto";
  const isMedium = alerta.nivel === "Medio";
  const itemClass = isHigh ? "urgent" : isMedium ? "normal" : "alert-item";
  const dotClass = isHigh ? "dot-red" : isMedium ? "dot-orange" : "dot-teal";

  return (
    <div className={`pending-item ${itemClass}`}>
      <span className={`pending-dot ${dotClass}`}></span>
      <span className="alert-text">
        {alerta.nombre_estudiante} [{alerta.nombre_curso || "Curso desconocido"}]: {alerta.mensaje}
      </span>
    </div>
  );
}
