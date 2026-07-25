# Resumen de implementación — Cierre de HU10 (spec 8)

**Spec:** [`8-spec-hu10-cierre.md`](8-spec-hu10-cierre.md)
**Rama:** `mostrar_notas`
**Estado:** Implementado y verificado; los cambios están en el árbol de trabajo, sin commitear.

---

## 1. Punto de partida

La rama `mostrar_notas` ya marcaba HU10 como ✅ en `docs/historias-de-usuario-y-asignaciones.md`, pero la historia no se cumplía:

> Como estudiante, quiero consultar mis calificaciones mostrando **la materia, el profesor y las calificaciones obtenidas**.

La pieza central sí estaba hecha (el docente anidado en `CursoResponse` y su render en `EstudianteCalificaciones`). Lo que faltaba era todo lo que la rodeaba: dos pantallas del estudiante seguían mostrando profesores y notas inventados, la consulta no estaba acotada a *sus* cursos, y el campo nuevo publicaba el nombre de todos los docentes a cualquier usuario autenticado.

---

## 2. Qué se implementó

### 2.1 Se retiraron los datos falsos del portal del estudiante (§5.1)

Dos de las tres pantallas del estudiante fabricaban información académica:

- **`EstudianteAsignaturas.jsx`** — el ítem “Mis Asignaturas” del navbar. Un array literal con *Matemáticas / Ing. Laura Gómez / 4.16*, *Ciencias Naturales / Dra. Sofía Ríos*, *Español / Prof. Daniel Castro*, con bimestres y definitivas fijas, igual para cualquier estudiante. Se eliminó el componente y su CSS (523 líneas), se quitó la entrada del navbar y la ruta quedó como `Navigate` hacia `calificaciones` para no romper enlaces guardados.
- **`PortalEstudiantil.jsx`** — la **ruta por defecto** del estudiante. Saludaba “Bienvenida, Sofía”, mostraba “Promedio general 8.7” (escala 0–10 en un sistema 0–5) y entregas y notas de materias y profesores inexistentes. Se reescribió: saludo con el nombre real de `useAuth()` y la lista real de cursos con su docente, con estado vacío explícito cuando no hay datos.

### 2.2 La consulta se acotó a los cursos del estudiante (§5.2, RN-10a)

Antes el frontend pedía `GET /api/cursos?id_grado=N` por cada matrícula, sin año ni periodo, y `listar_cursos` no filtraba nada. El estudiante veía **todos** los cursos que ese grado tuvo en cualquier año, con sus docentes, presentados como “mis calificaciones”.

- `CursoRepository.listar_para_estudiante()`: `Curso ⋈ PeriodoAcademico ⋈ Matricula` exigiendo `Matricula.anio == PeriodoAcademico.anio`.
- `CursoService.listar_cursos(..., usuario_actual)`: para el rol Estudiante delega en ese método e **ignora** el `id_grado` recibido, con el mismo criterio que `listar_matriculas` aplica para RN-04.
- `CursoService.obtener_curso(..., usuario_actual)`: mismo alcance para `GET /api/cursos/{id_curso}`, que si no permitía recorrer ids y leer el docente de cualquier curso. Responde 404, no 403, para no confirmar que el curso existe.

El frontend pasó de *matrículas → N llamadas* a **una sola** `GET /api/cursos`, sin deduplicar ni descubrir grados: el alcance ya no se decide en el cliente.

### 2.3 El anidado dejó de poder tumbar la respuesta (§5.4, RN-10d)

`nombre` y `apellido` eran obligatorios. Comprobado en ejecución: un `Docente` sin fila `Usuario` producía `ValidationError: Field required`, que en FastAPI es un 500 de **toda la lista**, no del curso afectado. Ahora son opcionales y la derivación se hace con un `model_validator(mode="before")` que aplana `Usuario`.

### 2.4 Se retiró `GET /api/estudiantes/{id_estudiante}` (§5.5)

No tenía ningún consumidor en el frontend ni pruebas, y no participaba en HU10. Permitía además que cualquier Docente enumerara nombre y **correo** de todos los estudiantes iterando ids secuenciales, validaba al estudiante solo por `usuario.rol` (a diferencia del resto del código, que exige la fila en `Estudiante`) e instanciaba el repositorio dentro del router.

### 2.5 Limpieza (§5.6)

| Antes | Ahora |
|---|---|
| `DocenteResponse` en `schemas/curso.py`, colisionando con el de `schemas/docente.py` (formas incompatibles) | `DocenteCursoResponse` |
| `Docente.nombre` / `Docente.apellido` como `@property` sobre la clase mapeada | Fuera del modelo ORM; la derivación vive en el schema |
| `nombreDocente` interpolando directo (`"Laura undefined"`, y `"null null"` al volverse anulables los campos) | Se arma campo por campo, como `etiquetaCurso` |
| `nombreDocente(curso)` invocado dos veces por render | Izado a un `const` |
| `CursoRepository.crear` sin anidados → 5 lazy loads al serializar | Relee con `buscar_por_id` |

---

## 3. Archivos tocados

**Backend**
- `app/schemas/curso.py` — `DocenteCursoResponse`, campos opcionales, `model_validator`
- `app/repositories/curso.py` — `listar_para_estudiante`, `crear` con anidados
- `app/services/curso.py` — alcance en `listar_cursos` y `obtener_curso`
- `app/routers/curso.py` — pasa `usuario_actual`; endpoint retirado
- `app/models/docente.py` — sin las propiedades derivadas
- `app/tests/test_curso_calificaciones.py`, `app/tests/test_rbac_cursos.py`, `app/tests/test_calificaciones_integracion.py`
- `requirements.txt` — `httpx2`, `httpcore2`, `truststore`

**Frontend**
- `modules/calificaciones/services/calificacionService.js` — `listarMisCursosEstudiante`; se quitó `listarCursosDeGrado`
- `modules/calificaciones/utils/cursos.js` — `nombreDocente` endurecido
- `modules/dashboard/pages/estudiante/EstudianteCalificaciones.jsx` — una sola llamada
- `modules/dashboard/pages/estudiante/PortalEstudiantil.jsx` — reescrito con datos reales
- `modules/dashboard/pages/estudiante/EstudianteAsignaturas.jsx` y `styles/EstudianteAsignaturas.css` — **eliminados**
- `modules/dashboard/components/Navbar.jsx`, `routes/AppRouter.jsx`
- `modules/auth/pages/changePasswordPage.jsx` — ver §5

Total: 18 archivos, +382 / −759.

---

## 4. Validación

| Suite | Antes | Ahora |
|---|---|---|
| `test_curso_calificaciones` | 6 | **14** |
| `test_rbac_cursos` | 0 (no ejecutaba) | **3** |
| `test_calificacion_service` | 14 | 14 |
| `test_auth_service` | 5 | 5 |
| `test_curso_service_regression` | 2 | 2 |
| **Total ejecutable** | **27** | **38** |
| `test_calificaciones_integracion` | 7 (se saltan sin Docker) | **10** |

Pruebas nuevas: alcance de `listar_cursos` por rol, alcance de `obtener_curso` por id, degradación del docente sin `Usuario`, y en integración el camino real de HU10 (el estudiante recibe su curso con materia y profesor, y **no** recibe el curso del mismo grado en otro año).

Verificado además por HTTP con `TestClient`: las rutas quedan registradas, `/api/cursos` y `/api/cursos/{id}` exigen autenticación (401), y `/api/estudiantes/{id_estudiante}` responde 404 y desapareció del OpenAPI.

Frontend: `npm run build` compila; `eslint` no suma problemas nuevos (quedan 11 preexistentes, ajenos a este cambio).

---

## 5. Hallazgos colaterales

1. **El frontend no compilaba en Linux.** `changePasswordPage.jsx` importaba `../components/ChangePasswordForm`, pero el archivo en disco es `changePasswordForm.jsx`. En Windows/macOS pasaba; en Linux fallaba con `UNRESOLVED_IMPORT`. Se corrigió porque bloqueaba verificar todo lo demás — es ajeno a HU10 y podría ir en su propio commit.
2. **`test_rbac_cursos.py` nunca se ejecutaba**, por dos causas encadenadas: `fastapi.testclient` exige `httpx2` (agregado a `requirements.txt` junto con `httpcore2` y `truststore`), y el archivo estaba escrito como función suelta al estilo pytest, que no está en el proyecto, así que `unittest` recogía 0 pruebas. Se pasó a `unittest.TestCase` como el resto de la suite.
3. **`GET /api/secciones` y `GET /api/actividades` siguen sin alcance por usuario:** un estudiante puede enumerar secciones y actividades de cursos ajenos. Las *notas* sí están protegidas (RN-04). No afecta a HU10 con la UI actual; conviene cerrarlo junto con HU11.
4. **`get_session()` hace `return SessionLocal()` en vez de `yield` + `close()`:** ninguna sesión se cierra explícitamente. Preexistente y transversal a toda la API.

Los puntos 3 y 4 se dejaron documentados y **sin tocar**, por quedar fuera del alcance de esta spec.

---

## 6. Estado final

HU10 queda cumplida: el estudiante ve únicamente los cursos de su grado y año de matrícula, cada uno con materia, grado, periodo y **nombre del profesor**, y al expandirlos consulta sus propias calificaciones por sección y actividad. Ninguna pantalla del portal del estudiante muestra ya datos inventados.

Pendiente de HU11: porcentaje, comentario, nombre de la entrega y estudiante asociado a cada calificación, sobre esta misma pantalla.
