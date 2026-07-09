// eslint-disable-next-line no-unused-vars
import React, { useState } from 'react';
import PortalDocente from './PortalDocente';
import PortalEstudiantil from './PortalEstudiantil';
import './styles.css';

export default function App() {
  // Estado para alternar entre vistas: 'docente' o 'estudiante'
  const [view, setView] = useState('docente');

  return (
    <>
      {/* Barra Superior Dinámica */}
      <header className="topbar">
        <div className="logo-area">
          <div className="logo-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>
            </svg>
          </div>
          <div className="logo-text">
            <h1>Colegio San Andrés</h1>
            <p>{view === 'docente' ? 'Portal Docente' : 'Portal Estudiantil'}</p>
          </div>
        </div>

        <div className="topbar-right">
          {/* Conmutador React interactivo */}
          <div className="view-toggle">
            <button 
              className={view === 'estudiante' ? 'active' : ''} 
              onClick={() => setView('estudiante')}
            >
              Estudiante
            </button>
            <button 
              className={view === 'docente' ? 'active' : ''} 
              onClick={() => setView('docente')}
            >
              Docente
            </button>
          </div>

          <button className="notif-btn" aria-label="Notificaciones">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4A6060" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
            <span className="dot"></span>
          </button>

          {view === 'docente' ? (
            <div className="user-pill">
              <div className="avatar">CG</div>
              <div className="user-info">
                <p>Prof. Carlos García</p>
                <p>Docente · Matemáticas</p>
              </div>
            </div>
          ) : (
            <div className="user-pill">
              <div className="avatar" style={{ background: 'var(--teal-primary)', color: 'var(--ink)' }}>SR</div>
              <div className="user-info">
                <p>Sofía Ramírez</p>
                <p>3ro de Bachillerato · Sección A</p>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Renderizado Condicional del Portal */}
      {view === 'docente' ? <PortalDocente /> : <PortalEstudiantil />}
    </>
  );
}