# Spec: Cierre de HU10 — Consulta de calificaciones del estudiante

**Owner:** Snehider (revisión: Mariana)
**Repo:** `Saanhevi/Sistema-de-seguimiento-academico`
**Rama:** `mostrar_notas` (desde `main`)
**Complementa:** SPEC 7: Frontend de calificaciones
**Origen:** revisión de código de la rama `mostrar_notas`, que marca HU10 como ✅ sin cumplirla del todo.

---

## 1. Objetivo

Cerrar de verdad **HU10**:

> Como estudiante, quiero consultar mis calificaciones mostrando **la materia, el profesor y las calificaciones obtenidas**, para conocer mi desempeño académico.

La rama `mostrar_notas` ya resolvió la pieza central (el docente anidado en `CursoResponse` y su render en `EstudianteCalificaciones`). Falta cerrar tres frentes que hoy impiden dar la historia por terminada: **datos falsos todavía visibles al estudiante**, **alcance de la consulta** y **exposición de datos del docente**.

---

## 2. Contexto — qué dejó pendiente `mostrar_notas`

La rama agrega:

- `CursoResponse.docente` (`id_docente`, `nombre`, `apellido`) con `joinedload(Curso.docente).joinedload(Docente.usuario)`.
- `nombreDocente()` en `utils/cursos.js` y su render en el acordeón de `EstudianteCalificaciones`.
- Un test de serialización del anidado.

Pero el estudiante sigue viendo **dos pantallas con datos inventados**, la consulta no está acotada a *sus* cursos, y el nuevo campo publica el nombre de todos los docentes a cualquier usuario autenticado.

---

## 3. Alcance

### Incluye

- Eliminar los datos mock que quedan en el portal del estudiante.
- Acotar `GET /api/cursos` para el rol `Estudiante` a los cursos que realmente cursa (grado **y** año de su matrícula).
- Endurecer la serialización del docente para que un dato inconsistente no tumbe la respuesta completa.
- Retirar el endpoint muerto `GET /api/estudiantes/{id_estudiante}`.
- Limpieza de nombres/duplicados introducidos por la rama.
- Tests que cubran el camino real de HU10.

### No incluye

- HU11 (porcentaje, comentario, nombre de la entrega y estudiante asociado por calificación) — es la historia siguiente y reusa esta misma pantalla.
- HU8/HU9 (promedios automáticos) — el promedio ponderado ya tiene utilidades en `utils/notas.js`, pero calcularlo y mostrarlo es de Laura.
- Rediseño visual del portal del estudiante.

---

## 4. Reglas de negocio

| Regla | Descripción |
|---|---|
| **RN-10a** | El estudiante solo ve cursos de un grado en el que tenga matrícula, y solo del año de esa matrícula (`Matricula.anio == PeriodoAcademico.anio`). |
| **RN-10b** | Ninguna pantalla del portal del estudiante puede mostrar materias, docentes, notas o promedios que no vengan del backend. Sin datos ⇒ estado vacío explícito, nunca un valor de ejemplo. |
| **RN-10c** | El nombre del docente se expone únicamente dentro de un curso que el solicitante tiene derecho a ver (se deriva de RN-10a y de RN-03 para el docente). |
| **RN-10d** | Un curso con datos incompletos (docente sin `Usuario`) degrada a `nombre`/`apellido` nulos; nunca produce un 5xx que tumbe la lista entera. Sin docente asignado, `docente: null`. |

---

## 5. Requisitos

### 5.1 — Blocker: retirar los datos falsos del portal del estudiante 🔴

**Problema.** Dos de las tres pantallas del estudiante muestran profesores y notas inventados:

| Archivo | Qué inventa |
|---|---|
| `pages/estudiante/EstudianteAsignaturas.jsx:4` | `const materias = [...]` — Matemáticas / *Ing. Laura Gómez* / 4.16, Ciencias Naturales / *Dra. Sofía Ríos*, Español / *Prof. Daniel Castro*, con bimestres y definitivas fijas. Es la pantalla del ítem **“Mis Asignaturas”** del navbar. |
| `pages/estudiante/PortalEstudiantil.jsx:30-36` | Es la **ruta por defecto** del estudiante. Saluda “Bienvenida, Sofía”, muestra “Promedio general **8.7**” (escala 0–10 en un sistema 0–5), “Química Orgánica · Prof. Núñez”, entregas y notas ficticias. |

Esto contradice HU10 de frente: la historia pide ver *el profesor* y *las calificaciones obtenidas*, y la pantalla más visible del estudiante fabrica ambos. El merge de la rama incluso revirtió el fetch real que se le había agregado a `EstudianteAsignaturas.jsx`.

**Decisión.** `EstudianteAsignaturas` es funcionalmente redundante con `EstudianteCalificaciones`, que sí consume el backend. Se **elimina** la pantalla mock (componente, CSS y entrada de navbar) en vez de duplicar el fetch; la ruta `/dashboard/estudiante/asignaturas` queda como `Navigate` a `calificaciones` para no romper enlaces guardados. `PortalEstudiantil` se reescribe: saludo con el nombre real de `useAuth()` y la lista real de cursos con su docente, con estado vacío explícito cuando no hay datos.

### 5.2 — Blocker: acotar la consulta a *mis* cursos 🔴

**Problema.** `EstudianteCalificaciones.jsx:121` hace `listarCursosDeGrado(matricula.id_grado)` → `GET /api/cursos?id_grado=N`, sin año ni periodo. `services/curso.py listar_cursos` no recibe `usuario_actual` y no filtra nada. Resultado: el estudiante ve **todos** los cursos que ha tenido ese grado en cualquier año — los de cohortes anteriores, con sus docentes — presentados como “mis calificaciones”.

**Solución.** Aplicar RN-10a en el backend (no en el frontend, que es donde no se puede confiar):

- `CursoRepository.listar_para_estudiante(id_estudiante, ...)`: `Curso ⋈ PeriodoAcademico ⋈ Matricula` con `Matricula.id_grado == Curso.id_grado AND Matricula.anio == PeriodoAcademico.anio AND Matricula.id_estudiante == :id`.
- `CursoService.listar_cursos(..., usuario_actual)`: si el rol es `Estudiante`, delega a ese método ignorando cualquier `id_grado` recibido — mismo patrón que ya usan `listar_matriculas` y `listar_notas` para RN-04.
- `routers/curso.py listar_cursos` pasa `usuario_actual=usuario`.
- `CursoService.obtener_curso(..., usuario_actual)`: mismo alcance para `GET /api/cursos/{id_curso}`, que si no permitía recorrer ids y leer el docente de cualquier curso. Responde **404**, no 403, para no confirmar que el curso existe.

Administrador y Docente conservan el comportamiento actual.

### 5.3 — Seguridad: el docente anidado amplía la fuga de `GET /api/cursos` 🟠

Con `listar_cursos` sin alcance, cualquier token de estudiante podía pedir `GET /api/cursos` sin filtros y recibir todos los cursos del colegio; con el cambio de la rama, ahora cada uno trae `nombre`, `apellido` e `id_docente` (= `id_usuario`) del profesor. Antes solo se filtraban enteros opacos.

Queda cubierto por 5.2 (RN-10c): al acotar la consulta del estudiante, el directorio de docentes deja de ser enumerable desde ese rol.

### 5.4 — Robustez: el anidado obligatorio puede tumbar la lista completa 🟠

`schemas/curso.py:53` declara `nombre: str` y `apellido: str` como **obligatorios**. Comprobado en ejecución:

```
CursoResponse.model_validate(curso)   # curso.docente presente, docente.usuario = None
ValidationError: docente.nombre  Field required [type=missing]
                 docente.apellido Field required [type=missing]
```

En FastAPI eso es `ResponseValidationError` → **HTTP 500 de toda la lista**, no del curso afectado. `grado`/`materia`/`periodo` y `EstudianteMatriculadoResponse` sí degradan. Es el mismo tipo de fila huérfana que documenta BE-4 del SPEC 7.

**Solución (RN-10d).** `nombre`/`apellido` opcionales, y la derivación desde `Usuario` se hace en el schema con un `model_validator(mode="before")` en lugar de propiedades en el modelo ORM.

### 5.5 — Retirar `GET /api/estudiantes/{id_estudiante}` 🟠

`routers/curso.py:133` agrega un endpoint que **no tiene un solo llamador en el frontend, ni un test**, y que no participa en HU10. Además:

- Deja que cualquier `Docente` enumere nombre y **correo** de todos los estudiantes iterando IDs secuenciales, sin verificar que le dé clase.
- Valida al estudiante solo por `usuario.rol`, mientras `crear_matricula`, `_validar_estudiante` y `listar_estudiantes_por_grado` exigen además la fila en `Estudiante`; tampoco mira `Estudiante.estado`.
- Instancia el repositorio dentro del router, saltándose la capa de servicio que usan las otras 11 rutas del archivo.
- Reusa `EstudianteMatriculadoResponse` para algo que no consulta matrículas.

**Decisión.** Se elimina. Si más adelante hace falta (HU12), se implementa en `CursoService` con verificación de pertenencia.

### 5.6 — Limpieza

| Ítem | Acción |
|---|---|
| `DocenteResponse` duplicado (`schemas/curso.py:49` vs `schemas/docente.py:24`), con formas incompatibles (`id_docente/nombre/apellido` vs `id/nombres/apellidos`) | Renombrar el nuevo a `DocenteCursoResponse` |
| `Docente.nombre` / `Docente.apellido` (`models/docente.py:22`) — propiedades Python sobre una clase mapeada: invisibles al query layer (`Docente(nombre=…)` revienta, `where(Docente.nombre == …)` no filtra), y en singular contra el `nombres`/`apellidos` del resto | Eliminar; la derivación pasa al schema (5.4) |
| `nombreDocente` (`utils/cursos.js:14`) — con payload parcial renderiza el literal `"Laura undefined"` | Defender campo por campo, como ya hace `etiquetaCurso` justo encima |
| `nombreDocente(curso)` llamado dos veces por render (`EstudianteCalificaciones.jsx:78-79`) | Izar a un `const` |
| `CursoRepository.crear` no aplica `_con_relaciones`, así que `POST /api/cursos` dispara 5 lazy loads al serializar | Releer el curso con `buscar_por_id` tras el commit |

---

## 6. Contrato de API (después del cambio)

```jsonc
// GET /api/cursos            (rol Estudiante: solo sus cursos, RN-10a)
// GET /api/cursos?id_grado=  (rol Estudiante: el filtro se ignora)
[
  {
    "id_curso": 10, "id_docente": 3, "id_grado": 1, "id_materia": 2, "id_periodo": 5,
    "grado":    { "id_grado": 1, "nombre": "6A" },
    "materia":  { "id_materia": 2, "nombre": "Matemáticas" },
    "periodo":  { "id_periodo": 5, "nombre": "Periodo 1", "anio": 2026, "estado": "Abierto" },
    // null si el curso no tiene docente; nombre/apellido en null si la fila Usuario falta
    "docente":  { "id_docente": 3, "nombre": "Laura", "apellido": "Gómez" }
  }
]
```

`GET /api/estudiantes/{id_estudiante}` deja de existir.

---

## 7. Plan de pruebas

| # | Prueba | Tipo |
|---|---|---|
| T1 | `CursoResponse` serializa `docente` con nombre y apellido | unitaria (ya existe) |
| T2 | `docente` presente pero `docente.usuario` ausente ⇒ `docente: null`, sin excepción | unitaria — **nueva**, cubre RN-10d |
| T3 | `listar_cursos` con rol `Estudiante` delega en `listar_para_estudiante` e **ignora** el `id_grado` recibido | unitaria — **nueva**, cubre RN-10a |
| T4 | `listar_cursos` con rol Administrador/Docente conserva los filtros | unitaria — **nueva** |
| T5 | e2e: el estudiante pide `/api/cursos` y recibe su curso **con** `docente`, y **no** recibe el curso de otro grado/año | integración — **nueva** (extiende `test_calificaciones_integracion.py`) |
| T6 | `GET /api/estudiantes/{id}` responde 404 (ruta retirada) | integración |

Las de integración siguen bajo `skipUnless(_backend_disponible())`; las unitarias corren siempre.

---

## 8. Estado de implementación

| § | Cambio | Archivos | Estado |
|---|---|---|---|
| 5.1 | Se elimina la pantalla mock `EstudianteAsignaturas` (componente + CSS + ítem de navbar); la ruta redirige a `calificaciones` | `pages/estudiante/EstudianteAsignaturas.jsx`, `styles/EstudianteAsignaturas.css`, `components/Navbar.jsx`, `routes/AppRouter.jsx` | ✅ |
| 5.1 | `PortalEstudiantil` reescrito sin datos inventados: saludo con `useAuth()` y cursos reales con su docente | `pages/estudiante/PortalEstudiantil.jsx` | ✅ |
| 5.2 | `listar_para_estudiante` + alcance en `listar_cursos` y `obtener_curso` | `repositories/curso.py`, `services/curso.py`, `routers/curso.py` | ✅ |
| 5.2 | El frontend pasa de `matriculas` → N× `cursos?id_grado=` a **una** llamada `GET /api/cursos` | `services/calificacionService.js`, `pages/estudiante/EstudianteCalificaciones.jsx` | ✅ |
| 5.4 | `nombre`/`apellido` opcionales + `model_validator` que aplana `Usuario` | `schemas/curso.py` | ✅ |
| 5.5 | `GET /api/estudiantes/{id_estudiante}` retirado | `routers/curso.py` | ✅ |
| 5.6 | `DocenteResponse` → `DocenteCursoResponse` | `schemas/curso.py` | ✅ |
| 5.6 | Propiedades `nombre`/`apellido` fuera del modelo ORM | `models/docente.py` | ✅ |
| 5.6 | `nombreDocente` defiende campo por campo; se iza a un `const` | `utils/cursos.js`, `EstudianteCalificaciones.jsx` | ✅ |
| 5.6 | `CursoRepository.crear` relee con los anidados | `repositories/curso.py` | ✅ |
| 7 | T2, T3, T4 unitarias (+ alcance de `obtener_curso`) y T5, T6 de integración | `tests/test_curso_calificaciones.py`, `tests/test_calificaciones_integracion.py` | ✅ |

**Verificación:** 38 pruebas en verde (antes 27, de las cuales `test_rbac_cursos` no llegaba a correr); 10 casos de integración registrados (antes 7), que se saltan sin Docker. Además se comprobó por HTTP con `TestClient` que las rutas quedan registradas, que `/api/cursos` y `/api/cursos/{id}` exigen autenticación (401) y que `/api/estudiantes/{id_estudiante}` responde 404 y desapareció del OpenAPI. `npm run build` compila y `eslint` no suma problemas nuevos (quedan 11 preexistentes, ajenos a este cambio).

### Hallazgos colaterales (fuera del alcance de esta spec)

1. **`changePasswordPage.jsx` importaba `../components/ChangePasswordForm`** pero el archivo en disco es `changePasswordForm.jsx`. En Windows/macOS el build pasaba; en Linux fallaba con `UNRESOLVED_IMPORT` y **el frontend no compilaba**. Se corrigió porque bloqueaba verificar todo lo demás.
2. **`test_rbac_cursos.py` no se ejecutaba** — resuelto durante esta tarea. Eran dos causas encadenadas: `fastapi.testclient` exige `httpx2` (se agregó a `requirements.txt` junto con `httpcore2` y `truststore`), y además el archivo estaba escrito como función suelta al estilo pytest, que no está en el proyecto, así que `unittest` recogía 0 pruebas. Se pasó a `unittest.TestCase` como el resto de la suite y ahora corre (3 casos), incluido uno que fija que `GET /api/estudiantes/{id}` ya no existe.
3. **`GET /api/secciones` y `GET /api/actividades` siguen sin alcance por usuario:** un estudiante puede enumerar secciones y actividades de cursos ajenos (las *notas* sí están protegidas por RN-04). No afecta a HU10 con la UI actual, pero conviene cerrarlo junto con HU11.
4. **`get_session()` en `core/dependencies.py` hace `return SessionLocal()` en vez de `yield` + `close()`:** ninguna sesión se cierra explícitamente. Preexistente y transversal a toda la API.

---

## 9. Criterio de aceptación de HU10

- [ ] Ninguna pantalla del portal del estudiante muestra materias, docentes o notas que no vengan del backend.
- [ ] El estudiante ve exactamente los cursos de su grado y año de matrícula, cada uno con materia, grado, periodo y **nombre del profesor**.
- [ ] Al expandir un curso ve sus secciones, actividades y **sus** calificaciones (RN-04 ya cubierto).
- [ ] Un curso con docente incompleto no rompe la lista.
- [ ] Un estudiante no puede obtener cursos ni docentes de grados ajenos.
- [ ] `docs/historias-de-usuario-y-asignaciones.md` marca HU10 ✅ **después** de lo anterior.
