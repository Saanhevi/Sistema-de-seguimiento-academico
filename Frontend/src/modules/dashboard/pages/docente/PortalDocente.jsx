// eslint-disable-next-line no-unused-vars
import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Greeting from "../../components/Greeting";

// PortalDocente: componente funcional para docentes que muestra
// métricas clave, secciones activas, distribución de notas y tareas
// pendientes. Actualmente es una vista estática, pensada para
// ser alimentada más adelante con datos reales desde props o contexto.
export default function PortalDocente() {
  const location = useLocation();
  const isHomeView = location.pathname === '/dashboard/docente';

  if (!isHomeView) {
    return <Outlet />;
  }

  return (
    <>

      <main className="main">
        {/* Header de bienvenida y contexto de fecha para el docente */}
        <Greeting />

        {/* KPI cards con resúmenes rápidos de estudiantes, promedio y alertas */}
        <div className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-icon blue">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
            <div className="kpi-value">60</div>
            <div className="kpi-label">Total estudiantes</div>
            <div className="kpi-sub">4 secciones</div>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon teal">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0ED9B5" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>
              </svg>
            </div>
            <div className="kpi-value">7.8</div>
            <div className="kpi-label">Promedio general</div>
            <div className="kpi-sub">Matemáticas</div>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon orange">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFAA00" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <div className="kpi-value">12</div>
            <div className="kpi-label">En riesgo (&lt; 7)</div>
            <div className="kpi-sub">Requieren atención</div>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon purple">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
              </svg>
            </div>
            <div className="kpi-value pending">Pendiente</div>
            <div className="kpi-label">Asistencia hoy</div>
            <div className="kpi-sub">Sin registrar</div>
          </div>
        </div>

        {/* Contenido principal dividido en tres paneles: secciones, distribución de notas y pendientes */}
        <div className="content-grid">
          <div className="panel">
            <div className="panel-header">
              <span className="panel-title">Mis secciones</span>
              <a href="#notas" className="panel-link">Ver notas →</a>
            </div>

            {/* Fila de sección con cantidad de estudiantes, indicadores de riesgo y promedio */}
            <div className="section-row">
              <div className="section-badge">3ro A</div>
              <div className="section-info">
                <div className="label">15 estudiantes</div>
                <div className="risk-tag low">2 en riesgo</div>
                <div className="progress-bar" style={{ marginTop: '6px' }}><div className="fill" style={{ width: '78%' }}></div></div>
              </div>
              <div className="section-avg">7.8</div>
            </div>

            <div className="section-row">
              <div className="section-badge">3ro B</div>
              <div className="section-info">
                <div className="label">15 estudiantes</div>
                <div className="risk-tag mid">5 en riesgo</div>
                <div className="progress-bar" style={{ marginTop: '6px' }}><div className="fill" style={{ width: '75%' }}></div></div>
              </div>
              <div className="section-avg" style={{ color: 'var(--warn)' }}>7.5</div>
            </div>

            <div className="section-row">
              <div className="section-badge">2do A</div>
              <div className="section-info">
                <div className="label">15 estudiantes</div>
                <div className="risk-tag low">2 en riesgo</div>
                <div className="progress-bar" style={{ marginTop: '6px' }}><div className="fill" style={{ width: '79%' }}></div></div>
              </div>
              <div className="section-avg">7.9</div>
            </div>

            <div className="section-row">
              <div className="section-badge">2do B</div>
              <div className="section-info">
                <div className="label">15 estudiantes</div>
                <div className="risk-tag mid">3 en riesgo</div>
                <div className="progress-bar" style={{ marginTop: '6px' }}><div className="fill" style={{ width: '78%' }}></div></div>
              </div>
              <div className="section-avg">7.8</div>
            </div>
          </div>

          {/* Panel de distribución de notas - pendiente */}    
          

          

          <div className="panel">
            <div className="panel-header">
              <span className="panel-title">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ verticalAlign: '-2px', marginRight: '6px' }}>
                  <rect x="9" y="2" width="6" height="4" rx="1"/><path d="M5 4h-2a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2"/>
                  <line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="13" y2="16"/>
                </svg>
                Pendientes
              </span>
            </div>

            <div className="pending-list">
              <div className="pending-item urgent">
                <span className="pending-dot dot-orange"></span>
                Ingresar notas B3 · 3ro A
              </div>
              <div className="pending-item urgent">
                <span className="pending-dot dot-orange"></span>
                Ingresar notas B3 · 3ro B
              </div>
              <div className="pending-item normal">
                <span className="pending-dot dot-gray"></span>
                Revisar recuperaciones · 2do A
              </div>
              <div className="pending-item alert-item">
                <span className="pending-dot dot-teal"></span>
                Marcar asistencia · Hoy
              </div>
              <div className="pending-item" style={{ background: 'var(--alert-soft)', color: 'var(--alert)' }}>
                <span className="pending-dot dot-red"></span>
                Informe académico B2 · Pendiente entrega
              </div>
            </div>
          </div>
        </div>

      </main>
    </>
  );
}