# Spec: Frontend — Registro y Consulta de Calificaciones

**Owner:** Mariana  
**Repo:** `Saanhevi/Sistema-de-seguimiento-academico`  
**Complementa:** `4-spec-registro-calificaciones.md` (backend de calificaciones ya mergeado a `main`)  
**Rama sugerida:** `feat/frontend-calificaciones` (desde `main`)

---

## 0. Referencia visual: prototipo

Repo local: `d:\Documents\UNAL\Ingesoft1\PrototipoSitioWebEducativo`

**Archivo principal a adaptar:**  
`src/app/components/teacher/TeacherGrades.tsx` — es la implementación de referencia más completa para este módulo. Contiene:

- Vista de lista de estudiantes con tabla de notas por actividad y bimestre (columnas dinámicas).
- `GradeCell`: celda inline editable con clic, campo de nota + comentario, confirm/cancel con teclado.
- `ActivityModal`: modal para crear/editar actividades (nombre, tipo, porcentaje).
- Selector de sección (curso) y bimestre con pills activos.
- Aviso de periodo cerrado (lock) que deshabilita edición.
- Detalle individual de estudiante: todas sus actividades agrupadas por bimestre con promedios ponderados.

**Regla de traducción:** el prototipo usa TypeScript + Tailwind + shadcn. El proyecto real usa **React JS plano + CSS manual**. No copies el código tal cual — traduce el layout e interacción a JSX con las clases CSS del proyecto real.

> **Diferencia importante prototipo vs backend real:** el `ActivityModal` del prototipo tiene campos `tipo` y `porcentaje`. En el backend real, `ActividadEvaluativa` solo tiene `nombre`, `fecha`, `id_seccion` — **no tiene tipo ni porcentaje**. El porcentaje vive en `SeccionPorcentaje`, no en la actividad. Adapta el modal en consecuencia.

**Paleta idéntica** — las variables de `styles/variables.css` ya mapean exactamente los colores del prototipo:

| Prototipo (Tailwind/hardcoded) | Variables CSS real |
|---|---|
| `#0ED9B5` | `var(--teal-primary)` |
| `#34A6AA` | `var(--teal-brand)` |
| `#111C1C` | `var(--ink)` |
| `#F4F9F9` | `var(--bg)` |
| `#FF6B6B` | `var(--alert)` |
| `#FFAA00` | `var(--warn)` |
| `border-border` | `var(--border)` |
| `bg-card` | `var(--bg-card)` |
| `shadow-sm` | `var(--shadow-card)` |

**Archivos del prototipo también útiles:**  
- `src/app/components/teacher/TeacherPanel.tsx` — sidebar del docente, para entender la navegación del rol.
- `src/app/components/teacher/TeacherDashboard.tsx` — resumen de KPIs del docente.

---

## 0.5 Cambios de backend requeridos (HACER PRIMERO)

Antes de escribir el frontend hay que ajustar el backend. Estos cambios son la **base** para poder implementar el frontend siguiendo buenas prácticas (una sola llamada por vista, sin joins forzados en el cliente, sin datos inaccesibles). Se detectaron leyendo el código real de `main`.

Cada cambio indica: **por qué**, **archivos/líneas exactas**, **el fix** y su **clasificación** (🔴 bloqueante / 🟡 calidad).

Sugerencia de organización: los cambios de backend pueden ir en su propio commit inicial de esta rama (o en un PR pequeño previo). No los jmezcles en el mismo commit que el frontend.

---

### 🔴 BE-1. Exponer `id_usuario` en el login (bloqueante)

**Por qué:** el frontend necesita el `id_usuario` del docente autenticado para pedir sus cursos (`GET /api/cursos?id_docente=`). Hoy no está disponible en ninguna parte del cliente: `TokenResponse` solo devuelve `rol`, `nombres`, `apellidos`. Sin esto, `SelectorCurso` no puede arrancar.

**Archivos:**
- `Backend/app/schemas/auth.py` — `TokenResponse` (líneas 8-13).
- `Backend/app/services/auth.py` — `autenticar_usuario`, dict de retorno (líneas 48-54).

**Fix — `schemas/auth.py`:**
```python
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombres: str
    apellidos: str
    id_usuario: int          # + agregar
```

**Fix — `services/auth.py`** (el `user.id_usuario` ya existe en ese scope; se usa en la línea 44 para el claim `sub`):
```python
return {
    "access_token": token_real,
    "token_type": "bearer",
    "rol": user.rol,
    "nombres": user.nombres,
    "apellidos": user.apellidos,
    "id_usuario": user.id_usuario,   # + agregar
}
```

> **Alternativa considerada:** un endpoint `GET /api/auth/me` que decodifique el JWT (el `id_usuario` ya viaja en el claim `sub`). Es más "REST-purista" pero implica un endpoint + una llamada extra en cada carga. Para este proyecto, exponerlo en la respuesta del login es el cambio más pequeño y consistente con el patrón actual. **Recomendado: modificar la respuesta del login.**

---

### 🟡 BE-2. Enriquecer `CursoResponse` con nombres legibles (calidad)

**Por qué:** `CursoResponse` devuelve solo IDs (`id_grado`, `id_materia`, `id_periodo`). Para mostrar "Matemáticas · 3°A · Primer Periodo" en el `SelectorCurso`, el frontend tendría que hacer **3 llamadas extra** (`/api/grados`, `/api/materias`, `/api/periodos`) y cruzarlas en el cliente en cada render. Eso es frágil y no es buena práctica. El modelo `Curso` **ya tiene** los `relationship()` a `grado`, `materia`, `periodo` (ver `models/curso.py` líneas 22-25), así que enriquecer la respuesta es casi gratis.

**Retrocompatibilidad:** los consumidores actuales de `CursoResponse` (`CursoPanel.jsx`) solo leen los IDs planos. Agregar campos anidados **opcionales** no rompe nada.

**Archivos:**
- `Backend/app/schemas/curso.py` — `CursoResponse` (líneas 49-56). Reutiliza los schemas `GradoResponse`, `MateriaResponse`, `PeriodoAcademicoResponse` que ya existen en ese mismo archivo.
- `Backend/app/repositories/curso.py` — `listar` (líneas 20-30), para evitar el N+1 con eager loading.

**Fix — `schemas/curso.py`:**
```python
class CursoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_curso: int
    id_docente: int
    id_grado: int
    id_materia: int
    id_periodo: int
    # + anidados opcionales (Pydantic los lee de los relationship del modelo)
    grado: Optional[GradoResponse] = None
    materia: Optional[MateriaResponse] = None
    periodo: Optional[PeriodoAcademicoResponse] = None
```

**Fix — `repositories/curso.py`** (evita una query por cada curso al serializar los anidados):
```python
from sqlalchemy.orm import joinedload
# ...
def listar(self, id_docente=None, id_grado=None, id_periodo=None):
    query = select(Curso).options(
        joinedload(Curso.grado),
        joinedload(Curso.materia),
        joinedload(Curso.periodo),
    )
    # ...resto de filtros igual
```

**Resultado:** `GET /api/cursos?id_docente=` devuelve en **una sola llamada** todo lo que el selector necesita, incluido `periodo.estado` (que sirve directo para el banner de `EstadoPeriodo`, ver §6.6). El frontend deja de necesitar joins manuales.

---

### 🔴 BE-3. Permitir filtrar matrículas por `id_estudiante` (bloqueante para vista Estudiante)

**Por qué:** la vista del Estudiante (§8) necesita descubrir en qué grado está matriculado para encontrar sus cursos. Hoy `GET /api/matriculas` solo filtra por `id_grado` y `anio` — y el frontend no conoce el `id_grado` del estudiante. No hay forma de que el estudiante bootstrapee su propia lista de cursos. Falta un filtro por `id_estudiante`.

**Archivos:**
- `Backend/app/repositories/matricula.py` — `listar` (líneas 20-28).
- `Backend/app/services/curso.py` — `listar_matriculas` (líneas 141-142).
- `Backend/app/routers/curso.py` — `listar_matriculas` (líneas 111-118).

**Fix — `repositories/matricula.py`:**
```python
def listar(self, id_grado=None, anio=None, id_estudiante=None):
    query = select(Matricula)
    if id_grado is not None:
        query = query.where(Matricula.id_grado == id_grado)
    if anio is not None:
        query = query.where(Matricula.anio == anio)
    if id_estudiante is not None:                          # + agregar
        query = query.where(Matricula.id_estudiante == id_estudiante)
    return self.session.execute(query).scalars().all()
```

**Fix — `services/curso.py`** — pasar el parámetro y aplicar la regla de pertenencia (mismo patrón que `listar_notas` en calificaciones, que fuerza el filtro por rol Estudiante):
```python
def listar_matriculas(self, id_grado=None, anio=None, id_estudiante=None, usuario_actual=None) -> list[Matricula]:
    # Un Estudiante solo puede consultar sus propias matrículas
    if usuario_actual is not None and usuario_actual.rol == "Estudiante":
        id_estudiante = usuario_actual.id_usuario
    return self.matricula_repo.listar(id_grado=id_grado, anio=anio, id_estudiante=id_estudiante)
```

**Fix — `routers/curso.py`:**
```python
@router.get("/matriculas", response_model=list[MatriculaResponse])
def listar_matriculas(
    id_grado: int | None = None,
    anio: int | None = None,
    id_estudiante: int | None = None,                      # + agregar
    service: CursoService = Depends(get_curso_service),
    usuario=Depends(require_role("Administrador", "Docente", "Estudiante")),
):
    return service.listar_matriculas(id_grado=id_grado, anio=anio, id_estudiante=id_estudiante, usuario_actual=usuario)
```

> **Nota de seguridad:** al forzar `id_estudiante = usuario.id_usuario` cuando el rol es Estudiante, se evita que un estudiante liste matrículas ajenas. Es la misma decisión de pertenencia (RN-04) que ya aplica `listar_notas`.

---

### 🔴 BE-4. Bug: el registro de estudiante nunca persiste la fila `Estudiante` (bloquea pruebas)

**Por qué:** `crear_cuenta_estudiantil` (`services/auth.py` líneas 56-87) crea el objeto `Estudiante` en la línea 80 pero **nunca lo guarda** — falta la llamada al repositorio (`self.repositorio_estudiante.crear_estudiante(...)`, que sí existe en `repositories/estudiante.py`). Consecuencia: un estudiante registrado por la app tiene fila en `Usuario` (rol Estudiante) pero **no** en `Estudiante`.

Esto rompe dos cosas del flujo de calificaciones:
- `_validar_estudiante` (RN-e, `services/calificacion.py` líneas 94-100) exige que exista la fila `Estudiante` → cargar una nota a un estudiante auto-registrado da **400**.
- `listar_estudiantes_por_grado` (`services/curso.py` líneas 149-158) hace `JOIN Estudiante` → un estudiante sin esa fila **no aparece** en la tabla de notas del docente.

Sin este fix no se puede probar el flujo de punta a punta con estudiantes reales creados desde la app.

**Archivo:** `Backend/app/services/auth.py`, `crear_cuenta_estudiantil` (después de crear el `Estudiante`, antes del `return`).

**Fix:**
```python
estudiante = Estudiante(
    id_estudiante=usuario.id_usuario,
    estado="Activo",
)
self.repositorio_estudiante.crear_estudiante(estudiante)   # + agregar: hoy falta
```

> Este es un bug preexistente ajeno al frontend de calificaciones. Idealmente va en su **propio PR de fix** (no bundleado con el frontend), pero es prerequisito para poder demostrar el DoD end-to-end. Menciónalo en el standup.

---

### Resumen de cambios de backend

| ID | Cambio | Clasif. | Archivos | Desbloquea |
|---|---|---|---|---|
| BE-1 | `id_usuario` en `TokenResponse` + login service | 🔴 | `schemas/auth.py`, `services/auth.py` | SelectorCurso (todo el flujo docente) |
| BE-2 | `CursoResponse` con `grado`/`materia`/`periodo` anidados + `joinedload` | 🟡 | `schemas/curso.py`, `repositories/curso.py` | Nombres legibles + estado de periodo en 1 llamada |
| BE-3 | Filtro `id_estudiante` en `GET /api/matriculas` + regla de pertenencia | 🔴 | `repositories/matricula.py`, `services/curso.py`, `routers/curso.py` | Vista Estudiante |
| BE-4 | Persistir fila `Estudiante` en el registro | 🔴 (bug) | `services/auth.py` | Pruebas end-to-end con estudiantes reales |

**Frontend correspondiente a BE-1** (una vez el backend devuelve `id_usuario`):

`Frontend/src/models/Usuario.js`:
```js
export function crearUsuario({ rol, nombres, apellidos, id_usuario }) {
    return { rol, nombres, apellidos, id_usuario };
}
```

`Frontend/src/context/AuthContext.jsx` — función `login`:
```js
const login = ({ access_token, rol, nombres, apellidos, id_usuario }) => {
    const userData = crearUsuario({ rol, nombres, apellidos, id_usuario });
    setUser(userData);
    setToken(access_token);
    setStoredAuth({ user: userData, token: access_token });
};
```

Verifica con `useAuth()` que `usuario.id_usuario` esté disponible antes de seguir.

---

## 1. Objetivo

Reemplazar el placeholder de `DocenteCalificaciones.jsx` (actualmente con datos hardcodeados) por una vista funcional conectada al backend real que permita al Docente:

1. Seleccionar uno de sus cursos (combinación de sección/materia que le fue asignada).
2. Ver y gestionar las secciones de porcentaje de ese curso.
3. Crear actividades evaluativas dentro de cada sección.
4. Cargar y editar notas de los estudiantes del curso por actividad (carga individual y carga masiva).
5. Ver el estado del periodo (abierto/cerrado) y bloquear edición si está cerrado.

Y permitir al **Estudiante** autenticado ver únicamente sus propias notas.

---

## 2. Estado actual del frontend (punto de partida)

- `Frontend/src/modules/dashboard/pages/docente/DocenteCalificaciones.jsx` **ya existe** con datos hardcodeados. Reemplaza su contenido manteniendo el `export default`.
- `Frontend/src/modules/dashboard/styles/DocenteCalificaciones.css` **ya existe** con clases `dc-`. Puedes conservarla si reutilizas esas clases para el header/toolbar, o migrar todo a `Calificaciones.css`. **No borres el archivo** si `DocenteCalificaciones.jsx` aún lo importa — Vite lanza error si se importa un CSS inexistente.
- `AppRouter.jsx` ya tiene registrada la ruta `/dashboard/docente/calificaciones` → `DocenteCalificaciones`. **No la toques para la vista docente.**
- `PortalDocente.jsx` ya maneja el layout del portal docente. **No lo toques.**
- **Vista Estudiante:** `EstudianteAsignaturas.jsx` **ya tiene contenido propio** (3 materias hardcodeadas con bimestres y actividades). No es un placeholder — no se puede reutilizar para calificaciones sin romper la vista de asignaturas. La ruta `/dashboard/estudiante/calificaciones` necesita crearse y eso **sí** requiere tocar `AppRouter.jsx` (ver §7 pregunta 2).

---

## 3. Backend disponible (después de aplicar §0.5)

Documentado en `/docs` (Swagger del backend en Docker Compose):

| Método | Ruta | Quien puede llamar | Para qué |
|---|---|---|---|
| `GET` | `/api/cursos?id_docente=` | Docente, Admin, Estudiante | Listar cursos — filtra server-side; con BE-2 incluye `grado`/`materia`/`periodo` anidados |
| `GET` | `/api/secciones?id_curso=` | Docente, Admin, Estudiante | Listar secciones de porcentaje de un curso |
| `POST` | `/api/secciones` | Docente, Admin | Crear sección de porcentaje |
| `GET` | `/api/actividades?id_seccion=` | Docente, Admin, Estudiante | Listar actividades de una sección |
| `POST` | `/api/actividades` | Docente, Admin | Crear actividad evaluativa |
| `GET` | `/api/notas?id_actividad=` | Docente, Admin, Estudiante | Listar notas de una actividad (Estudiante solo ve la suya) |
| `POST` | `/api/notas` | Docente, Admin | Registrar nota individual |
| `POST` | `/api/notas/carga-masiva` | Docente, Admin | Upsert de notas de múltiples estudiantes en una actividad |
| `GET` | `/api/grados/{id_grado}/estudiantes?anio=` | Docente, Admin, Estudiante | Lista de estudiantes matriculados en un grado |
| `GET` | `/api/matriculas?id_estudiante=` | Docente, Admin, Estudiante | (con BE-3) Matrículas del estudiante — para descubrir su grado |
| `GET` | `/api/periodos` | Docente, Admin, Estudiante | Listar períodos académicos (incluye campo `estado`) |

**Body de `POST /api/secciones`:** `{ nombre_seccion, porcentaje, id_curso }`  
**Body de `POST /api/actividades`:** `{ nombre, fecha, id_seccion }`  
**Body de `POST /api/notas`:** `{ id_actividad, id_estudiante, calificacion, comentario? }`

**Body de `POST /api/notas/carga-masiva`:**
```json
{
  "id_actividad": 1,
  "notas": [
    { "id_estudiante": 2, "calificacion": 4.5, "comentario": "Excelente" },
    { "id_estudiante": 3, "calificacion": 3.8 }
  ]
}
```

**Response de `GET /api/secciones`:**
```json
[{ "id_seccion": 1, "nombre_seccion": "Primer corte", "porcentaje": 30.0, "id_curso": 1, "advertencia": null }]
```

**Response de `GET /api/cursos` (con BE-2 aplicado):**
```json
[{
  "id_curso": 1, "id_docente": 3, "id_grado": 2, "id_materia": 1, "id_periodo": 1,
  "grado":   { "id_grado": 2, "nombre": "3°A" },
  "materia": { "id_materia": 1, "nombre": "Matemáticas" },
  "periodo": { "id_periodo": 1, "nombre": "Primer Periodo", "anio": 2026, "estado": "Abierto" }
}]
```

**Response de `GET /api/notas`:**
```json
[{ "id_nota": 1, "id_actividad": 1, "id_estudiante": 2, "calificacion": 4.5, "comentario": "Excelente" }]
```

**Response de `GET /api/grados/{id_grado}/estudiantes`:**
```json
[{ "id_estudiante": 2, "nombre": "Sofía", "apellido": "Ramírez", "correo": "sofia@colegio.com" }]
```

---

## 4. Cómo llamar al backend (patrón establecido — síguelo tal cual)

Usa la instancia de axios de `Frontend/src/services/api.js` que inyecta el Bearer token automáticamente. Mismo patrón que `modules/auth/services/authService.js`:

```js
// Frontend/src/modules/calificaciones/services/calificacionService.js
import api from "../../../services/api";

export async function listarMisCursos(idDocente) {
  try {
    const response = await api.get("/api/cursos", { params: { id_docente: idDocente } });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}

export async function listarSecciones(idCurso) {
  try {
    const response = await api.get("/api/secciones", { params: { id_curso: idCurso } });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}

export async function crearSeccion(data) { /* POST /api/secciones, body: { nombre_seccion, porcentaje, id_curso } */ }
export async function listarActividades(idSeccion) { /* GET /api/actividades?id_seccion= */ }
export async function crearActividad(data) { /* POST /api/actividades, body: { nombre, fecha, id_seccion } */ }
export async function listarNotas(idActividad) { /* GET /api/notas?id_actividad= */ }
export async function registrarNota(data) { /* POST /api/notas */ }
export async function cargaMasiva(data) { /* POST /api/notas/carga-masiva */ }
export async function listarEstudiantesDeGrado(idGrado) { /* GET /api/grados/{id_grado}/estudiantes */ }
export async function listarMisMatriculas(idEstudiante) { /* GET /api/matriculas?id_estudiante= (vista Estudiante) */ }
```

> `listarEstudiantesDeGrado` ya existe en `modules/cursos/services/cursoService.js`. Puedes importarla desde ahí en lugar de duplicarla.

---

## 5. Estructura de archivos a crear

Sigue el patrón de módulo por dominio, igual que `modules/auth/` y `modules/profesores/`:

```
Frontend/src/modules/calificaciones/
  services/
    calificacionService.js        <- wrappers de todos los endpoints de §3

  components/
    SelectorCurso.jsx             <- lista de cursos del docente
    SeccionPanel.jsx              <- acordeón de secciones de porcentaje
    ActividadModal.jsx            <- modal crear actividad (nombre, fecha, id_seccion)
    TablaNotas.jsx                <- tabla de notas por actividad (inline editable)
    CargaMasivaModal.jsx          <- modal para cargar notas de toda la clase a la vez
    EstadoPeriodo.jsx             <- banner informativo de periodo abierto/cerrado

Frontend/src/modules/dashboard/pages/docente/
  DocenteCalificaciones.jsx       <- YA EXISTE — reemplazar contenido, mantener export default

Frontend/src/modules/dashboard/pages/estudiante/
  EstudianteCalificaciones.jsx    <- NUEVO (vista de solo lectura del estudiante, §8)

Frontend/src/styles/
  Calificaciones.css              <- estilos específicos del módulo (prefijo .cal-)
```

**Importa `Calificaciones.css` en `App.jsx`** junto a los demás imports de estilos, siguiendo el patrón existente.

---

## 6. Comportamiento de UI — Vista Docente (MVP)

### Flujo principal

```
DocenteCalificaciones
  +-- SelectorCurso              <- paso 0: elegir curso
       +-- (curso elegido)
            +-- EstadoPeriodo    <- banner abierto/cerrado (de curso.periodo.estado)
            +-- SeccionPanel     <- acordeón: lista de secciones + "Nueva sección"
            |    +-- (sección expandida → se convierte en la sección activa)
            |         +-- lista de actividades con nombre y fecha
            |         +-- botón "Nueva actividad" → ActividadModal
            +-- TablaNotas       <- tabla activa para la sección seleccionada
                 +-- botón "Carga masiva" → CargaMasivaModal
```

**Cómo fluye la selección de sección → tabla:** al expandir/seleccionar una sección en `SeccionPanel`, su `id_seccion` se guarda en el state de `DocenteCalificaciones` como `seccionActiva`. `TablaNotas` recibe `seccionActiva` como prop y carga las actividades + notas de esa sección. Sin sección activa, `TablaNotas` muestra un estado vacío ("Selecciona una sección para ver las notas").

### 6.1 SelectorCurso

- Al montar, llama a `GET /api/cursos?id_docente={usuario.id_usuario}` (una sola llamada; el filtro es server-side).
- Con BE-2 aplicado, cada curso trae `grado`, `materia` y `periodo` anidados → el label se arma directo: `` `${curso.materia.nombre} · ${curso.grado.nombre} · ${curso.periodo.nombre}` ``. **No hace falta cruzar con otros endpoints.**
- Muestra los cursos como chips o cards seleccionables.
- Al seleccionar un curso, guarda en state: el curso completo (incluye `id_grado` para la tabla y `periodo.estado` para el banner) y carga sus secciones.

### 6.2 SeccionPanel

- Lista las secciones del curso (`GET /api/secciones?id_curso=`).
- Muestra nombre + porcentaje de cada sección.
- Si el response incluye `advertencia` (secciones suman > 100%), muéstrala con `var(--warn)` y un ícono — no bloquees el flujo.
- Formulario inline o modal simple para crear sección: `nombre_seccion` (text) + `porcentaje` (number, 0-100). Solo visible si el periodo está abierto.
- Al hacer clic en una sección, actualiza `seccionActiva` en el state padre.

### 6.3 ActividadModal

Adapta el `ActivityModal` de `TeacherGrades.tsx`, traducido a JSX + CSS manual:

- Campos: `nombre` (text, max 50 chars), `fecha` (date). `id_seccion` viene de la sección activa — no hace falta campo visible.
- **No hay campo `tipo` ni `porcentaje`** — el backend de `ActividadEvaluativa` no los tiene.
- Botones: Cancelar / Agregar.
- Cierra el modal y refresca la lista de actividades después de crear.

### 6.4 TablaNotas

Componente central. Adapta la tabla de `TeacherGrades.tsx`:

- Props: `seccionActiva` (`{ id_seccion }`), `idGrado` (del curso), `periodoAbierto` (boolean).
- Al montar (o al cambiar `seccionActiva`):
  1. `GET /api/actividades?id_seccion={seccionActiva.id_seccion}` → columnas.
  2. `GET /api/grados/{idGrado}/estudiantes` → filas (usa `listarEstudiantesDeGrado`).
  3. Por cada actividad, `GET /api/notas?id_actividad=` → celdas.
- **Filas:** estudiantes del grado del curso. **Columnas:** actividades de la sección activa.
- **Celda editable (`GradeCell` equivalente):**
  - Clic abre input inline de nota (0.00–5.00) + comentario opcional.
  - Enter confirma, Escape cancela.
  - Al confirmar: `POST /api/notas` con `{ id_actividad, id_estudiante, calificacion, comentario }`.
  - Badge de color: `.cal-badge.good` (≥ 4.0), `.cal-badge.ok` (≥ 3.0), `.cal-badge.alert` (< 3.0).
- Periodo cerrado: celdas no editables, ícono de candado.
- Footer: promedio de la columna + botón "Carga masiva".

### 6.5 CargaMasivaModal

- Se abre desde el footer de `TablaNotas`.
- Formulario con un campo de nota por estudiante (lista scrolleable). La lista de estudiantes ya está en el state de `TablaNotas` — no vuelvas a llamar al backend.
- Al confirmar: `POST /api/notas/carga-masiva` con todas las notas de la actividad activa.
- Spinner mientras procesa; mensaje de éxito/error al terminar.
- Nota vacía → omítela del array `notas`.

### 6.6 EstadoPeriodo

- Banner debajo del selector de curso.
- Con BE-2, el estado viene directo en el curso seleccionado: `curso.periodo.estado` (`"Abierto"` / `"Cerrado"`). **No necesitas llamar a `/api/periodos` aparte.**
- `"Abierto"`: banner verde suave (`var(--ok-soft)`), "Periodo activo — edición habilitada".
- `"Cerrado"`: banner gris (`var(--bg)`), ícono de candado, "Periodo cerrado — solo lectura". Propaga `periodoAbierto={false}` a los componentes que editan.

---

## 7. Preguntas abiertas

1. **~~¿Cómo obtener la lista de estudiantes de un curso?~~ — RESUELTA:**  
   `GET /api/grados/{id_grado}/estudiantes` devuelve `[{ id_estudiante, nombre, apellido, correo }]`.  
   Flujo: `curso.id_grado` → `listarEstudiantesDeGrado(id_grado)` (ya en `cursoService.js`).

2. **¿Vista de calificaciones del Estudiante en `EstudianteAsignaturas.jsx` o nueva subruta?**  
   `EstudianteAsignaturas.jsx` **ya tiene contenido propio** (no es placeholder). Se necesita:  
   - Crear `EstudianteCalificaciones.jsx`.
   - Agregar `<Route path="calificaciones" element={<EstudianteCalificaciones />} />` en el bloque `estudiante` de `AppRouter.jsx`.  
   Requiere tocar `AppRouter.jsx` — coordina para no pisar PRs abiertos.

3. **~~¿El Docente ve todos los cursos o solo los suyos?~~ — RESUELTA:**  
   `GET /api/cursos?id_docente={usuario.id_usuario}` — filtra server-side. `id_usuario` disponible tras BE-1.

---

## 8. Vista Estudiante (MVP mínimo)

El estudiante autenticado ve sus propias calificaciones (solo lectura). Flujo (habilitado por BE-3):

1. `GET /api/matriculas?id_estudiante={usuario.id_usuario}` → obtiene su(s) `id_grado`. (BE-3 fuerza que el estudiante solo vea las suyas.)
2. `GET /api/cursos?id_grado={id_grado}` → cursos de su grado.
3. Por cada curso: `GET /api/secciones?id_curso=` → `GET /api/actividades?id_seccion=` → `GET /api/notas?id_actividad=` (el backend ya filtra la nota del estudiante autenticado, RN-04).

**UI:** acordeón de cursos → secciones → actividades → nota con badge de color. Sin formularios de edición. Usa el mismo `calificacionService.js`.

**Componentes reutilizados:** `SeccionPanel.jsx` puede recibir `readOnly={true}` para esconder los formularios de creación.

---

## 9. Estilos (Calificaciones.css)

Crea `Frontend/src/styles/Calificaciones.css` con prefijo `.cal-`. Reutiliza siempre las variables de `variables.css` — no hardcodees colores.

> **Nota sobre el CSS existente:** `modules/dashboard/styles/DocenteCalificaciones.css` (prefijo `dc-`) seguirá importado por `DocenteCalificaciones.jsx` mientras exista. Si migras todo a `Calificaciones.css`, puedes quitar ese import; no borres el archivo si aún hay clases `dc-` en uso.

Clases sugeridas (no exhaustivas):

```css
/* Toolbar de selección */
.cal-toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.cal-pill { padding: 6px 16px; border-radius: 99px; border: 1.5px solid var(--border);
            background: var(--bg-card); font-size: 13px; cursor: pointer; transition: all 0.15s; }
.cal-pill.active { background: var(--teal-primary); color: var(--ink);
                   border-color: var(--teal-primary); font-weight: 600; }
.cal-pill:hover:not(.active) { border-color: var(--teal-brand); }

/* Tabla de notas */
.cal-table-wrap { overflow-x: auto; border-radius: var(--radius-md); border: 1px solid var(--border); }
.cal-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.cal-table thead tr { background: var(--bg); }
.cal-table th { padding: 10px 14px; text-align: center; font-weight: 600;
                color: var(--ink-muted); font-size: 12px; border-bottom: 1px solid var(--border); }
.cal-table th:first-child { text-align: left; }
.cal-table tbody tr:hover { background: var(--ok-soft); }
.cal-table td { padding: 10px 14px; text-align: center; border-bottom: 1px solid var(--border); }
.cal-table td:first-child { text-align: left; }

/* Badges de nota */
.cal-badge { display: inline-block; min-width: 48px; padding: 3px 10px;
             border-radius: 99px; font-weight: 700; font-size: 13px; text-align: center; }
.cal-badge.good  { background: var(--ok-soft);   color: #0a8a70; border: 1.5px solid var(--teal-primary); }
.cal-badge.ok    { background: var(--warn-soft);  color: #b37400; border: 1.5px solid var(--warn); }
.cal-badge.alert { background: var(--alert-soft); color: var(--alert); border: 1.5px solid var(--alert); }
.cal-badge.empty { background: var(--bg);         color: var(--ink-muted); border: 1.5px solid var(--border); }

/* Editor inline de nota */
.cal-grade-editor { display: flex; flex-direction: column; gap: 4px; min-width: 130px; }
.cal-grade-editor input { padding: 5px 8px; border-radius: var(--radius-sm);
                           border: 2px solid var(--teal-primary); font-size: 13px;
                           text-align: center; outline: none; }
.cal-grade-actions { display: flex; gap: 4px; }
.cal-grade-actions button { flex: 1; padding: 4px; border-radius: var(--radius-sm);
                              font-size: 11px; border: none; cursor: pointer; }
.cal-grade-actions .save   { background: var(--teal-primary); color: var(--ink); }
.cal-grade-actions .cancel { background: var(--bg); color: var(--ink-muted); }

/* Banner de periodo */
.cal-period-banner { display: flex; align-items: center; gap: 10px; padding: 12px 18px;
                     border-radius: var(--radius-sm); font-size: 13px; font-weight: 500;
                     margin-bottom: 20px; }
.cal-period-banner.open   { background: var(--ok-soft); color: #0a8a70;
                             border: 1px solid var(--teal-primary); }
.cal-period-banner.closed { background: var(--bg); color: var(--ink-muted);
                             border: 1px solid var(--border); }

/* Modal overlay */
.cal-modal-overlay { position: fixed; inset: 0; background: rgba(17,28,28,0.35);
                     display: flex; align-items: center; justify-content: center; z-index: 100; }
.cal-modal { background: var(--bg-card); border-radius: var(--radius-md); padding: 28px;
             border: 1px solid var(--border); box-shadow: 0 8px 32px rgba(17,28,28,0.14);
             width: 100%; max-width: 420px; }
.cal-modal-header { display: flex; align-items: center; justify-content: space-between;
                    margin-bottom: 20px; }
.cal-modal-title { font-size: 15px; font-weight: 700; color: var(--ink); }

/* Formulario en modal */
.cal-field { margin-bottom: 14px; }
.cal-field label { display: block; font-size: 12px; color: var(--ink-muted);
                   margin-bottom: 5px; font-weight: 600; }
.cal-field input, .cal-field select {
  width: 100%; padding: 9px 12px; border-radius: var(--radius-sm);
  border: 1.5px solid var(--border); font-size: 13px; color: var(--ink);
  background: var(--bg); outline: none; transition: border-color 0.15s;
}
.cal-field input:focus, .cal-field select:focus { border-color: var(--teal-primary); }

/* Botones principales */
.cal-btn { padding: 9px 20px; border-radius: var(--radius-sm); font-size: 13px;
           font-weight: 600; cursor: pointer; border: none; transition: background 0.15s; }
.cal-btn.primary   { background: var(--teal-primary); color: var(--ink); }
.cal-btn.primary:hover   { background: var(--teal-brand); color: white; }
.cal-btn.secondary { background: var(--bg); color: var(--ink-muted);
                     border: 1.5px solid var(--border); }
.cal-btn.secondary:hover { border-color: var(--teal-brand); color: var(--ink); }

/* Sección acordeón */
.cal-seccion { border: 1px solid var(--border); border-radius: var(--radius-sm);
               margin-bottom: 10px; overflow: hidden; }
.cal-seccion-header { display: flex; align-items: center; justify-content: space-between;
                      padding: 12px 16px; cursor: pointer; background: var(--bg);
                      transition: background 0.1s; }
.cal-seccion-header:hover { background: var(--ok-soft); }
.cal-seccion-header.selected { background: var(--ok-soft); border-left: 3px solid var(--teal-primary); }
.cal-seccion-name { font-weight: 700; color: var(--ink); font-size: 14px; }
.cal-seccion-pct  { font-size: 12px; color: var(--teal-brand); font-weight: 600; }
.cal-seccion-body { padding: 14px 16px; background: var(--bg-card);
                    border-top: 1px solid var(--border); }

/* Advertencia de porcentaje */
.cal-warn-msg { display: flex; align-items: center; gap: 6px; font-size: 12px;
                color: #b37400; background: var(--warn-soft); padding: 8px 12px;
                border-radius: var(--radius-sm); margin-bottom: 12px;
                border: 1px solid var(--warn); }

/* Estado vacío */
.cal-empty { text-align: center; padding: 32px; color: var(--ink-muted); font-size: 14px; }
```

---

## 10. Reglas de arquitectura

- **No tocar:** `PortalDocente.jsx`, `PortalAdmin.jsx`.
- **`AppRouter.jsx`:** no tocar para la vista docente. Para la nueva ruta del estudiante (§7 pregunta 2), coordina con el equipo.
- **Mantener export:** `DocenteCalificaciones.jsx` usa `export default` — no lo cambies.
- **Sin hardcode de colores** — solo variables CSS de `variables.css`.
- **Sin TypeScript** — el proyecto es JS plano.
- **Sin librerías nuevas** — no instales nada que no esté ya en `package.json`.
- **El token no se maneja manualmente** — solo usa `api.js`.
- **Errores del backend:** muéstralos con el campo `detail` del response, en texto rojo (`var(--alert)`) debajo del formulario/modal.
- **Cálculo de promedio ponderado en cliente:** `promedio = Suma(calificacion * porcentaje) / Suma(porcentaje)` — con `calificacion` de cada nota y `porcentaje` de cada **sección** (las actividades no tienen porcentaje propio).
- **Backend antes que frontend:** aplica §0.5 (al menos BE-1 y BE-3) antes de escribir los componentes que dependen de esos datos.

---

## 11. Definition of Done

**Backend (§0.5):**
- [ ] BE-1: `id_usuario` en `TokenResponse` y en la respuesta del login; `useAuth()` lo expone.
- [ ] BE-2: `GET /api/cursos` devuelve `grado`/`materia`/`periodo` anidados (con `joinedload`, sin N+1).
- [ ] BE-3: `GET /api/matriculas?id_estudiante=` funciona y un Estudiante solo ve las suyas.
- [ ] BE-4: registrar un estudiante crea también su fila `Estudiante` (verificable en `psql` o vía el flujo de notas).

**Frontend:**
- [ ] `DocenteCalificaciones.jsx` reemplazado: cursos reales desde `GET /api/cursos?id_docente=`, sin datos hardcodeados.
- [ ] Flujo completo contra el backend real en Docker Compose: seleccionar curso → elegir sección → ver actividades → cargar nota individual → verificar en tabla.
- [ ] `POST /api/notas/carga-masiva` probado con al menos 3 estudiantes en una llamada desde `CargaMasivaModal`.
- [ ] Periodo cerrado bloquea edición (celdas no editables, botones de crear ocultos/deshabilitados).
- [ ] Si una sección trae `advertencia`, se muestra el aviso de > 100%.
- [ ] Estilos con prefijo `.cal-` en `Calificaciones.css`, importado en `App.jsx`. Sin colores hardcodeados.
- [ ] No se modificaron `PortalDocente.jsx` ni `PortalAdmin.jsx`.
- [ ] Vista del Estudiante: puede ver sus propias notas por actividad (solo lectura).
- [ ] PR contra `main` con al menos un review, según reglas del README.

---

## 12. Pendientes a coordinar en standup

- **Cambios de backend (§0.5):** decidir si van en un PR previo pequeño o como primeros commits de esta rama. BE-1 y BE-3 son bloqueantes; BE-2 es calidad; BE-4 es un bug preexistente que idealmente va en su propio fix.
- **Con Santiago (cursos/matrículas):** validar BE-2 (enriquecer `CursoResponse`) y BE-3 (filtro `id_estudiante` en matrículas) — son sus módulos. Confirmar que `GET /api/grados/{id_grado}/estudiantes` devuelve nombres completos.
- **Con quien mantiene `auth`:** BE-1 (`id_usuario` en login) y BE-4 (bug del registro de estudiante) tocan `services/auth.py`. Coordinar para no pisarse.
- **Con Snehider (consulta de calificaciones):** si ya planifica una vista de Estudiante, coordinar para no duplicar. La de este spec es la mínima.
- **Con Laura (promedios):** el promedio ponderado de este spec usa `porcentaje` de la sección (las actividades no tienen porcentaje en el backend). Confirmar que su cálculo usa la misma lógica.
- **Con quien mantiene `AppRouter.jsx`:** agregar la ruta `calificaciones` del estudiante sin pisar PRs abiertos.
- **Deuda de lint (§13):** `npm run lint` ya fallaba en `main` antes de este spec. Decidir quién toma el PR de limpieza.

---

## 13. Deuda de lint en archivos ajenos a este módulo

`npm run lint` **falla en `main`** desde antes de este spec: 11 errores y 2 warnings, todos en archivos de otros módulos. Los archivos nuevos de `modules/calificaciones/` ya salen limpios, así que el módulo de calificaciones no aporta ni un error nuevo — pero mientras el resto siga en rojo no se puede meter el lint en CI ni usarlo como criterio de review.

Esta sección define cómo dejar el repo en verde. **Va en su propio PR de `chore`**, no mezclado con el frontend de calificaciones: toca módulos de otras personas y un PR de limpieza mecánica se revisa mucho más rápido si no viene con features encima.

### Inventario

| Archivo | Línea | Regla | Grupo |
|---|---|---|---|
| `modules/cursos/components/GradoPanel.jsx` | 22 | `react-hooks/set-state-in-effect` | A |
| `modules/cursos/components/MateriaPanel.jsx` | 22 | `react-hooks/set-state-in-effect` | A |
| `modules/cursos/components/PeriodoPanel.jsx` | 24 | `react-hooks/set-state-in-effect` | A |
| `modules/cursos/components/CursoPanel.jsx` | 39 | `react-hooks/set-state-in-effect` | A |
| `modules/cursos/components/CursoPanel.jsx` | 40 | `react-hooks/exhaustive-deps` (warning) | A |
| `modules/cursos/components/CursoPanel.jsx` | 46 | `react-hooks/set-state-in-effect` | B |
| `modules/cursos/components/MatriculaPanel.jsx` | 36 | `react-hooks/set-state-in-effect` | A |
| `modules/cursos/components/MatriculaPanel.jsx` | 37 | `react-hooks/exhaustive-deps` (warning) | A |
| `modules/cursos/components/MatriculaPanel.jsx` | 44 | `react-hooks/set-state-in-effect` | B |
| `modules/profesores/components/ProfesorModal.jsx` | 16 | `react-hooks/set-state-in-effect` | C |
| `modules/dashboard/pages/estudiante/EstudianteAsignaturas.jsx` | 1 | `no-unused-vars` | D |
| `context/AuthContext.jsx` | 41 | `react-refresh/only-export-components` | E |

> **Por qué aparecieron:** `eslint-plugin-react-hooks` v7 (ya en `package.json`) trae las reglas del React Compiler. `set-state-in-effect` prohíbe llamar `setState` de forma **síncrona** dentro de un efecto, porque provoca un render en cascada. La regla sigue las llamadas a funciones: `useEffect(() => { cargarDatos(); })` también la dispara si `cargarDatos` empieza con `setLoading(true)`.

---

### Grupo A — carga inicial en `useEffect` (6 errores + 2 warnings)

Patrón actual (`GradoPanel.jsx` líneas 9-23, idéntico en `MateriaPanel`, `PeriodoPanel`, `CursoPanel`, `MatriculaPanel`):

```jsx
const [loading, setLoading] = useState(false);

const cargarGrados = async () => {
  setLoading(true);                 // <- setState síncrono...
  try {
    setGrados(await listarGrados());
  } finally {
    setLoading(false);
  }
};

useEffect(() => {
  cargarGrados();                   // <- ...alcanzado desde el efecto
}, []);
```

**Fix** — el estado de carga arranca en `true` y el efecto solo hace `setState` dentro de callbacks asíncronos. El flag `vigente` además evita escribir estado sobre un componente ya desmontado:

```jsx
const [loading, setLoading] = useState(true);   // arranca en true

// Se conserva SOLO para el refresco manual: llamar setState desde un
// event handler (handleSubmit) sí está permitido por la regla.
const cargarGrados = async () => { /* igual que hoy */ };

useEffect(() => {
  let vigente = true;

  listarGrados()
    .then((data) => { if (vigente) setGrados(data); })
    .catch((error) => {
      if (vigente) alert(error.detail || "No se pudieron cargar los grados");
    })
    .finally(() => { if (vigente) setLoading(false); });

  return () => { vigente = false; };
}, []);
```

Los dos warnings de `exhaustive-deps` (`CursoPanel:40`, `MatriculaPanel:37`) **desaparecen solos**: al inlinear el fetch, el efecto deja de referenciar `cargarDatos`.

**Referencia viva:** `modules/calificaciones/components/SelectorCurso.jsx` y `SeccionPanel.jsx` ya usan exactamente este patrón.

---

### Grupo B — reset de estado en la rama `else` (2 errores)

`CursoPanel.jsx` líneas 42-48 y `MatriculaPanel.jsx` líneas 39-47:

```jsx
useEffect(() => {
  if (gradoSeleccionado) {
    listarCursos(gradoSeleccionado).then(setCursos).catch(() => setCursos([]));
  } else {
    setCursos([]);                  // <- setState síncrono en el efecto
  }
}, [gradoSeleccionado]);
```

**Fix** — no resetear desde el efecto: derivar el valor en el render. El efecto solo corre cuando hay algo que pedir.

```jsx
useEffect(() => {
  if (!gradoSeleccionado) return undefined;

  let vigente = true;
  listarCursos(gradoSeleccionado)
    .then((data) => { if (vigente) setCursos(data); })
    .catch(() => { if (vigente) setCursos([]); });

  return () => { vigente = false; };
}, [gradoSeleccionado]);

// El "vacío" se deriva, no se guarda en state:
const cursosVisibles = gradoSeleccionado ? cursos : [];
```

En `CursoPanel` esto encaja directo con el `useMemo` de `cursosDelGrado` (líneas 50-53), que ya filtra por grado. En `MatriculaPanel` hay que derivar tanto `matriculas` como `estudiantes`.

**Referencia viva:** `DocenteCalificaciones.jsx` hace lo mismo con `actividadesVisibles`.

---

### Grupo C — `ProfesorModal` sincroniza props a state (1 error)

`ProfesorModal.jsx` líneas 14-27: un `useEffect` copia la prop `profesor` al state `formData` cada vez que cambia. Es el antipatrón que la regla busca señalar.

**Fix** — remontar el modal con `key` y calcular el estado inicial una sola vez. Se elimina el `useEffect` completo:

```jsx
// ProfesorModal.jsx — sin useEffect
export default function ProfesorModal({ profesor, onClose, onSave }) {
  const [formData, setFormData] = useState(() =>
    profesor
      ? {
          nombres: profesor.nombres || "",
          apellidos: profesor.apellidos || "",
          correo: profesor.correo || "",
          password: profesor.password || "",
          estado: profesor.estado ?? true,
        }
      : initialForm()
  );
  // ...resto igual
}
```

```jsx
// AdminProfesores.jsx línea 135 — render condicional + key
{modalOpen && (
  <ProfesorModal
    key={profesorSeleccionado?.id_docente ?? "nuevo"}
    profesor={profesorSeleccionado}
    onClose={closeModal}
    onSave={handleSave}
  />
)}
```

La prop `isOpen` desaparece (el padre ya decide si montarlo). Verifica el nombre real del identificador del profesor en `profesorService.js` antes de usarlo como `key`.

---

### Grupo D — import de React sin usar (1 error)

`EstudianteAsignaturas.jsx` línea 1: `import React from 'react';` y el archivo nunca usa `React`. Con el JSX transform automático (React 19 + `@vitejs/plugin-react`) el import no hace falta.

**Fix:** borrar la línea.

> **Limpieza opcional en el mismo PR:** `PortalDocente.jsx`, `PortalEstudiantil.jsx` y `DocenteAsistencia.jsx` tienen el mismo import muerto pero silenciado con `// eslint-disable-next-line no-unused-vars` encima. No dan error, pero conviene borrar las dos líneas (comentario + import) para que el patrón quede uniforme.

---

### Grupo E — `AuthContext.jsx` exporta un hook junto al provider (1 error)

`AuthContext.jsx` exporta `AuthProvider` (componente) y `useAuth` (hook). `react-refresh/only-export-components` pide que un archivo con componentes no exporte otras cosas, porque rompe el Fast Refresh en dev.

**Fix** — mover el hook a su propio archivo:

```js
// Frontend/src/context/useAuth.js
import { useContext } from "react";
import { AuthContext } from "./AuthContext";

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  }
  return context;
}
```

`AuthContext.jsx` pasa a exportar el contexto (`export const AuthContext = createContext();`) y `AuthProvider`, y se le quita la función `useAuth`.

Hay que actualizar el import en los **8 archivos** que lo consumen:
`AppRouter.jsx`, `Navbar.jsx`, `Header.jsx`, `Greeting.jsx`, `DashboardPage.jsx`, `LoginForm.jsx`, `DocenteCalificaciones.jsx`, `EstudianteCalificaciones.jsx`.

```bash
grep -rl "context/AuthContext" Frontend/src
```

> **Alternativa barata:** dejar el hook donde está y silenciar la regla con un `// eslint-disable-next-line react-refresh/only-export-components`. Solo si el PR de limpieza se vuelve demasiado grande — el fix real es trivial y mejora el Fast Refresh. **Recomendado: separar el hook.**

---

### Orden sugerido

1. Grupo D (borrar imports muertos) — 1 minuto, sin riesgo.
2. Grupo A (carga inicial) — mecánico, 5 archivos, mismo patrón.
3. Grupo B (reset derivado) — 2 archivos, requiere leer el render.
4. Grupo E (`useAuth`) — mecánico pero toca 8 archivos; commit aparte para que el diff se lea fácil.
5. Grupo C (`ProfesorModal`) — el único que cambia una interfaz de componente; probar el alta y la edición de profesor a mano.

### Definition of Done del PR de lint

- [ ] `npm run lint` termina con **0 errores y 0 warnings**.
- [ ] `npm run build` sigue pasando.
- [ ] Probado a mano: panel de admin (grados, materias, periodos, cursos, matrículas), alta y edición de profesor, login/logout.
- [ ] Sin cambios de comportamiento: es un PR de `chore`, no de feature.
- [ ] Una vez en verde, proponer en standup añadir `npm run lint` al CI para que no vuelva a acumularse.
