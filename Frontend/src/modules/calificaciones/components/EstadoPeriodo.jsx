/**
 * Banner informativo del estado del periodo académico del curso.
 * El estado llega anidado en el curso (BE-2), no hace falta llamar a /api/periodos.
 */
export default function EstadoPeriodo({ periodo }) {
  const abierto = periodo?.estado === "Abierto";

  return (
    <div className={`cal-period-banner ${abierto ? "open" : "closed"}`}>
      {abierto ? (
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="11" width="18" height="11" rx="2" />
          <path d="M7 11V7a5 5 0 0 1 9.9-1" />
        </svg>
      ) : (
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="11" width="18" height="11" rx="2" />
          <path d="M7 11V7a5 5 0 0 1 10 0v4" />
        </svg>
      )}
      {abierto
        ? "Periodo activo — edición habilitada"
        : "Periodo cerrado — solo lectura"}
    </div>
  );
}
