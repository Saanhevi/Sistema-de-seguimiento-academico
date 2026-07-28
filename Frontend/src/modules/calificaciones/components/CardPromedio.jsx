import { formatearNota } from '../utils/notas';

const CardPromedio = ({ titulo, valor }) => {
  // null/undefined significan "todavía no hay notas"; los errores los muestra la pantalla.
  const hayValor = valor !== null && valor !== undefined && !Number.isNaN(Number(valor));

  return (
    <div style={{ 
      border: '1px solid #e2e8f0', 
      padding: '20px', 
      borderRadius: '10px', 
      minWidth: '220px', 
      backgroundColor: '#f8fafc',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      <h3 style={{ margin: '0 0 10px 0', fontSize: '16px', color: '#475569' }}>
        {titulo}
      </h3>
      <p style={{ margin: '0', fontSize: '28px', fontWeight: 'bold', color: '#0f172a' }}>
        {/* Corrección H13: mismo formato de dos decimales que la tabla de notas */}
        {hayValor ? formatearNota(valor) : "Sin datos"}
      </p>
    </div>
  );
};

export default CardPromedio;