import React, { useState, useEffect } from 'react'
import api from '../../../../services/api'
import '../../styles/EstudianteAsignaturas.css'

const defaultMaterias = [
  {
    id: 1,
    nombre: 'Matemáticas',
    docente: 'Ing. Laura Gómez',
    promedio: '4.16',
    escala: 'Escala 0–5',
    bimestres: [
      { id: 1, promedio: '4.13', actividades: [] },
      { id: 2, promedio: '4.14', actividades: [] },
      {
        id: 3,
        promedio: '4.22',
        actividades: [
          { titulo: 'Quiz rápido B3', peso: '10%', nota: '4.3' },
          { titulo: 'Tarea integradora', peso: '20%', nota: '3.1' },
          { titulo: 'Examen bimestral 3', peso: '45%', nota: '4.3' },
          { titulo: 'Práctica lab. B3', peso: '25%', nota: '5.0' }
        ]
      },
      { id: 4, promedio: '--', actividades: [] }
    ],
    definitiva: '4.16'
  },
  {
    id: 2,
    nombre: 'Ciencias Naturales',
    docente: 'Dra. Sofía Ríos',
    promedio: '4.02',
    escala: 'Escala 0–5',
    bimestres: [
      { id: 1, promedio: '3.95', actividades: [{ titulo: 'Observación de laboratorio', peso: '20%', nota: '4.0' }] },
      { id: 2, promedio: '4.10', actividades: [{ titulo: 'Informe de experimento', peso: '30%', nota: '4.2' }] },
      { id: 3, promedio: '4.00', actividades: [{ titulo: 'Proyecto ambiental', peso: '50%', nota: '4.0' }] },
      { id: 4, promedio: '4.05', actividades: [] }
    ],
    definitiva: '4.02'
  },
  {
    id: 3,
    nombre: 'Español',
    docente: 'Prof. Daniel Castro',
    promedio: '3.90',
    escala: 'Escala 0–5',
    bimestres: [
      { id: 1, promedio: '3.80', actividades: [{ titulo: 'Ensayo corto', peso: '25%', nota: '3.8' }] },
      { id: 2, promedio: '3.95', actividades: [{ titulo: 'Comprensión lectora', peso: '25%', nota: '4.0' }] },
      { id: 3, promedio: '4.00', actividades: [{ titulo: 'Exposición oral', peso: '20%', nota: '4.1' }] },
      { id: 4, promedio: '3.85', actividades: [] }
    ],
    definitiva: '3.90'
  }
]

const ACTIVITY_PESO = '10%'

function construirMateriasDesdeNotas(notas = []) {
  const actividades = notas.map((nota) => ({
    titulo: `Actividad ${nota.id_actividad}`,
    peso: ACTIVITY_PESO,
    nota: nota.calificacion?.toString() ?? '--',
    comentario: nota.comentario ?? '—'
  }))

  const promedio = actividades.length
    ? (
        actividades.reduce((sum, actividad) => sum + Number(actividad.nota || 0), 0) /
        actividades.length
      ).toFixed(2)
    : '--'

  return [
    {
      id: 1,
      nombre: 'Mis actividades',
      docente: 'Docente asignado',
      promedio,
      escala: 'Escala 0–5',
      bimestres: [
        {
          id: 1,
          promedio,
          actividades
        }
      ],
      definitiva: promedio
    }
  ]
}

export default function EstudianteAsignaturas() {
  const [materias, setMaterias] = useState(defaultMaterias)
  const [openMatter, setOpenMatter] = useState(defaultMaterias[0].id)
  const [openBimester, setOpenBimester] = useState(defaultMaterias[0].bimestres[0].id)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true

    async function cargarNotas() {
      try {
        const whoamiResponse = await api.get('/api/whoami')
        if (whoamiResponse?.data?.rol !== 'Estudiante') {
          return
        }

        const notasResponse = await api.get('/api/notas')
        const notas = Array.isArray(notasResponse.data) ? notasResponse.data : []
        if (!notas.length) {
          return
        }

        if (!mounted) {
          return
        }

        const materiasBackend = construirMateriasDesdeNotas(notas)
        setMaterias(materiasBackend)
        setOpenMatter(materiasBackend[0].id)
        setOpenBimester(materiasBackend[0].bimestres[0].id)
      } catch (error) {
        console.warn('No se pudieron cargar notas desde el backend:', error)
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }

    cargarNotas()
    return () => {
      mounted = false
    }
  }, [])

  return (
    <main className="ea-main">
      <section className="ea-hero">
        <div className="ea-hero-copy">
          <span className="ea-eyebrow">Seguimiento académico</span>
          <h1>Mis materias</h1>
          <p>Despliega cada materia para ver su progreso por bimestre y el detalle de tus actividades.</p>
        </div>

        <div className="ea-hero-stat">
          <span>Promedio general</span>
          <strong>4.03</strong>
          <small>Rendimiento destacado</small>
        </div>
      </section>

      <section className="ea-list">
        {materias.map(materia => (
          <div key={materia.id} className={`ea-matter ${openMatter === materia.id ? 'open' : ''}`}>
            <button
              className="ea-matter-header"
              onClick={() => setOpenMatter(openMatter === materia.id ? null : materia.id)}
              aria-expanded={openMatter === materia.id}
            >
              <div className="ea-matter-title">
                <div className="ea-matter-name">{materia.nombre}</div>
                <div className="ea-matter-subtitle">{materia.docente} · {materia.escala}</div>
              </div>
              <div className="ea-matter-meta">
                <span className="ea-badge">Promedio: {materia.promedio}</span>
                <span className={`ea-caret ${openMatter === materia.id ? 'open' : ''}`} aria-hidden>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M6 9l6 6 6-6" stroke="#335eef" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </span>
              </div>
            </button>

            {openMatter === materia.id && (
              <div className="ea-matter-body">
                <section className="ea-summary" aria-label={`Resumen de bimestres de ${materia.nombre}`}>
                  {materia.bimestres.map(b => (
                    <button
                      key={b.id}
                      className={`ea-summary-card ${openBimester === b.id ? 'active' : ''}`}
                      onClick={() => setOpenBimester(openBimester === b.id ? null : b.id)}
                      aria-expanded={openBimester === b.id}
                    >
                      <div className="ea-card-title">Bimestre {b.id}</div>
                      <div className="ea-card-value">{b.promedio}</div>
                    </button>
                  ))}

                  <div className="ea-definitiva">
                    <div className="ea-card-title">Definitiva</div>
                    <div className="ea-card-value">{materia.definitiva}</div>
                  </div>
                </section>

                <section className="ea-list-inner">
                  {materia.bimestres.map(b => (
                    <div key={b.id} className={`ea-bimester ${openBimester === b.id ? 'open' : ''}`}>
                      <div className="ea-bimester-header" onClick={() => setOpenBimester(openBimester === b.id ? null : b.id)}>
                        <div className="ea-bimester-title">
                          <div className="ea-bimester-name">Bimestre {b.id}</div>
                          <div className="ea-badge">Promedio: {b.promedio}</div>
                        </div>
                        <div className={`ea-caret ${openBimester === b.id ? 'open' : ''}`} aria-hidden>
                          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M6 9l6 6 6-6" stroke="#335eef" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                        </div>
                      </div>

                      {openBimester === b.id && (
                        <div className="ea-bimester-body">
                          {b.actividades.length === 0 ? (
                            <div className="ea-empty">No hay actividades registradas.</div>
                          ) : (
                            <table className="ea-table">
                              <thead>
                                <tr>
                                  <th>Actividad</th>
                                  <th>%</th>
                                  <th>Nota</th>
                                  <th>Comentario</th>
                                </tr>
                              </thead>
                              <tbody>
                                {b.actividades.map((a, i) => (
                                  <tr key={i}>
                                    <td>{a.titulo}</td>
                                    <td>{a.peso}</td>
                                    <td><span className="ea-note">{a.nota}</span></td>
                                    <td>{a.comentario}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </section>
              </div>
            )}
          </div>
        ))}
      </section>
    </main>
  )
}
