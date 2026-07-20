# Spec: Módulo de Registro de Calificaciones

**Owner:** Mariana (intercambio con Snehider — Mariana toma Registro, Snehider toma Consulta)
**Repo:** `Saanhevi/Sistema-de-seguimiento-academico`
**Componente arquitectónico:** `CalificacionController` + `Servicio Calificaciones` (ver `Arquitectura_del_software.pdf`)
**Rama sugerida:** `feat/registro-calificaciones` (desde `main`)

---

## 1. Objetivo

Permitir que un profesor registre calificaciones para sus cursos: define cómo se reparte el porcentaje de la nota final (secciones), crea actividades evaluables dentro de esas secciones, y carga la calificación de cada estudiante por actividad. Este módulo alimenta directamente el trabajo de Laura (cálculo de promedios) y Snehider (consulta de calificaciones) — sin esto, ninguno de los dos tiene datos reales sobre los que trabajar.

## 2. Historias de usuario cubiertas

- Como profesor, quiero cargar notas para el periodo académico actual, para evaluar el desempeño de los estudiantes.
- Como administrador del colegio, quiero que el sistema almacene las calificaciones por periodo y año escolar, para conservar el historial académico de los estudiantes.

## 3. Fuera de alcance (explícitamente, para este sprint)

- Modificar y eliminar notas ya cargadas (RF-10 lo pide, pero no estaba en las 2 historias asignadas). Se documentan como extensión natural en §6b — Hace parte del sprint 3
- Importación masiva desde Excel (RF-11) — el endpoint de carga masiva que se define aquí (§6) es el mismo que después recibiría las filas ya parseadas de un Excel, así que estás dejando la puerta abierta sin construirlo ahora.
- Bloqueo de edición cuando el período está cerrado (RN-02) más allá de la validación básica en creación (RN-01, sí incluida).
- Recalcular promedios automáticamente al guardar una nota (RN-08) — es responsabilidad del servicio de Laura. Coordina con ella si su cálculo va a ser "bajo demanda" (ella consulta `Nota` cuando la piden) o si espera que tu servicio dispare algo — con "bajo demanda" no necesitas hacer nada extra.
- La validación de *pertenencia* de RN-03 (que el docente sea específicamente el dueño de ese curso, no solo tener rol Docente) — eso va más allá de lo que `require_role` resuelve (ver §6). `require_role` sí es obligatorio desde ya para todos los endpoints.

## 4. Modelo de datos (ya existe en `Database/schemas.sql`, no se modifica el esquema)

```sql
SeccionPorcentaje(id_seccion PK, nombre_seccion, porcentaje NUMERIC(5,2), id_curso FK->Curso)
ActividadEvaluativa(id_actividad PK, nombre, fecha, id_seccion FK->SeccionPorcentaje)
Nota(id_nota PK, id_actividad FK->ActividadEvaluativa, id_estudiante FK->Estudiante,
     calificacion NUMERIC(3,2), comentario VARCHAR(100))
```

**Cadena de dependencia:** `Nota` → `ActividadEvaluativa` → `SeccionPorcentaje` → `Curso`. El período académico y el docente no están directamente en esta cadena — se llega a ellos a través de `Curso` (`id_periodo`, `id_docente`).

> **Actualización — el módulo de Curso ya está mergeado (PR #5, 20 jul 2026).** Ya no hace falta insertar filas de prueba por SQL: `Backend/app/models/curso.py`, `app/repositories/curso.py` y `app/services/curso.py` existen y funcionan. Usa el modelo `Curso` real con un `relationship()` normal (`ForeignKey("curso.id_curso")` + `relationship("Curso")`), en vez del workaround de FK como string sin relación que este spec sugería antes. Para probar de punta a punta, crea un curso real vía `POST /api/cursos` (como Administrador o Docente) en lugar de insertarlo a mano.

**RBAC ya está disponible — úsalo desde el día uno, no como TODO.** `core/dependencies.py` ya tiene `require_role`, y `routers/curso.py` (mergeado) es el ejemplo real de cómo se usa: `usuario = Depends(require_role("Administrador", "Docente"))` en cada endpoint. Todos los endpoints de este spec (§6) deben protegerse así — ver el detalle de qué rol va en cada uno más abajo.

## 5. Reglas de negocio

| Regla | Descripción |
|---|---|
| RN-a | `calificacion` debe estar entre 0.00 y 5.00 (la columna permite hasta 9.99, la regla de negocio la limita a 5). |
| RN-b | Al crear `SeccionPorcentaje`: `id_curso` debe existir. (Opcional/recomendado: avisar si la suma de porcentajes de las secciones de un curso supera 100%, sin bloquear — es una validación de calidad, no un constraint duro.) |
| RN-c | Al crear `ActividadEvaluativa`: `id_seccion` debe existir. |
| RN-d (RN-01 del doc técnico) | Solo se pueden crear/cargar notas si el período del curso (`Curso.id_periodo` → `PeriodoAcademico.estado`) está `'Abierto'`. |
| RN-e | `id_estudiante` en una `Nota` debe existir y tener rol `Estudiante`. |
| RN-f | La tabla `Nota` **no tiene** constraint único sobre `(id_actividad, id_estudiante)` — un estudiante podría terminar con dos notas para la misma actividad si no se valida en el service. Al hacer carga masiva, decide y documenta el comportamiento: ¿rechazar duplicados o actualizar (upsert)? Sugerencia: upsert, porque "cargar notas" normalmente se hace más de una vez mientras el profesor corrige. |

## 6. Endpoints

Prefijo sugerido: `/api` (mismo estilo que `auth_router`).

### 6a. MVP (cubre las 2 historias asignadas)

Todos usan `Depends(require_role(...))`, mismo patrón que `routers/curso.py` (ya mergeado) — no lo dejes como TODO.

| Método | Ruta | Rol requerido | Body | Descripción |
|---|---|---|---|---|
| POST | `/api/secciones` | `Administrador`, `Docente` | `{nombre_seccion, porcentaje, id_curso}` | Crear sección de porcentaje de un curso |
| GET | `/api/secciones?id_curso=` | `Administrador`, `Docente`, `Estudiante` | — | Listar secciones de un curso |
| POST | `/api/actividades` | `Administrador`, `Docente` | `{nombre, fecha, id_seccion}` | Crear actividad evaluativa dentro de una sección |
| GET | `/api/actividades?id_seccion=` | `Administrador`, `Docente`, `Estudiante` | — | Listar actividades de una sección |
| POST | `/api/notas` | `Administrador`, `Docente` | `{id_actividad, id_estudiante, calificacion, comentario?}` | Registrar la nota de un estudiante en una actividad |
| POST | `/api/notas/carga-masiva` | `Administrador`, `Docente` | `{id_actividad, notas: [{id_estudiante, calificacion, comentario?}, ...]}` | **El endpoint principal de "cargar notas"** — registra/actualiza (upsert) las notas de varios estudiantes de una actividad en una sola llamada |
| GET | `/api/notas?id_actividad=` | `Administrador`, `Docente`, `Estudiante` | — | Listar notas cargadas para una actividad (para verificar la carga) |

*(`Estudiante` puede leer — RN-04 dice que solo debe ver lo suyo, pero esa restricción de pertenencia es más fina que `require_role` y no es responsabilidad de este módulo, ver §3. Por ahora un estudiante autenticado puede leer notas de cualquier actividad vía estos GET; si eso te incomoda para el sprint, dilo en el standup.)*

### 6b. Extensión natural (opcional, si sobra tiempo)

| Método | Ruta | Body | Descripción |
|---|---|---|---|
| PUT | `/api/notas/{id_nota}` | `{calificacion?, comentario?}` | Modificar una nota individual |
| DELETE | `/api/notas/{id_nota}` | — | Eliminar una nota |

## 7. Preguntas abiertas para validar con el equipo antes/mientras se programa

1. ¿"Cargar notas" en el frontend será siempre por lote (toda la clase de una vez, vía `/carga-masiva`) o también hace falta cargar una sola nota puntual? Ambos endpoints están definidos (§6a), pero vale confirmar cuál usa el frontend como flujo principal, sobre todo si tú misma vas a construir esa vista más adelante.
2. Duplicados en `Nota` (RN-f): confirma con el equipo si el service debe hacer upsert silencioso o rechazar con error si ya existe una nota para ese estudiante+actividad.
3. Con Laura: ¿su servicio de promedios consulta `Nota` bajo demanda, o espera que el servicio de Calificaciones dispare algo al guardar? Si es bajo demanda (lo más simple), no necesitas coordinar nada más por ahora.
4. ~~Con Santiago: mientras su `Curso` no esté mergeado...~~ **Resuelto** — el módulo de Curso ya está en `develop`/`main`. Usa sus endpoints reales para crear datos de prueba.
5. ¿Un estudiante debería poder leer notas de actividades que no son suyas vía `GET /api/notas`? Hoy el spec lo permite (solo exige rol `Estudiante`, no pertenencia) — decide si es aceptable para este sprint o si vale la pena una validación adicional en el service (comparar `id_estudiante` de la nota contra el usuario autenticado).

## 8. Estructura de archivos a crear (siguiendo el patrón ya usado en `auth`)

```
Backend/app/models/seccion_porcentaje.py
Backend/app/models/actividad_evaluativa.py
Backend/app/models/nota.py
Backend/app/models/__init__.py        (agregar los nuevos imports)

Backend/app/repositories/seccion_porcentaje.py
Backend/app/repositories/actividad_evaluativa.py
Backend/app/repositories/nota.py

Backend/app/schemas/calificacion.py   (todos los schemas de este dominio en un solo archivo)

Backend/app/services/calificacion.py  (una sola clase CalificacionService, igual que "Servicio Calificaciones")

Backend/app/routers/calificacion.py   (un router, agrupa /secciones, /actividades, /notas)

Backend/app/core/dependencies.py      (agregar get_calificacion_service, mismo patrón que get_auth_service)
Backend/app/main.py                   (agregar app.include_router(calificacion_router))
```

## 9. Definition of Done

- [ ] Los 3 modelos ORM creados y agregados a `models/__init__.py`, sin romper `auth` ni ningún otro módulo.
- [ ] Los endpoints de §6a funcionando, protegidos con `require_role` según la tabla, y documentados en `/docs` (Swagger).
- [ ] Validaciones RN-a a RN-f implementadas en el service (no en el router).
- [ ] `carga-masiva` probado con al menos 3 estudiantes en una misma llamada.
- [ ] Probado manualmente de punta a punta contra la BD de Docker Compose (crear sección → actividad → cargar notas → listarlas).
- [ ] Al menos un script de prueba en `app/tests/`, siguiendo el estilo de `prueba_conexion_db.py`.
- [ ] PR contra `develop` con al menos un review, según reglas del README.
