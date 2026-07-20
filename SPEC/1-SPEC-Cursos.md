# Spec: Módulo de Cursos, Grados y Materias

**Owner:** Santiago
**Repo:** `Saanhevi/Sistema-de-seguimiento-academico`
**Componente arquitectónico:** `CursoController` + `Servicio Cursos` (ver `Arquitectura_del_software.pdf`)
**Rama sugerida:** `feat/cursos-grados-materias` (desde `develop`, según reglas de Git del README)

---

## 1. Objetivo

Construir el backend para gestionar la estructura académica base (Grados, Materias, Períodos y Cursos) y la matrícula de estudiantes en un grado. Este módulo es una **dependencia bloqueante**: sin él, ni el registro de calificaciones (Snehider) ni la asistencia (Rafael) tienen dónde "colgar" sus datos, porque `Nota` → `ActividadEvaluativa` → `SeccionPorcentaje` → `Curso`, y `HistorialAsistencia` → `DiaAsistible` → `Curso` también.

## 2. Historias de usuario cubiertas

- Como administrador del colegio, quiero relacionar las asignaturas con los grados en los que se cursan, para organizar correctamente la estructura académica.
- Como administrador del colegio (ver nota en §7), quiero asignar estudiantes a un grado académico, para mantener actualizada la organización de los grupos.
- (Soporte implícito) RF-05 y RF-06 de `docs/Requerimientos funcionales y no funcionales.md`: crear/gestionar cursos, grados y materias; asignar materias a profesores y estudiantes a cursos.

## 3. Fuera de alcance (explícitamente)

- Frontend / Vista de Gestión Académica (coordinar con quien lleve esa vista).
- Enforcement estricto de roles (RBAC) — hoy no existe una dependencia `get_current_user` reusable en `app/core/dependencies.py`, solo el login. Para este sprint los endpoints quedan **sin protección de rol** (se documenta como deuda técnica, ver §8). Si Santiago quiere resolverlo ya, es un plus, no un bloqueante.
- Promoción automática de estudiantes al siguiente grado (RF-07) — futuro sprint.
- Cierre/bloqueo de período (RF-08/RN-01/RN-02) — solo se modela el campo `estado` de `PeriodoAcademico`, la lógica de bloqueo de notas la implementa quien construya Calificaciones.

## 4. Modelo de datos (ya existe en `Database/schemas.sql`, no se modifica el esquema)

```sql
Grado(id_grado PK, nombre)
Materia(id_materia PK, nombre)
PeriodoAcademico(id_periodo PK, nombre, anio, estado ['Abierto'|'Cerrado'])
Curso(id_curso PK, id_docente FK->Docente, id_grado FK->Grado,
      id_materia FK->Materia, id_periodo FK->PeriodoAcademico)
Matricula(id_matricula PK, id_estudiante FK->Estudiante, id_grado FK->Grado, anio)
```

**Punto importante para validar con el equipo:** `Materia` no tiene `grado_id` propio. La "asociación materia–grado" del RF-05 se materializa creando un registro en `Curso` (que además exige un docente y un período ya existentes). Es decir, no existe un endpoint de "asociar materia a grado" aislado; se hace al crear un `Curso`. Si el equipo prefiere una tabla de asociación directa `Materia–Grado` independiente del dictado real, es un cambio de esquema que hay que acordar antes de programar (ver §7).

## 5. Reglas de negocio

| Regla | Descripción |
|---|---|
| RN-a | `nombre` de Grado y Materia no vacío. |
| RN-b | Al crear `Curso`: `id_docente` debe existir y corresponder a un usuario con rol `Docente`; `id_grado`, `id_materia`, `id_periodo` deben existir. |
| RN-c | No se permite crear un `Curso` duplicado (misma combinación docente+grado+materia+periodo). |
| RN-d | Al crear `Matricula`: `id_estudiante` debe existir con rol `Estudiante`; `id_grado` debe existir. |
| RN-e | Un estudiante no debería tener dos matrículas activas en el mismo `anio` (la tabla no tiene constraint único — validarlo en el service). |
| RN-f (RN-06 del doc técnico) | Toda materia debe terminar asociada a al menos un grado a través de un `Curso`; no es un constraint de BD, es una regla a comunicar al frontend/admin. |

## 6. Endpoints

Prefijo sugerido: `/api` (mismo estilo que `auth_router`, que usa `prefix="/api/auth"`).

| Método | Ruta | Body | Descripción |
|---|---|---|---|
| POST | `/api/grados` | `{nombre}` | Crear grado |
| GET | `/api/grados` | — | Listar grados |
| POST | `/api/materias` | `{nombre}` | Crear materia |
| GET | `/api/materias` | — | Listar materias |
| POST | `/api/periodos` | `{nombre, anio, estado}` | Crear período académico |
| GET | `/api/periodos` | — | Listar períodos |
| POST | `/api/cursos` | `{id_docente, id_grado, id_materia, id_periodo}` | Crear curso (= "asociar materia a grado" + "asignar materia a profesor") |
| GET | `/api/cursos` | query opcional: `id_docente`, `id_grado`, `id_periodo` | Listar cursos con filtros |
| GET | `/api/cursos/{id_curso}` | — | Detalle de un curso |
| POST | `/api/matriculas` | `{id_estudiante, id_grado, anio}` | Matricular estudiante a un grado ("asignar estudiante a grado académico") |
| GET | `/api/matriculas?id_grado=&anio=` | — | Listar matrículas filtradas |
| GET | `/api/grados/{id_grado}/estudiantes?anio=` | — | Estudiantes matriculados en ese grado/año (helper que necesitarán Rafael y Snehider) |

Respuestas: siempre JSON vía schema Pydantic con `model_config = ConfigDict(from_attributes=True)`, igual que se hará para el resto del proyecto (en `schemas/auth.py` los schemas son de request/response simples, pero para entidades ORM usar `from_attributes`).

## 7. Preguntas abiertas para validar con el equipo antes/mientras se programa

1. La historia dice "**profesor** asigna estudiantes a un grado", pero RF-05/06 lo describen como tarea de **administrador**. Confirmar quién llama a `POST /api/matriculas` en el frontend — no cambia el backend, pero si luego se agrega RBAC, define qué rol se exige.
RTA: profesor y administrador pueden asignar estudiantes. RBAC: Estará encargado a Mariana.
2. ¿Se acepta que "materia–grado" se resuelva únicamente a través de `Curso` (como está en el schema actual), o se prefiere una tabla de asociación directa? Si es lo segundo, es un cambio de esquema compartido — coordinarlo antes de tocar `Database/schemas.sql`.
RTA: Mantener el esquema actual.
3. `PeriodoAcademico` no tiene owner claro en el reparto de tareas (RF-09). Este spec asume que Santiago lo construye mínimamente porque `Curso` lo necesita como FK. Confirmar en standup que nadie más lo está haciendo en paralelo.
RTA: Santiago lo hace (yo)

## 8. Estructura de archivos a crear (siguiendo el patrón ya usado en `auth`)

```
Backend/app/models/grado.py
Backend/app/models/materia.py
Backend/app/models/periodo_academico.py
Backend/app/models/curso.py
Backend/app/models/matricula.py
Backend/app/models/__init__.py        (agregar los nuevos imports)

Backend/app/repositories/grado.py
Backend/app/repositories/materia.py
Backend/app/repositories/periodo_academico.py
Backend/app/repositories/curso.py
Backend/app/repositories/matricula.py

Backend/app/schemas/curso.py          (todos los schemas de este dominio en un solo archivo)

Backend/app/services/curso.py         (una sola clase CursoService, igual que "Servicio Cursos" en la arquitectura)

Backend/app/routers/curso.py          (un router, agrupa /grados, /materias, /periodos, /cursos, /matriculas)

Backend/app/core/dependencies.py      (agregar get_curso_service, mismo patrón que get_auth_service)
Backend/app/main.py                   (agregar app.include_router(curso_router))
```

## 9. Definition of Done

- [ ] Los 5 modelos ORM creados y agregados a `models/__init__.py`, sin romper `auth`.
- [ ] Los 12 endpoints funcionando y documentados en `/docs` (Swagger, igual que login).
- [ ] Validaciones de RN-a a RN-e implementadas en el service (no en el router).
- [ ] Probado manualmente contra la BD de Docker Compose (crear grado → materia → período → curso → matricular estudiante → listar estudiantes del grado).
- [ ] Al menos un script de prueba en `app/tests/`, siguiendo el estilo de `prueba_conexion_db.py`.
- [ ] PR contra `develop` con al menos un review, según reglas del README.
