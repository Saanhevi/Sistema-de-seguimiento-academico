# Resumen de implementación — Registro de Calificaciones (spec-registro-calificaciones.md)

**Rama:** `feat/registro-calificaciones` (creada desde `main`)
**Estado:** Implementado, revisado con code review (xhigh, 9 ángulos + verificación + barrido), hallazgos corregidos y re-probado en vivo. Listo para PR con review.

---

## 1. Qué se implementó

Un commit por pieza, siguiendo la estructura de archivos de la sección 8 del spec:

| Commit | Archivo(s) | Contenido |
|---|---|---|
| `6e6594c` | `models/seccion_porcentaje.py`, `actividad_evaluativa.py`, `nota.py`, `models/__init__.py` | Modelos ORM con `relationship()` real hacia `Curso` (no FK como string), siguiendo el patrón `Mapped`/`mapped_column` del resto del proyecto. |
| `58c59d5` | `repositories/seccion_porcentaje.py`, `actividad_evaluativa.py`, `nota.py` | Un repository por entidad, mismo patrón que `CursoRepository`/`UsuarioRepository`. |
| `b089cbb` | `schemas/calificacion.py` | Todos los schemas Pydantic del dominio en un solo archivo. |
| `bdd01ae` | `services/calificacion.py` | `CalificacionService` con las validaciones RN-a a RN-f. |
| `532bdfa` | `routers/calificacion.py` | Router con `Depends(require_role(...))` en cada endpoint, según la tabla de §6a. |
| `de0d71d` | `core/dependencies.py`, `main.py` | `get_calificacion_service` + registro del router en la app. |
| `c68c377` | `tests/prueba_modulo_calificaciones.py` | Script manual: crea sección, actividad y carga notas para 3 estudiantes. |

No se tocó `routers/auth.py`, `services/auth.py` ni nada del módulo de Curso (reglas explícitas del pedido original).

## 2. Decisiones sobre las preguntas abiertas (§7)

**Pregunta 5 — ¿Un Estudiante puede leer notas de actividades que no son suyas vía `GET /api/notas`?**
Decisión inicial: **sí**, siguiendo el default del spec y el precedente del módulo de Curso (ninguno de los dos filtraba por pertenencia). Se documentó como punto para el standup.

**Esta decisión se revirtió después**, a pedido explícito: `GET /api/notas` ahora filtra por `id_estudiante` cuando quien llama tiene rol Estudiante — un estudiante autenticado solo ve sus propias notas, nunca las de sus compañeros (ver §4).

**Pregunta 2 — Duplicados en `Nota` (RN-f):** se implementó upsert silencioso (actualiza si ya existe una nota para ese estudiante+actividad), como sugería el spec. Ver §4 para el fix de la condición de carrera sobre este mismo mecanismo.

**Pregunta 1 (carga por lote vs. individual) y Pregunta 3 (promedios de Laura, "bajo demanda"):** sin cambios respecto a lo documentado originalmente — quedan como puntos a confirmar con el equipo, no bloquean esta pieza.

## 3. Hallazgos del code review y fixes aplicados

Después de la implementación inicial se corrió un `/code-review` a esfuerzo xhigh (9 ángulos de búsqueda + verificación 1-voto + barrido de huecos) contra el diff completo de la rama, con varios hallazgos **verificados en vivo contra el backend real** (no solo por lectura de código). Todos se corrigieron:

| Hallazgo | Commit del fix | Verificación |
|---|---|---|
| `carga-masiva` no era atómica: una fila inválida a mitad de lote dejaba las anteriores ya comiteadas | `f60ca2e` | Lote de 3 con el 3° inválido → 0 filas persistidas (antes quedaban 2 de 3) |
| `NaN` evadía la validación de `calificacion` y de `porcentaje` (comparaciones `<`/`>` son `False` para NaN) | `f60ca2e` | `calificacion:NaN` / `porcentaje:NaN` → 400 (antes: 200, guardaba `NaN` literal en BD) |
| `porcentaje` sin límite superior → overflow de `NUMERIC(5,2)` → 500 sin manejar | `f60ca2e` | `porcentaje=99999` → 400 (antes: 500 `NumericValueOutOfRange`) |
| `nombre_seccion`, `nombre` (actividad) y `comentario` sin `max_length` → overflow de `VARCHAR` → 500 | `a034380` | Textos >50/100 caracteres → 422 (antes: 500 `StringDataRightTruncation`) |
| Upsert de `Nota` (RN-f) era una condición de carrera (check-then-act sin constraint único) | `f60ca2e` | Serializado con `pg_advisory_xact_lock(id_actividad, id_estudiante)`, sin tocar el esquema |
| Aviso de RN-b (secciones que suman >100%) solo se imprimía en el servidor, invisible para la API | `a034380` / `f60ca2e` | Ahora viaja en el campo `advertencia` de `SeccionPorcentajeResponse` |
| `Nota.calificacion` / `SeccionPorcentaje.porcentaje` tipadas `float` pero devolvían `Decimal` en runtime | `782959f` | `asdecimal=False` en las columnas `Numeric`; confirmado `type(...)` ahora es `float` |
| `_validar_estudiante` no verificaba que existiera la fila `Estudiante` (solo el rol en `Usuario`) | `f005e1e` | Simulado un `Usuario` rol=Estudiante sin fila `Estudiante` → 400 (antes: 500 `IntegrityError`) |
| IDs (`id_curso`, `id_seccion`, `id_actividad`, `id_estudiante`) sin límite superior → overflow de `INTEGER` → 500 | `9746d05` | `id_curso=99999999999` y `id_curso=-5` → 422 en creación y en query params |
| Script de prueba no era idempotente (secciones/actividades duplicadas en cada corrida) | `37b469b` | Corrido dos veces seguidas: mismo `id_seccion`/`id_actividad` reutilizado |
| Lista vacía en carga-masiva | ya cubierto en `f60ca2e` | `notas: []` → 400 explícito |

## 4. Pertenencia (RN-03 y RN-04) — implementadas a pedido explícito

El diseño original dejaba RN-03/RN-04 fuera de alcance (igual que hizo RBAC con `require_role`). A pedido posterior se implementaron ambas, en `f60ca2e`:

- **RN-03:** un Docente que no dicta el curso recibe **403** al crear secciones, actividades o notas sobre él (`_validar_pertenencia_curso`, comparando `curso.id_docente` contra el usuario autenticado). Administrador no tiene esta restricción. Probado con un segundo docente contra un curso ajeno: 403 en los 3 endpoints de escritura.
- **RN-04:** `GET /api/notas` filtra por `id_estudiante` cuando quien llama es Estudiante. Probado: un estudiante ve 1 de 3 notas (la suya), el docente dueño sigue viendo las 3.
- **Alcance:** la pertenencia de RN-04 solo se aplicó a `GET /api/notas` (lo pedido explícitamente). `GET /api/secciones` y `GET /api/actividades` siguen sin filtrar por matrícula del estudiante — no se pidió y requeriría cruzar contra `Matricula`/`Grado`/`anio`, más complejo que lo solicitado.

## 5. Pruebas realizadas

Todo contra la BD y el backend reales de `docker compose` (no solo `pytest`/mocks):

- Flujo completo de punta a punta vía `app/tests/prueba_modulo_calificaciones.py`, corrido dos veces para confirmar idempotencia.
- Los 6 escenarios de RBAC ya cubiertos por el spec de calificaciones (200 válido, 401 sin token, 403 rol equivocado, RN-a a RN-f) probados vía `curl` contra el backend containerizado.
- Los 11 hallazgos de la tabla de §3, cada uno reproducido **antes** del fix (confirmando el bug) y re-probado **después** (confirmando el fix), incluyendo inspección directa de la BD (`psql`) y de los logs del backend para los errores 500 originales.
- RN-03 y RN-04 probados con un segundo usuario Docente (no dueño del curso) y con un token de Estudiante real.

## 6. Pendientes / qué comunicar al equipo

- **No existe rama `develop`** en el remoto (solo `main`, igual que en `feat/rbac-core`). Se creó `feat/registro-calificaciones` desde `main`; falta decidir contra qué rama abrir el PR.
- **PR requiere al menos un review** (DoD del spec) — no se abrió todavía.
- **Extensión 6b** (`PUT`/`DELETE /api/notas/{id_nota}`) sigue fuera de alcance de este sprint, tal como indica el spec.
- **Con Laura (promedios):** sigue sin coordinar si su servicio consulta `Nota` bajo demanda o espera un trigger del servicio de Calificaciones — asumido "bajo demanda", no se implementó ningún disparador.
- **Con el equipo, sobre RN-04:** el filtro de pertenencia solo se aplicó a notas, no a secciones/actividades. Si se quiere extender, hace falta cruzar `Curso` contra `Matricula` del estudiante (por `Grado` + año), que es una regla más compleja que la implementada aquí.
- **Datos de prueba en la BD de docker compose:** quedaron varias secciones y actividades de prueba en el curso 1 (creadas durante la verificación de los fixes), incluyendo una sección con `porcentaje` que hace que la suma del curso supere ampliamente el 100% — es solo para evidenciar el aviso de RN-b, no afecta producción.
