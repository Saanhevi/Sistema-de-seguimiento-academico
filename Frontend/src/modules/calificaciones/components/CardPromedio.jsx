import React from 'react';

const CardPromedio = ({ titulo, valor }) => {
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
        {/* Aquí está la magia de la corrección H13: validamos el null */}
        {valor !== null ? valor : "Sin datos"}
      </p>
    </div>
  );
};

export default CardPromedio;