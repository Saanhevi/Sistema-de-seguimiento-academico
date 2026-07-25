# Resumen de implementación — Spec 7 (Frontend de calificaciones)

**Rama:** `feat/frontend-calificaciones` (desde `main`)
**Spec:** [`7-spec-frontend-calificaciones.md`](7-spec-frontend-calificaciones.md)
**Fecha:** 2026-07-23

---

## Commits

| Hash | Tipo | Contenido |
|---|---|---|
| `a2753fd` | `fix(backend)` | BE-1 a BE-4 de §0.5 del spec |
| `ebde891` | `feat(frontend)` | Módulo de calificaciones + vistas docente y estudiante + §13 del spec |

Los cambios de backend van en su propio commit, como sugiere §0.5 del spec.

---

## 1. Backend (commit `a2753fd`)

### BE-1 — `id_usuario` en el login 🔴
- `Backend/app/schemas/auth.py` → `TokenResponse` ahora incluye `id_usuario: int`.
- `Backend/app/services/auth.py` → `autenticar_usuario` lo agrega al dict de retorno.

Desbloquea `GET /api/cursos?id_docente=`, o sea todo el flujo del docente.

### BE-2 — `CursoResponse` enriquecido 🟡
- `Backend/app/schemas/curso.py` → campos anidados opcionales `grado`, `materia`, `periodo`.
- `Backend/app/repositories/curso.py` → helper `_con_relaciones()` con `joinedload`, aplicado tanto en `listar()` como en `buscar_por_id()`.

**Desviación menor respecto al spec:** el spec solo pedía `joinedload` en `listar()`. Se aplicó también en `buscar_por_id()` porque `GET /api/cursos/{id_curso}` usa el mismo `CursoResponse` y habría hecho 3 queries extra al serializar los anidados.

Con esto el selector de cursos arma `"Matemáticas · 3°A · Primer Periodo"` en **una sola llamada**, y el banner de periodo lee `curso.periodo.estado` sin pegarle a `/api/periodos`.

### BE-3 — Filtro `id_estudiante` en matrículas 🔴
- `Backend/app/repositories/matricula.py` → `listar()` acepta `id_estudiante`.
- `Backend/app/services/curso.py` → `listar_matriculas()` recibe `usuario_actual` y **fuerza** el filtro cuando el rol es Estudiante (misma regla de pertenencia RN-04 que ya aplica `listar_notas`).
- `Backend/app/routers/curso.py` → expone el query param y pasa el usuario.

Desbloquea el bootstrap de la vista del estudiante (descubrir su grado).

### BE-4 — Bug: la fila `Estudiante` nunca se guardaba 🔴
- `Backend/app/services/auth.py` → `crear_cuenta_estudiantil` llama a `self.repositorio_estudiante.crear_estudiante(estudiante)`.

Sin esto, un estudiante registrado desde la app no aparecía en la tabla de notas del docente (`listar_estudiantes_por_grado` hace `JOIN Estudiante`) y cargarle una nota devolvía 400 (`_validar_estudiante`).

> Es un bug preexistente ajeno a este spec. Va bundleado en el commit de backend; si en el review prefieren separarlo, es un `git cherry-pick` de esas 1 línea.

**Verificación:** `python -m compileall` sobre los 7 archivos tocados **más una suite de tests nueva** (ver §4) que cubre BE-1 a BE-4 y las reglas de negocio del módulo, tanto unitaria como de integración end-to-end.

---

## 2. Frontend (commit `ebde891`)

### Archivos nuevos

```
Frontend/src/modules/calificaciones/
  services/calificacionService.js     <- wrappers de todos los endpoints
  utils/notas.js                      <- claseBadge, formatearNota, promedios
  utils/cursos.js                     <- etiquetaCurso
  components/
    SelectorCurso.jsx
    EstadoPeriodo.jsx
    SeccionPanel.jsx
    ActividadModal.jsx
    TablaNotas.jsx
    CargaMasivaModal.jsx

Frontend/src/modules/dashboard/pages/estudiante/EstudianteCalificaciones.jsx
Frontend/src/styles/Calificaciones.css
```

### Archivos modificados

| Archivo | Cambio |
|---|---|
| `models/Usuario.js` | `crearUsuario` propaga `id_usuario` |
| `context/AuthContext.jsx` | `login()` recibe y guarda `id_usuario` |
| `App.jsx` | importa `Calificaciones.css` |
| `routes/AppRouter.jsx` | ruta `/dashboard/estudiante/calificaciones` |
| `components/Navbar.jsx` | enlace "Mis Calificaciones" para el rol Estudiante |
| `pages/docente/DocenteCalificaciones.jsx` | reescrito, sin datos hardcodeados |

**No se tocaron** `PortalDocente.jsx` ni `PortalAdmin.jsx`, como pide §10.

### Decisiones de diseño

1. **Las actividades se cargan una sola vez, en la vista padre.** El spec dejaba que `SeccionPanel` listara actividades y que `TablaNotas` las volviera a pedir como columnas. En su lugar `DocenteCalificaciones` es el único que llama a `GET /api/actividades` y las pasa por prop a los dos. Una llamada en vez de dos, y ambos componentes siempre muestran lo mismo.

2. **`etiquetaCurso` vive en `utils/cursos.js`**, no exportada desde `SelectorCurso.jsx`. Un archivo de componente que exporta funciones sueltas rompe el Fast Refresh (`react-refresh/only-export-components`) — es exactamente el error que arrastra `AuthContext.jsx` (ver §13 del spec, grupo E).

3. **`SeccionPanel` sirve a los dos roles.** Con `readOnly` esconde los formularios de creación; con `notaPorActividad` muestra la nota del estudiante junto a cada actividad. La vista del estudiante lo monta una vez por curso dentro de su propio acordeón.

4. **`listarEstudiantesDeGrado` se reexporta desde `cursoService.js`**, no se duplica (§4 del spec).

5. **`anio` se pasa a `GET /api/grados/{id}/estudiantes`.** Sale de `curso.periodo.anio`. Sin él, un estudiante matriculado en varios años aparecería repetido en la tabla.

6. **Efectos sin `setState` síncrono.** Los estados de carga arrancan en `true` y solo se escriben desde callbacks asíncronos, con flag `vigente` en el cleanup para no escribir sobre un componente desmontado. Es lo que exige `react-hooks/set-state-in-effect`, la regla que revienta en el resto del repo (§13).

7. **`key` para remontar en vez de sincronizar por efecto.** `SeccionPanel` lleva `key={curso.id_curso}` y `TablaNotas` `key={curso-seccion}`: al cambiar de curso o sección el componente se remonta limpio, sin efectos de reseteo.

---

## 3. Sección 13 del spec — deuda de lint

Se agregó al spec un inventario de los **10 errores y 2 warnings** de `npm run lint` que ya venían fallando en `main`, agrupados en 5 patrones con su fix:

- **A** — carga inicial con `setState` síncrono en `useEffect` (5 archivos de `modules/cursos/`).
- **B** — reset de estado en la rama `else` de un efecto (`CursoPanel`, `MatriculaPanel`).
- **C** — `ProfesorModal` sincroniza props a state (fix: `key` + render condicional).
- **D** — `import React` muerto en `EstudianteAsignaturas.jsx`.
- **E** — `AuthContext.jsx` exporta el hook `useAuth` junto al provider (fix: archivo aparte, 8 imports a actualizar).

Con orden sugerido y DoD propio. **Va en un PR de `chore` separado**, no mezclado con esta feature.

---

## 4. Estado de verificación

| Check | Estado |
|---|---|
| `npm run build` | ✅ pasa |
| `npm run lint` | ✅ 10 errores / 2 warnings — **uno menos que el baseline de `main`** (11/2), y ninguno en archivos nuevos |
| `python -m compileall` backend | ✅ pasa |
| Tests unitarios backend | ✅ 24 tests (`unittest`, con dobles, sin BD) |
| Flujo end-to-end contra Docker Compose | ✅ 7 tests de integración por HTTP contra el backend levantado |

### Tests agregados (`Backend/app/tests/`)

Todo con `unittest` de la stdlib (el repo no tiene `pytest` ni `httpx`); la integración usa `urllib`.

| Archivo | Tipo | Cubre |
|---|---|---|
| `test_auth_service.py` | unit | BE-1/BE-4: `id_usuario` en el login, `TokenResponse`, creación de la fila `Estudiante` |
| `test_curso_calificaciones.py` | unit | BE-2: anidados de `CursoResponse`. BE-3: filtro por estudiante + RN-04 |
| `test_calificacion_service.py` | unit | RN-03, RN-a (rango 0–5), RN-b (porcentaje/aviso), RN-d, RN-04 |
| `test_calificaciones_integracion.py` | integración | Flujo completo Admin→Docente→Estudiante por HTTP + RN-03 y RN-d extremo a extremo |

La integración crea sus propios datos (usa un año libre ≤ 2100) y los borra en `tearDownClass`, así que es repetible y no deja residuo. Se salta sola si el backend no responde en `CALIF_BASE_URL` (default `http://localhost:8000`).

```bash
# unitarios (no requieren nada levantado)
cd Backend && .venv/Scripts/python.exe -m unittest app.tests.test_auth_service app.tests.test_curso_calificaciones app.tests.test_calificacion_service
# integración (requiere docker-compose up + BD sembrada)
cd Backend && .venv/Scripts/python.exe -m unittest app.tests.test_calificaciones_integracion
```

---

## 5. Pendiente

### DoD del backend (§11 del spec) — cubierto por la integración

Los 7 tests de `test_calificaciones_integracion.py` recorren el flujo con el backend levantado y verifican, del lado servidor:

- [x] Seleccionar curso → sección → actividades → cargar nota individual → verificar en `GET /api/notas`.
- [x] `POST /api/notas/carga-masiva` (upsert sin duplicar).
- [x] Periodo cerrado bloquea el registro de notas (400).
- [x] RN-03 (docente ajeno → 403) y RN-04 (estudiante ve solo lo suyo).

### Falta la verificación **de UI** (manual, en el navegador)

Los tests cubren la API, no el render. Queda comprobar a mano en la app:

- [ ] Celdas con candado y botones ocultos cuando el periodo está cerrado.
- [ ] Aviso visible cuando una sección trae `advertencia` (porcentajes > 100%).
- [ ] La carga masiva desde `CargaMasivaModal` con al menos 3 estudiantes.

La BD de Docker ya quedó sembrada con los usuarios de `creacion_usuarios.py`; para más datos hay scripts en `Backend/app/tests/seed_datos_curso.py`.

### Ojo al probar

**Las sesiones abiertas antes de BE-1 no tienen `id_usuario`** en localStorage. Ambas vistas detectan el caso y muestran "cierra sesión y vuelve a iniciarla", pero hay que hacerlo o parecerá que la vista está rota.

### Para el standup

- BE-4 es un bug ajeno a este spec y toca `services/auth.py` — coordinar con quien mantiene `auth`.
- BE-2 y BE-3 son módulos de Santiago (cursos/matrículas) — pedirle review de esos tres archivos.
- La ruta nueva toca `AppRouter.jsx` — confirmar que no pisa PRs abiertos.
- Con Laura: el promedio ponderado usa el `porcentaje` de la **sección**, no de la actividad (las actividades no tienen porcentaje en el backend real). Confirmar que su cálculo usa la misma fórmula.
- Proponer meter `npm run lint` al CI una vez saldada la deuda de §13.

### Falta el PR

Rama publicada con `git push -u origin feat/frontend-calificaciones`. Queda abrir el PR contra `main` con al menos un review, según el README.
