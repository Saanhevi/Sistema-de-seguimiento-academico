# Sprint 2 — Asignación de tareas

**Equipo:** Santiago Cardenas, Samuel Herrera, Rafael Uribe, Laura Cadavid, Snehider Salas, Mariana Giraldo
**Metodología:** Scrumban
**Ya terminado antes de este sprint:** Login (autenticación con JWT, correo + contraseña, para los tres roles).

---

## 1. Módulos y responsables

| Persona | Módulo | Componente arquitectónico | Historias cubiertas |
|---|---|---|---|
| **Santiago** | Cursos, Grados, Materias (backend + frontend) | `CursoController` + `Servicio Cursos` | Relacionar asignaturas con grados · Asignar estudiantes a un grado académico |
| **Samuel** | Gestión de Profesores | `UsuarioController` + `Servicio Usuarios` | Agregar profesores al sistema |
| **Mariana** | 1) RBAC (infraestructura) 2) Registro de Calificaciones | `core/` (transversal) → luego `CalificacionController` + `Servicio Calificaciones` | Autenticación de request y control de acceso por rol · Cargar notas del periodo actual · Almacenar calificaciones por periodo y año |
| **Laura** | Cálculo de Promedios | `Servicio Calificaciones` (lógica) | Promedio por estudiante en una materia · Promedio grupal de la materia |
| **Snehider** | Consulta de Calificaciones | Vista Estudiante | Consultar calificaciones (materia, profesor, nota) · Consultar detalle de calificación (%, comentario, entrega) |
| **Rafael** | Gestión de Asistencia | `AsistenciaController` + `Servicio Asistencia` | Registrar inasistencias · Consultar inasistencias |

> **Cambio respecto al reparto original:** Snehider y Mariana intercambiaron tareas — Mariana tomó Registro de Calificaciones (originalmente de Snehider) y Snehider tomó Consulta de Calificaciones (originalmente de Mariana). RBAC se asignó después, sin dueño previo, y quedó con Mariana.

## 2. Orden de dependencias

```
Santiago (Cursos/Grados/Materias)
        │
        │  Curso es requisito de casi todo lo demás
        ▼
Mariana (RBAC) ──► Mariana (Registro de Calificaciones) ──┬──► Laura (Cálculo de Promedios)
                                                            └──► Snehider (Consulta de Calificaciones)

Samuel (Profesores) ────────────────────────────────────────────► autónomo, no bloquea ni es bloqueado
Rafael (Asistencia) ─────────────────────────────────────────────► depende solo de Curso (Santiago)
```

**Puntos clave:**
- **Santiago es el cuello de botella real.** `Curso` (materia + grado + docente + período) es la base de la que cuelgan Calificaciones y Asistencia. Mientras su módulo no esté mergeado a `develop`, los demás pueden avanzar con datos de prueba insertados directamente por SQL (las tablas ya existen en `Database/schemas.sql`, no dependen del código Python de Santiago).
- **Mariana es la segunda dependencia crítica.** Laura y Snehider necesitan que exista al menos el modelo de `Nota` para trabajar con datos reales — mientras tanto pueden avanzar con mocks.
- **RBAC no bloquea merges de otros módulos en este sprint.** Cada módulo documentó la protección de rol como TODO explícito; una vez Mariana lo termine, hay que volver a cada router y agregar `Depends(require_role(...))` — no pasa automáticamente, hay que agendarlo.
- **Samuel y Rafael son los más autónomos** y pueden avanzar sin esperar a nadie más (Rafael solo necesita una fila de prueba en `Curso`).

## 3. Specs técnicos disponibles

Cada módulo tiene un spec detallado (modelo de datos real, endpoints, reglas de negocio, estructura de archivos y Definition of Done) más un prompt listo para usar con un asistente de IA:

| Spec | Cubre |
|---|---|
| `spec-modulo-cursos-grados-materias.md` | Backend de Cursos/Grados/Materias (Santiago) |
| `spec-frontend-cursos-grados-materias.md` | Frontend de Cursos/Grados/Materias (Santiago), incluye referencia al prototipo de Figma Make |
| `spec-rbac.md` | RBAC — `get_current_user` + `require_role` en `core/` (Mariana) |
| `spec-registro-calificaciones.md` | Backend de Registro de Calificaciones (Mariana) |

*(Pendientes de escribir: specs de Profesores, Cálculo de Promedios, Consulta de Calificaciones y Asistencia — se pueden generar con el mismo formato cuando cada persona esté por arrancar.)*

## 4. Reglas de Git (recordatorio, ya están en el README principal)

1. `main` es el tronco protegido — nadie sube código ahí directamente.
2. Todo el desarrollo se integra en `develop`.
3. Rama por tarea desde `develop`, con prefijo `feat/` o `fix/` (ej. `feat/cursos-grados-materias`, `feat/rbac-core`, `feat/registro-calificaciones`).
4. PR contra `develop` con al menos un review antes de mergear.
