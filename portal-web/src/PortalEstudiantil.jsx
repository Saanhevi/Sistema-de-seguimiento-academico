// eslint-disable-next-line no-unused-vars
import React from 'react';

// PortalEstudiantil: componente funcional que renderiza la interfaz
// principal para estudiantes. Contiene navegación, sección hero,
// lista de entregas y calificaciones. Es un componente presentacional
// sin estado ni props por ahora.
//
// Este componente está organizado por bloques visuales:
// - nav: enlaces de navegación del tablero
// - hero: resumen académico y métricas clave
// - two-col: panel de entregas y panel de notas
export default function PortalEstudiantil() {
  return (
    <>
      {/* Navegación del panel estudiantil: enlaces a secciones internas del tablero */}
      <nav className="nav">
        <a href="#resumen" className="active">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
          </svg>
          Resumen
        </a>
        <a href="#asignaturas">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
          Mis Asignaturas
        </a>
        <a href="#historial">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
          </svg>
          Historial
        </a>
        <a href="#asistencia">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
          Asistencia
        </a>
      </nav>

      <main className="main">
        {/* Resumen principal del estudiante con contexto de bimestre y sección */}
        <div className="hero">
          <p className="hero-eyebrow">Año lectivo 2025–2026 · 3er Bimestre en curso</p>
          <h2 className="hero-name">Bienvenida, Sofía</h2>
          <p className="hero-sub">3ro de Bachillerato · Sección A · Colegio San Andrés</p>

          <div className="hero-stats">
            <div>
              <div style={{ fontSize: '11px', color: 'rgba(255,255,255,.5)', marginBottom: '4px' }}>Promedio general</div>
              <div className="hero-avg">8.7</div>
            </div>

            <div className="hero-meta">
              <div className="meta-item">
                <div className="meta-label">Asignaturas</div>
                <div className="meta-value">8</div>
              </div>
              <div className="meta-item">
                <div className="meta-label">Aprobadas</div>
                <div className="meta-value">7/8</div>
              </div>
              <div className="meta-item">
                <div className="meta-label">Entrega urgente</div>
                <div className="meta-value urgent-val">1</div>
              </div>
            </div>
          </div>
        </div>

        {/* Contenedor con dos paneles: actividades próximas y estado de notas */}
        <div className="two-col">
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                </svg>
                Próximas entregas y exámenes
              </div>
              <span className="urgent-badge">1 urgente</span>
            </div>

            <div className="delivery-list">
              {/* Lista de entregas y tareas con tags de prioridad y fechas límite */}
              <div className="delivery-item is-urgent">
                <div className="clock-icon urgent-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--alert)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                  </svg>
                </div>
                <div className="delivery-body">
                  <div className="delivery-tags">
                    <span className="tag tag-lab">Laboratorio</span>
                    <span className="delivery-subject">Química Orgánica · Prof. Núñez</span>
                  </div>
                  <div className="delivery-name">Informe de práctica: Reacciones de esterificación</div>
                  <div className="delivery-date">2026-06-17</div>
                </div>
                <div className="time-chip chip-urgent">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                  2d
                </div>
              </div>

              <div className="delivery-item">
                <div className="clock-icon warn-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--warn)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                  </svg>
                </div>
                <div className="delivery-body">
                  <div className="delivery-tags">
                    <span className="tag tag-proj">Proyecto</span>
                    <span className="delivery-subject">Historia · Prof. Salazar</span>
                  </div>
                  <div className="delivery-name">Ensayo: Consecuencias de la Primera Guerra Mundial</div>
                  <div className="delivery-date">2026-06-19</div>
                </div>
                <div className="time-chip chip-warn">4 días</div>
              </div>

              <div className="delivery-item">
                <div className="clock-icon normal-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--ink-muted)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                  </svg>
                </div>
                <div className="delivery-body">
                  <div className="delivery-tags">
                    <span className="tag tag-task">Tarea</span>
                    <span className="delivery-subject">Inglés · Prof. Williams</span>
                  </div>
                  <div className="delivery-name">Writing: Opinion essay (250 words)</div>
                  <div className="delivery-date">2026-06-20</div>
                </div>
                <div className="time-chip chip-ok">5 días</div>
              </div>
            </div>
          </div>

          {/* Panel de rendimiento académico con notas y barras de progreso */}
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
                </svg>
                Mis notas · B3
              </div>
            </div>

            <div className="grade-list">
              {/* Filas de asignaturas con estado visual: aprobado, en progreso o en riesgo */}
              <div className="grade-row">
                <div className="subject-dot" style={{ background: '#3B82F6' }}></div>
                <div className="grade-subject">Matemáticas</div>
                <div className="grade-bar-wrap"><div className="grade-bar-fill fill-green" style={{ width: '92%' }}></div></div>
                <div className="grade-num gn-green">9.2</div>
                <div className="grade-status gs-pass">✓</div>
              </div>

              <div className="grade-row">
                <div className="subject-dot" style={{ background: '#8B5CF6' }}></div>
                <div className="grade-subject">Química Orgánica</div>
                <div className="grade-bar-wrap"><div className="grade-bar-fill fill-green" style={{ width: '85%' }}></div></div>
                <div className="grade-num gn-green">8.5</div>
                <div className="grade-status gs-pass">✓</div>
              </div>

              <div className="grade-row">
                <div className="subject-dot" style={{ background: 'var(--alert)' }}></div>
                <div className="grade-subject">Ed. Física</div>
                <div className="grade-bar-wrap"><div className="grade-bar-fill fill-red" style={{ width: '62%' }}></div></div>
                <div className="grade-num gn-red">6.2</div>
                <div className="grade-status gs-risk">!</div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}