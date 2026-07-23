import React, { useMemo, useEffect, useState } from 'react'
import api from '../../../../services/api'
import '../../styles/DocenteCalificaciones.css'

const secciones = ['3ro A', '3ro B', '2do A', '2do B']
const bimestres = [1, 2, 3, 4]

const studentFallback = [
  { id: 1, nombre: 'Sofía Ramírez', iniciales: 'SR', color: 'teal', promedio: 4.3, estado: 'Bueno' },
  { id: 2, nombre: 'Andrés Molina', iniciales: 'AM', color: 'blue', promedio: 3.8, estado: 'En proceso' },
  { id: 3, nombre: 'Camila Torres', iniciales: 'CT', color: 'orange', promedio: 4.6, estado: 'Excelente' },
  { id: 4, nombre: 'Mateo León', iniciales: 'ML', color: 'teal', promedio: 3.2, estado: 'Atención' }
]

const actividades = [
  { id: 1, nombre: 'Examen bimestral', porcentaje: 40, tipo: 'Examen' },
  { id: 2, nombre: 'Tarea integradora', porcentaje: 25, tipo: 'Tarea' },
  { id: 3, nombre: 'Proyecto final', porcentaje: 20, tipo: 'Proyecto' },
  { id: 4, nombre: 'Participación', porcentaje: 15, tipo: 'Participación' }
]

const notas = {
  1: { 1: 4.5, 2: 3.8, 3: 4.1, 4: 4.0 },
  2: { 1: 4.2, 2: 3.5, 3: 4.4, 4: 3.9 },
  3: { 1: 4.8, 2: 4.0, 3: 4.6, 4: 4.2 },
  4: { 1: 3.9, 2: 3.1, 3: 4.3, 4: 3.7 }
}

function getEstado(promedio) {
  if (promedio >= 4.2) return { label: 'Excelente', cls: 'good' }
  if (promedio >= 3.5) return { label: 'Bueno', cls: 'ok' }
  if (promedio >= 3.0) return { label: 'En proceso', cls: 'warn' }
  return { label: 'Atención', cls: 'alert' }
}

function getBadgeClass(value) {
  if (value >= 4.2) return 'good'
  if (value >= 3.5) return 'ok'
  if (value >= 3.0) return 'warn'
  return 'alert'
}

export default function DocenteCalificaciones() {
  const [seccion, setSeccion] = useState('3ro A')
  const [bimestre, setBimestre] = useState(3)
  const [editingId, setEditingId] = useState(null)
  const [draft, setDraft] = useState('')
  const [estudiantes, setEstudiantes] = useState(studentFallback)
  const [notasBackend, setNotasBackend] = useState([])
  const [studentNameMap, setStudentNameMap] = useState({})
  const [notaRows, setNotaRows] = useState([])
  const [loadingNotas, setLoadingNotas] = useState(true)

  const promedioSeccion = useMemo(() => {
    const avg = estudiantes.reduce((sum, student) => sum + student.promedio, 0) / estudiantes.length
    return avg.toFixed(1)
  }, [estudiantes])

  const getStudentName = (id) => {
    return studentNameMap[id] || estudiantes.find((item) => item.id === id)?.nombre || `Estudiante ${id}`
  }

  useEffect(() => {
    let mounted = true

    async function cargarDatos() {
      try {
        const response = await api.get('/api/notas')
        const notas = Array.isArray(response.data) ? response.data : []
        if (!mounted) return
        setNotasBackend(notas)

        const uniqueIds = [...new Set(notas.map((nota) => nota.id_estudiante))]
        const entries = await Promise.all(
          uniqueIds.map(async (id) => {
            try {
              const estudianteResponse = await api.get(`/api/estudiantes/${id}`)
              const estudiante = estudianteResponse.data
              const nombre = `${estudiante.nombre ?? ''} ${estudiante.apellido ?? ''}`.trim() || `Estudiante ${id}`
              return [id, nombre]
            } catch (error) {
              return [id, `Estudiante ${id}`]
            }
          })
        )

        if (!mounted) return
        setStudentNameMap(Object.fromEntries(entries))
      } catch (error) {
        console.warn('No se pudieron cargar notas desde el backend:', error)
      } finally {
        if (mounted) {
          setLoadingNotas(false)
        }
      }
    }

    cargarDatos()
    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    setNotaRows(
      notasBackend.map((nota) => ({
        id_actividad: nota.id_actividad,
        id_estudiante: nota.id_estudiante,
        nombre: getStudentName(nota.id_estudiante),
        calificacion: nota.calificacion
      }))
    )
  }, [notasBackend, estudiantes, studentNameMap])

  const handleSave = () => {
    if (editingId !== null) {
      setEditingId(null)
    }
  }

  return (
    <main className="ea-main">
      <div className="dc-page">
        <header className="dc-header">
          <div className="dc-title-group">
            <h1>Gestión de calificaciones</h1>
            <p>Administra notas por estudiante, bimestre y actividad con una vista rápida y clara.</p>
          </div>
          <div className="dc-header-actions">
            <button className="dc-btn-secondary">Exportar</button>
            <button className="dc-btn">Guardar cambios</button>
          </div>
        </header>

        <section className="dc-toolbar">
          <div className="dc-filter-group">
            <span className="dc-label">Curso</span>
            {secciones.map(item => (
              <button
                key={item}
                className={`dc-pill ${seccion === item ? 'active' : ''}`}
                onClick={() => setSeccion(item)}
              >
                {item}
              </button>
            ))}
          </div>

          <div className="dc-filter-group">
            <span className="dc-label">Bimestre</span>
            {bimestres.map(item => (
              <button
                key={item}
                className={`dc-chip-button ${bimestre === item ? 'active' : ''}`}
                onClick={() => setBimestre(item)}
              >
                B{item}
              </button>
            ))}
          </div>
        </section>

        <section className="dc-summary-grid">
          <article className="dc-summary-card">
            <span>Promedio sección</span>
            <strong>{promedioSeccion}</strong>
            <small>Escala 0–5</small>
          </article>
          <article className="dc-summary-card">
            <span>Actividades activas</span>
            <strong>{actividades.length}</strong>
            <small>{bimestre}° bimestre</small>
          </article>
          <article className="dc-summary-card">
            <span>Estado del período</span>
            <strong>Abierto</strong>
            <small>Edición habilitada</small>
          </article>
        </section>

        <section className="dc-student-card">
          <div>
            <strong>{seccion}</strong>
            <p>Matemáticas · {estudiantes.length} estudiantes · vista del docente</p>
          </div>
          <button className="dc-btn-secondary">Agregar actividad</button>
        </section>

        <section className="dc-table-wrap">
          {loadingNotas ? (
            <div className="dc-empty">Cargando notas...</div>
          ) : notaRows.length > 0 ? (
            <table className="dc-table">
              <thead>
                <tr>
                  <th>ID actividad</th>
                  <th>Estudiante</th>
                  <th>Nota</th>
                </tr>
              </thead>
              <tbody>
                {notaRows.map((nota, index) => (
                  <tr key={`${nota.id_estudiante}-${nota.id_actividad}-${index}`}>
                    <td>{nota.id_actividad}</td>
                    <td>{nota.nombre}</td>
                    <td>
                      <span className={`dc-row-btn ${getBadgeClass(nota.calificacion)}`}>
                        {nota.calificacion?.toFixed(1) ?? '--'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <table className="dc-table">
              <thead>
                <tr>
                  <th>Estudiante</th>
                  {actividades.map(actividad => (
                    <th key={actividad.id}>{actividad.nombre}</th>
                  ))}
                  <th>Promedio</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {estudiantes.map(student => {
                  const estado = getEstado(student.promedio)
                  return (
                    <tr key={student.id}>
                      <td>
                        <div className="dc-student-cell">
                          <div className={`dc-avatar ${student.color}`}>{student.iniciales}</div>
                          <div>
                            <strong>{student.nombre}</strong>
                            <p>{student.id} · {seccion}</p>
                          </div>
                        </div>
                      </td>
                      {actividades.map(actividad => {
                        const value = notas[bimestre][student.id] ?? 0
                        const isEditing = editingId === `${student.id}-${actividad.id}`
                        return (
                          <td key={actividad.id}>
                            {isEditing ? (
                              <div className="dc-grade-editor">
                                <input
                                  type="number"
                                  min="0"
                                  max="5"
                                  step="0.1"
                                  value={draft}
                                  onChange={(e) => setDraft(e.target.value)}
                                />
                                <div className="dc-editor-actions">
                                  <button className="save" onClick={handleSave}>Guardar</button>
                                  <button className="cancel" onClick={() => setEditingId(null)}>Cancelar</button>
                                </div>
                              </div>
                            ) : (
                              <button
                                className={`dc-row-btn ${getBadgeClass(value)}`}
                                onClick={() => {
                                  setEditingId(`${student.id}-${actividad.id}`)
                                  setDraft(String(value))
                                }}
                              >
                                {value.toFixed(1)}
                              </button>
                            )}
                          </td>
                        )
                      })}
                      <td>
                        <span className={`dc-row-btn ${getBadgeClass(student.promedio)}`}>{student.promedio.toFixed(1)}</span>
                      </td>
                      <td>
                        <span className={`dc-row-btn ${estado.cls}`}>{estado.label}</span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </section>
      </div>
  </main>
  )
}
