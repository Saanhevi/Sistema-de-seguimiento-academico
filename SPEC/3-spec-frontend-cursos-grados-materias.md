# Spec: Frontend de Cursos, Grados, Materias y Matrículas

**Owner:** Santiago
**Repo:** `Saanhevi/Sistema-de-seguimiento-academico`
**Complementa:** `spec-modulo-cursos-grados-materias.md` (el backend de este mismo dominio)
**Rama sugerida:**  `feat/cursos-grados-materias-frontend` ya se mergeó el backend a main.

---

## 0. Referencia visual: prototipo (ahora con código real)

Repo: `https://github.com/sn3hi/PrototipoSitioWebEducativo` (exportado del Figma Make original).

**Hallazgo importante — desalineación de stack:** el prototipo es una app React + TypeScript separada, con **Tailwind CSS y la librería de componentes shadcn/ui** (`accordion`, `dialog`, `table`, `tabs`, `select`, `sidebar`, `card`, iconos `lucide-react`, etc.). El `Frontend/` real del repo del equipo es React JS plano (sin TypeScript, sin Tailwind, sin librería de componentes), con CSS escrito a mano usando las variables de `variables.css`. **No copies código del prototipo tal cual** — tradúcelo a las convenciones de §3-§5.

**Buena noticia sobre la paleta:** `src/styles/theme.css` del prototipo usa exactamente los mismos colores de marca que ya están en `Frontend/src/styles/variables.css` del repo real (`#0ED9B5`, `#34A6AA`, `#111C1C`, `#F4F9F9`). No hay conflicto de paleta — solo tienes que usar las variables CSS existentes en vez de clases Tailwind.

**Archivos del prototipo directamente relevantes para este módulo:**

- `src/app/components/admin/AdminGrados.tsx` — es casi literalmente la historia "relacionar asignaturas con los grados". Patrón de UI a adaptar (no el código): selector de grado arriba, dos paneles lado a lado (izquierda: materias ya vinculadas a ese grado, con botón de desvincular; derecha: materias disponibles para agregar, con botón rápido de agregar), y una tabla-resumen abajo (materias × grados, con una marca en cada celda donde hay vínculo). Es un patrón de UX sólido y reutilizable para tu panel de Materias/Grados.
- `src/app/components/admin/AdminEstudiantes.tsx` — es la historia "asignar estudiantes a un grado académico". Patrón: chips de grado con contador de estudiantes arriba, filtro por grado, y una acción de asignar/reasignar por estudiante.
- `src/app/components/admin/AdminNav.tsx` + `AdminView.tsx` — confirma que la navegación por tabs (Resumen, Grados, Estudiantes, Docentes, Historial, Configuración) es un patrón ya validado — le da respaldo a la decisión del §5 de este spec de usar tabs en vez de subrutas.

**Divergencias de modelo de datos — no las copies sin decidirlas con el equipo:**

1. En el prototipo, el vínculo materia↔grado es directo (`{gradoNombre, asignaturaId, horasSemanales}`), **sin** necesitar un docente ni un período. En el backend real que ya especificaste, esa asociación solo existe a través de `Curso`, que **sí exige** `id_docente` e `id_periodo`. No puedes replicar el flujo de "agregar rápido" del prototipo tal cual — tu formulario de Curso necesita esos dos campos adicionales (aunque sea con el input de texto temporal del §6). Es un buen dato para la pregunta abierta 7.2 del backend, no algo que resolver aquí.
2. El prototipo maneja **secciones/paralelos** (grupos "A"/"B" dentro de un grado) y una entidad separada de **año escolar** (con fecha de inicio/fin, cuál está activo). **Ninguna de las dos existe en el esquema real** (`Matricula` no tiene columna `seccion`; no hay tabla de año escolar, solo el campo `anio` suelto y `PeriodoAcademico`). Es una idea razonable, pero es un cambio de esquema — no la agregues por tu cuenta en el frontend sin que el equipo decida si vale la pena para este sprint.

**Recomendación:** usa `AdminGrados.tsx` y `AdminEstudiantes.tsx` como referencia de layout/interacción, tradúcelos a componentes propios en `modules/cursos/components/` con las convenciones ya establecidas del repo real, y ajusta los campos a lo que tu backend realmente expone (sin secciones ni año escolar como entidades separadas, por ahora).

## 1. Objetivo

Construir la interfaz para que el Administrador gestione Grados, Materias, Períodos y Cursos, y matricule estudiantes en un grado — consumiendo los endpoints que definiste en el spec de backend.

## 2. Punto de partida (ya existe, no lo recrees)

- La ruta **`/dashboard/admin/cursos`** ya está registrada en `Frontend/src/routes/AppRouter.jsx` y apunta a `AdminCursos.jsx`.
- `Frontend/src/modules/dashboard/pages/admin/AdminCursos.jsx` **ya existe** como placeholder de Snehider:
  ```jsx
  export const AdminCursos = () => {
    return <div>AdminCursos</div>
  }
  ```
  ⚠️ **Es un export con nombre (`export const AdminCursos`), no un default export.** `AppRouter.jsx` lo importa como `import { AdminCursos } from "..."`. Si lo cambias a `export default`, rompes el router. Reemplaza el contenido de la función, no la forma de exportarla.
- No toques `AppRouter.jsx` ni `PortalAdmin.jsx` — el routing y el layout del panel admin ya están resueltos.

## 3. Cómo llamar al backend (patrón ya establecido, síguelo tal cual)

Ya existe una instancia de axios en `Frontend/src/services/api.js` que **inyecta el Bearer token automáticamente** en cada request (vía interceptor, leyendo `localStorage`). No manejes el token manualmente — solo usa esa instancia.

Sigue el mismo patrón de `Frontend/src/modules/auth/services/authService.js`:
```js
import api from "../../../services/api";

export async function listarGrados() {
  try {
    const response = await api.get("/api/grados");
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}
```

## 4. Estructura de archivos a crear

Sigue el patrón de módulo por dominio, igual que `modules/auth/`:

```
Frontend/src/modules/cursos/services/cursoService.js
  → un wrapper por cada endpoint del spec de backend (listarGrados, crearGrado,
    listarMaterias, crearMateria, listarPeriodos, crearPeriodo, listarCursos,
    crearCurso, listarMatriculas, crearMatricula, listarEstudiantesDeGrado)

Frontend/src/modules/cursos/components/GradoPanel.jsx      (form + lista de grados)
Frontend/src/modules/cursos/components/MateriaPanel.jsx    (form + lista de materias)
Frontend/src/modules/cursos/components/PeriodoPanel.jsx    (form + lista de períodos)
Frontend/src/modules/cursos/components/CursoPanel.jsx      (form + lista de cursos)
Frontend/src/modules/cursos/components/MatriculaPanel.jsx  (form + lista de matrículas)

Frontend/src/modules/dashboard/pages/admin/AdminCursos.jsx  (YA EXISTE — reemplazar el
  contenido para que componga los 5 paneles anteriores, ver §5)
```

## 5. Comportamiento de UI (MVP)

Dado que son 5 entidades en una sola página, usa **tabs simples** dentro de `AdminCursos.jsx` (no hace falta una librería nueva — con `useState` para saber cuál tab está activo alcanza, siguiendo el estilo simple que ya usa `LoginForm.jsx`). Cada tab renderiza su panel:

`Grados | Materias | Períodos | Cursos | Matrículas`

Cada panel es: un formulario simple arriba (los campos del endpoint POST correspondiente) + una lista/tabla abajo con lo que devuelve el GET. Después de crear un registro, refresca la lista (vuelve a llamar al GET o agrega el item al estado local).

**Para el panel de Cursos específicamente**, adapta el patrón de dos columnas de `AdminGrados.tsx` (§0): selector de grado a la izquierda, columna de "cursos ya creados para ese grado" (materia + docente + período, con opción de ver detalle) y columna de "crear nuevo curso" con el formulario completo (materia, docente, período — recordando que docente va como input de texto temporal, §6). No repliques `horasSemanales` ni conceptos de sección/año escolar (ver divergencias en §0).

**Para el panel de Matrículas**, adapta el patrón de chips + filtro de `AdminEstudiantes.tsx` (§0): chips por grado con contador de estudiantes matriculados, y una acción simple de asignar/reasignar. Sin secciones (A/B) — el esquema real no las tiene.

**Reutiliza estilos existentes**, no inventes un diseño nuevo desde cero:
- Envuelve cada panel con las clases `.panel`, `.panel-header`, `.panel-title` que ya existen en `styles/Dashboard.css`.
- Usa las variables de `styles/variables.css` (`--teal-brand`, `--border`, `--radius-md`, etc.) para cualquier CSS propio que necesites — no hardcodees colores.
- No existe todavía una clase genérica de formulario o tabla compartida en el proyecto (cada módulo hace la suya, ver `.login-form` en `Login.css` como ejemplo). Puedes crear tus propias clases con prefijo `.curso-` (ej. `.curso-form`, `.curso-tabla`) en un archivo nuevo `styles/Cursos.css`, e importarlo en `App.jsx` junto a los demás (`import "./styles/Cursos.css";`).

## 6. Bloqueo real a resolver (no es solo tuyo — llévalo al standup)

Los formularios de **Curso** (necesita `id_docente`) y **Matrícula** (necesita `id_estudiante`) deberían tener un selector (dropdown) de profesores/estudiantes reales. Hoy **no existe ningún endpoint que liste usuarios** — `UsuarioRepository` solo tiene `buscar_por_correo` y `buscar_por_id`, no un "listar por rol". Ese endpoint no es tuyo (cae en el módulo de Profesores de Samuel, y en gestión de Estudiantes, que hoy no tiene dueño claro).

**Decisión para no bloquearte:** por ahora, usa un input de texto simple para `id_docente` / `id_estudiante` (con placeholder tipo "ID del profesor" y una nota visible de "temporal"), y déjalo documentado como TODO para reemplazar por un `<select>` en cuanto exista el endpoint de listado. Menciónalo en el standup para que alguien lo tome.

## 7. Preguntas abiertas

1. ¿Confirmas que quieres tabs dentro de una sola página, o prefieres subrutas (`/dashboard/admin/cursos/grados`, etc.)? Con subrutas hay que tocar `AppRouter.jsx`, que hoy no es tuyo — coordínalo si cambias de opinión.
   RTA: Prefiero subrutas
2. ¿El backend ya está corriendo en paralelo o vas a mockear las respuestas mientras lo terminas? 
   RTA: Backend y frontend corren con docker compose
3. ¿El prototipo (`sn3hi/PrototipoSitioWebEducativo`) es solo referencia de UX, o el equipo quiere evaluar migrar todo el frontend a Tailwind+shadcn más adelante? (Ver §0 — no lo decidas solo, es una decisión de todo el equipo.)
   Referencia, evalua si es más fácil instalar tailwind
4. ¿Vale la pena agregar "secciones" (grupos A/B dentro de un grado) y una entidad de año escolar al esquema, inspirados en el prototipo? Es un cambio de esquema compartido — llévalo al standup, no lo agregues solo en el frontend (§0).
   RTA: No cambies el schema, mantén las reglas de negocio actuals.

## 8. Definition of Done

- [ ] Los 5 paneles (Grados, Materias, Períodos, Cursos, Matrículas) renderizan dentro de `AdminCursos.jsx` sin romper el export con nombre.
- [ ] Cada panel puede crear un registro y ver la lista actualizada, contra el backend real corriendo en Docker Compose.
- [ ] `AppRouter.jsx` y `PortalAdmin.jsx` no fueron modificados.
- [ ] Se reutilizan `.panel`/`.panel-header`/`.panel-title` y las variables de `variables.css`.
- [ ] El TODO de los selectores de docente/estudiante queda comentado en el código y mencionado en standup.
- [ ] Probado manualmente de punta a punta: crear grado → materia → período → curso → matricular estudiante, y verlos aparecer en cada lista.
- [ ] PR contra `develop` con al menos un review.
