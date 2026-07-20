# Spec: RBAC — Autenticación de request y control de acceso por rol

**Owner:** Mariana
**Repo:** `Saanhevi/Sistema-de-seguimiento-academico`
**Componente arquitectónico:** transversal — vive en `core/`, no es un módulo de dominio propio.
**Rama sugerida:** `feat/rbac-core` (desde `develop`)

---

## 1. Objetivo

Dar a todos los demás routers una forma estándar de saber **quién** está haciendo la petición y **qué rol** tiene, para poder proteger endpoints sin que cada persona invente su propia validación. Hoy el JWT ya lleva `sub` (id_usuario) y `rol` desde que Santiago hizo el login — falta el lado del servidor que lo lea y lo use.

## 2. Qué cubre / qué no

**Cubre:** RNF-03 (control de acceso por roles — ningún usuario opera fuera de su rol).

**No implementa, pero habilita:** RN-03 (solo el profesor asignado modifica sus notas) y RN-04 (un estudiante solo ve su propia información). Esas son reglas de *pertenencia*, más finas que un simple chequeo de rol — cada módulo (Calificaciones, Asistencia, etc.) las sigue implementando con su propia lógica, usando el usuario que esta pieza les entregue.

## 3. Fuera de alcance

- Refresh tokens, logout o revocación activa de un token antes de que expire.
- Las validaciones de pertenencia específicas de cada dominio (ver §2) — no son responsabilidad tuya.
- Tocar el endpoint de login existente (`routers/auth.py`, `services/auth.py`) — no se modifica, solo se construye encima.

## 4. Diseño técnico

### 4a. `Backend/app/core/security.py` — agregar

```python
def decode_access_token(token: str) -> dict:
    """
    Decodifica y valida un JWT firmado con settings.SECRET_KEY / settings.ALGORITHM.
    Debe propagar/traducir jwt.ExpiredSignatureError y jwt.InvalidTokenError
    en algo que la capa de dependencias pueda convertir en HTTPException 401.
    """
```

### 4b. `Backend/app/core/dependencies.py` — agregar

```python
from fastapi.security import HTTPBearer

security_scheme = HTTPBearer()

def get_current_user(
    credenciales = Depends(security_scheme),
    session = Depends(get_session),
):
    """
    1. Decodifica el token con decode_access_token.
    2. Extrae el claim "sub" (id_usuario).
    3. Busca al Usuario por id (reutiliza UsuarioRepository.buscar_por_id).
    4. Retorna el objeto Usuario.
    Lanza HTTPException 401 si: el token es inválido, expiró, o el usuario no existe.
    """

def require_role(*roles_permitidos: str):
    """
    Dependency factory. Uso en otro router:
        Depends(require_role("Administrador", "Docente"))
    Lanza HTTPException 403 si el rol del usuario actual no está en roles_permitidos.
    """
    def _verificar(usuario = Depends(get_current_user)):
        if usuario.rol not in roles_permitidos:
            raise HTTPException(status_code=403, detail="No tienes permiso para esta acción")
        return usuario
    return _verificar
```

Usa `HTTPBearer` (no `OAuth2PasswordBearer`): el login actual recibe JSON (`LoginRequest` con `correo`/`password`), no el formulario `username`/`password` que espera el flujo OAuth2 estándar de FastAPI, así que `HTTPBearer` es el que calza sin fricción con lo que ya existe.

### 4c. Cómo lo van a consumir los demás módulos (solo para validar el contrato, no lo implementes tú)

```python
@router.post("/cursos")
def crear_curso(data: CursoCreate, usuario = Depends(require_role("Administrador"))):
    ...
```

## 5. Preguntas abiertas para validar con el equipo

1. ¿`get_current_user` debe rechazar a un Docente/Estudiante con `estado = 'Inactivo'` aunque su token siga vigente? Afecta directamente la historia "el colegio elimina un profesor y le revoca el acceso" — si no se valida el estado en cada request, un profesor desactivado sigue operando hasta que expire su token viejo. Recomendación: sí, hacer esa consulta adicional.
2. Confirmar códigos de error consistentes: 401 cuando falta el token o es inválido/expiró, 403 cuando el rol no alcanza — para que el frontend los distinga.
3. Avisar en el standup: Cursos, Calificaciones y Asistencia quedaron documentados con RBAC como TODO. Una vez esto esté en `develop`, alguien tiene que volver a cada router y agregar el `Depends(require_role(...))` correspondiente — no pasa automáticamente.
4. Confirmar con Santiago/Samuel (dueños del login original) que no hay conflicto: tú solo agregas piezas nuevas en `security.py`/`dependencies.py`, no tocas `routers/auth.py` ni `services/auth.py`.

## 6. Estructura de archivos a tocar

No se crean routers ni services nuevos — es una pieza transversal:

```
Backend/app/core/security.py       (agregar decode_access_token)
Backend/app/core/dependencies.py   (agregar security_scheme, get_current_user, require_role)
```

Opcional: `Backend/app/schemas/token.py` con un `TokenPayload` (Pydantic) si prefieres validar el contenido decodificado del JWT en vez de trabajar con un `dict` crudo.

## 7. Definition of Done

- [ ] `decode_access_token` maneja token expirado e inválido con excepciones claras.
- [ ] `get_current_user` retorna 401 ante token inválido, expirado, o usuario inexistente.
- [ ] `require_role` retorna 403 cuando el rol no coincide con los permitidos.
- [ ] Probado manualmente: hacer login real, copiar el token, usar el botón "Authorize" de Swagger, y llamar un endpoint protegido de prueba.
- [ ] Se agrega al menos un endpoint temporal (o se usa uno ya existente) solo para verificar en Swagger que 401/403 se comportan como se espera.
- [ ] Comunicado en standup que RBAC está listo para que Cursos, Calificaciones y Asistencia lo adopten.
- [ ] PR contra `develop` con al menos un review.
