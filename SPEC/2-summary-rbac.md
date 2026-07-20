# Resumen de implementación — RBAC (spec-rbac.md)

**Rama:** `feat/rbac-core` (creada desde `main`; el spec sugiere `develop` — falta rebase, ver "Pendientes")
**Estado:** Implementado y probado manualmente. Listo para PR con review.

---

## 1. Qué se implementó

Un commit por pieza, siguiendo el diseño técnico de la sección 4 del spec:

| Commit | Archivo | Contenido |
|---|---|---|
| `9f5e9c5` | `Backend/app/core/security.py` | `decode_access_token`: decodifica el JWT y maneja explícitamente `jwt.ExpiredSignatureError` / `jwt.InvalidTokenError`. |
| `6d51c93` | `Backend/app/core/dependencies.py` | `security_scheme` (`HTTPBearer`) + `get_current_user`: decodifica el token, reutiliza `UsuarioRepository.buscar_por_id`, valida `estado` para Docente/Estudiante. |
| `8f3db8b` | `Backend/app/core/dependencies.py` | `require_role(*roles_permitidos)`: dependency factory con la firma exacta del spec (§4b). |
| `2a71132` | `Backend/app/main.py` | Endpoint temporal `GET /api/whoami` protegido con `require_role("Administrador", "Docente", "Estudiante")`, para verificar el flujo en Swagger. |

No se tocó `routers/auth.py` ni `services/auth.py` (regla explícita del spec).

## 2. Decisiones sobre las preguntas abiertas (§5)

**5.1 — ¿Validar `estado` de Docente/Estudiante?** → **Sí.**
`get_current_user` rechaza con 401 a un Docente o Estudiante cuyo `estado` no sea `"Activo"`, además de validar que el usuario exista. `Administrador` y `Acudiente` no tienen columna `estado` en sus modelos, así que no aplica para ellos. Un usuario con rol Docente/Estudiante sin fila asociada en su tabla de rol (`rol_docente`/`rol_estudiante` en `None`) también se trata como inactivo (fail closed).

Sin esto, un profesor desactivado seguiría operando con su token viejo hasta que expirara — el caso que preocupa la historia "el colegio elimina un profesor y le revoca el acceso".

**5.2 — Códigos 401 vs 403.** → Confirmado sin necesitar código extra.
`fastapi==0.139.0` (la versión en `requirements.txt`) ya hace que `HTTPBearer` por defecto devuelva 401 "Not authenticated" cuando falta el header o está mal formado (versiones viejas de FastAPI devolvían 403 ahí). `require_role` devuelve 403 solo cuando el rol no está permitido. Confirmado con pruebas manuales (sección 3).

## 3. Pruebas manuales realizadas

Contra Postgres real (Docker) + backend real (`uvicorn`), usando los usuarios de prueba de `app/tests/crear_usuario_test.py` (`admin_real@colegio.edu.co`, `profesor_real@colegio.edu.co`):

| Caso | Resultado esperado | Resultado obtenido |
|---|---|---|
| Login real + `/api/whoami` con token de Administrador | 200 | ✅ 200 |
| Login real + `/api/whoami` con token de Docente activo | 200 | ✅ 200 |
| `/api/whoami` sin header `Authorization` | 401 | ✅ 401 "Not authenticated" |
| `/api/whoami` con token basura | 401 | ✅ 401 "Token inválido" |
| `/api/whoami` con token firmado pero expirado (`exp` en el pasado) | 401 | ✅ 401 "El token ha expirado" |
| `/api/whoami` con Docente cuyo `estado` se puso en `"Inactivo"` en BD | 401 | ✅ 401 "El usuario está inactivo" (estado restaurado a `"Activo"` después de la prueba) |
| `require_role("Administrador")` invocado con un usuario Docente | 403 | ✅ 403 "No tienes permiso para esta acción" |
| `/openapi.json` — esquema de seguridad para Swagger | `HTTPBearer` visible, botón Authorize funcional | ✅ Confirmado |

## 4. Pendientes / qué comunicar al equipo

- **Cursos, Calificaciones y Asistencia** siguen con RBAC como TODO. Cada router debe agregar su propio `Depends(require_role("Rol1", "Rol2", ...))` una vez esto esté en `develop` — no ocurre automáticamente.
- **RN-03 y RN-04** (pertenencia: profesor solo edita sus notas, estudiante solo ve su info) quedan fuera de esta pieza, a propósito. Cada módulo las implementa usando el `Usuario` que entrega `get_current_user`.
- **`/api/whoami`**: quedó en el código como referencia de uso de `require_role`. Se puede quitar antes de mergear a `develop` si el equipo prefiere no dejar endpoints de prueba — es un cambio de una línea en `main.py`.
- **Rama base**: se creó `feat/rbac-core` desde `main` porque no había `develop` disponible localmente en este entorno. El spec pide PR contra `develop` — falta confirmar/rebasear antes de abrir el PR.
- **Confirmar con Santiago/Samuel** (dueños del login original) que no hay conflicto — no se tocó `routers/auth.py` ni `services/auth.py`, pero vale avisarles antes del PR.
- PR requiere al menos un review (DoD del spec).
