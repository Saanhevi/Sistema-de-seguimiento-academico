# Revisión de completitud — Historias de usuario marcadas como completadas

**Documento auditado:** `docs/historias-de-usuario-y-asignaciones.md`
**Fecha de la revisión:** 2026-07-26
**Alcance:** las 15 historias marcadas con ✅ en los Sprints 1 y 2 (HU0, HU0a, HU0b, HU1, HU2, HU3, HU4, HU5, HU6, HU7, HU8, HU9, HU10, HU12, HU14), contrastadas contra el código realmente implementado en `Backend/` y `Frontend/`.

---

## 1. Resumen ejecutivo

De las 15 historias marcadas como completadas, **3 no están realmente implementadas o no persisten** y **1 está implementada para un actor distinto al que declara la historia**. Las 11 restantes sí existen, pero varias arrastran defectos de corrección o de control de acceso.

Se identificaron **15 hallazgos**, encabezados por:

- **HU14** no tiene absolutamente nada de implementación: no existe ninguna ruta `DELETE` en toda la API.
- **HU12** guarda la asociación curso–estudiante en un `set` en memoria, sin tabla en la base de datos.
- **HU8 y HU9** tienen endpoints en el backend que **el frontend nunca invoca**; el promedio que ve el docente es un valor fijo escrito a mano.
- **HU0b** expone un endpoint de cambio de contraseña **sin autenticación**.

### 1.1 Estado declarado vs. estado real

| # | Historia | Declarado | Estado real | Veredicto |
|---|---|---|---|---|
| HU0 | Iniciar sesión | ✅ | Implementada | Correcta (ver H15) |
| HU0a | Crear cuenta estudiantil | ✅ | Implementada | Correcta |
| HU0b | Cambiar contraseña | ✅ | Implementada sin autenticación | **Defecto grave (H3)** |
| HU1 | Relacionar asignaturas con grados | ✅ | Implementada vía `Curso` | Correcta |
| HU2 | Profesor asigna estudiantes a grado | ✅ | Solo el administrador puede | **Actor incorrecto (H8)** |
| HU3 | Cargar notas del periodo | ✅ | Implementada | Correcta (ver H12) |
| HU4 | Almacenar notas por periodo y año | ✅ | Almacenamiento correcto | Correcta (ver H10) |
| HU5 | Agregar profesores | ✅ | Implementada | Correcta (ver H15) |
| HU6 | Registrar inasistencias | ✅ | Implementada con defectos | **Varios defectos (H5, H6, H9, H14)** |
| HU7 | Consultar mis inasistencias | ✅ | Implementada | Correcta |
| HU8 | Promedio por estudiante | ✅ | Backend sin interfaz de usuario | **Incompleta (H15b, H4, H10)** |
| HU9 | Promedio grupal | ✅ | Backend sin interfaz; falla para admin | **Incompleta (H7, H15b)** |
| HU10 | Consultar mis calificaciones | ✅ | Implementada | Correcta (ver H12) |
| HU12 | Añadir estudiantes a mi materia | ✅ | **Sin persistencia** | **Incompleta (H2)** |
| HU14 | Eliminar inasistencias | ✅ | **No implementada** | **No cumple (H1)** |

> **Actualización 2026-07-28 — HU8 y HU9.** Las dos filas de arriba reflejan la revisión
> del 2026-07-26 y se dejan como quedaron. Desde entonces se cerraron: H15b (el docente
> ya tiene interfaz, en *Gestión de calificaciones* y en el portal), H10 (el promedio
> pondera por sección y ya no mezcla periodos; la fórmula vive en un solo lugar del
> repositorio), H7 (el administrador obtiene el grupal en vez de 0.0), H13 (sin notas
> devuelve `null`, no 0.0) y H4/H11 (RN-03 se aplica al promedio individual, así que un
> docente no lee materias que no dicta). Pendiente de decisión: el promedio se normaliza
> sobre las secciones ya calificadas, así que un corte incompleto se reporta como
> definitivo; hay una prueba que lo documenta.

---

## 2. Hallazgos detallados

Ordenados de mayor a menor severidad.

---

### H1 — HU14 está marcada como completada pero no tiene ninguna implementación

**Archivo:** `docs/historias-de-usuario-y-asignaciones.md`, línea 28
**Severidad:** Crítica

La historia «Como profesor, quiero eliminar registros de inasistencias, para corregir datos ingresados incorrectamente» está marcada con ✅, pero no existe ni endpoint, ni método de servicio, ni método de repositorio, ni interfaz de usuario.

**Evidencia:**

- `grep -rn "router.delete" Backend/app/routers/` devuelve **cero** coincidencias: la API no expone el verbo `DELETE` en ningún módulo.
- `Backend/app/routers/asistencia.py` solo declara cuatro rutas: `GET /listas`, `PUT /listas/{id_dia}`, `GET /mis-asistencias` y `GET /listas/{id_curso}`.
- `AsistenciaService` y `AsistenciaRepository` no tienen ningún método `eliminar` / `borrar` / `delete`.
- En `Frontend/src/modules/asistencias/` no hay ninguna acción de eliminación.
- `SPEC/6-7-14-SPEC_Asistencias_Frontend.md` línea 18 sí lista HU14 dentro del alcance, pero su sección «Estado actual» solo declara una implementación preliminar del backend.

**Impacto:** un profesor que marcó por error una inasistencia no tiene forma de eliminar el registro.

**Matiz importante:** podría argumentarse que el `PUT` permite «corregir» devolviendo el estado a `Presente`. Sin embargo, eso corresponde a **HU17** («modificar las inasistencias registradas»), que sigue marcada con ⬜ en el Sprint 3. El `PUT` no puede cerrar HU14 sin cerrar también HU17.

---

### H2 — HU12 no persiste: la asociación curso–estudiante vive en memoria

**Archivo:** `Backend/app/services/curso.py`, línea 23
**Severidad:** Crítica

```python
class CursoService:
    asociaciones_curso_estudiante: set[tuple[int, int]] = set()
```

Se trata de un atributo **de clase** mutado en la línea 319 mediante `self.asociaciones_curso_estudiante.add(clave)`. No existe tabla que lo respalde: `Database/schemas.sql` define 17 tablas y ninguna es una tabla puente `CursoEstudiante`; tampoco hay modelo ORM correspondiente.

**Consecuencias:**

1. **Se pierde todo al reiniciar** la API o al hacer un nuevo despliegue.
2. Al ser un atributo de clase, el `set` es **estado global compartido** entre todas las peticiones y todos los usuarios.
3. Con `uvicorn --workers > 1` o varios contenedores, las asociaciones creadas por el worker A son **invisibles** para el worker B, de modo que `listar_estudiantes_para_curso` devuelve resultados distintos según qué proceso atienda la petición.
4. **Nada más lee ese `set`** salvo `listar_estudiantes_para_curso`. `lista_asistencia` arma su lista desde `grado.matriculas` y las notas se apoyan en `Matricula`, así que añadir un estudiante a la materia **no tiene ningún efecto** sobre asistencias ni calificaciones.

**Recomendación:** crear la tabla puente en `Database/schemas.sql` con su modelo y repositorio, y migrar la lógica de `asociar_estudiante_a_curso`.

---

### H3 — HU0b: el endpoint de cambio de contraseña no exige autenticación

**Archivo:** `Backend/app/routers/auth.py`, línea 23
**Severidad:** Crítica (seguridad)

```python
@router.put("/estudiante/password", response_model=MensajeResponde)
def actualizar_contrasena(
    credentials : ActualizarPasswordRequest,
    service : AuthService = Depends(get_auth_service)
):
```

La ruta declara únicamente `credentials` y `service`: **no tiene** `Depends(get_current_user)` ni `require_role(...)`, a diferencia de todas las demás rutas protegidas del proyecto. `AuthService.actualizar_contrasena` (`services/auth.py:94`) resuelve la cuenta objetivo con `self.repositorio.buscar_por_correo(credentials.correo)`, sin compararla nunca contra la identidad de la sesión.

**Escenarios de ataque:**

1. **Enumeración de cuentas:** una petición con cualquier correo devuelve `404 "El correo no existe"` si la cuenta no existe, frente a `401 "Contraseña actual incorrecta!!"` si existe. Eso permite descubrir qué correos están registrados.
2. **Fuerza bruta en línea:** sin límite de intentos, `password_anterior` puede probarse indefinidamente.
3. **Alcance más amplio del declarado:** pese a la ruta `/estudiante/`, no hay verificación de rol, por lo que la contraseña de un `Administrador` o de un `Docente` es igual de alcanzable.

**Defecto adicional:** `ActualizarPasswordRequest` (`schemas/auth.py:23`) tipa `password_nueva` como un `str` sin `min_length`, de modo que `""` es una contraseña nueva aceptada. Lo mismo ocurre con `CrearCuentaEstudiantilRequest.password` en HU0a.

---

### H4 — HU8: cualquier estudiante puede consultar el promedio de otro (IDOR)

**Archivo:** `Backend/app/routers/calificacion.py`, línea 80
**Severidad:** Alta (seguridad)

`GET /api/notas/promedio` está protegido con `require_role("Administrador", "Docente", "Estudiante")` y toma `id_estudiante` directamente del query string, pasándolo a `service.obtener_promedio_estudiante_materia(id_estudiante, id_materia)` **sin compararlo con el usuario autenticado**.

Esto contradice la regla RN-04, que sí se aplica en `listar_notas` (`services/calificacion.py:182`):

```python
# RN-04: un Estudiante solo puede ver sus propias notas
id_estudiante_filtro = usuario.id_usuario if usuario.rol == "Estudiante" else None
```

**Escenario:** el estudiante 42 invoca `/api/notas/promedio?id_estudiante=43&id_materia=1` y recibe el promedio de su compañero 43. Iterando `id_estudiante` se obtiene el rendimiento de todo el curso.

---

### H5 — HU6: un `GET` escribe en la base de datos y marca a todo el curso como presente

**Archivo:** `Backend/app/services/asistencia.py`, línea 41
**Severidad:** Alta

`GET /api/asistencias/listas` invoca `lista_asistencia`, que cuando no encuentra el día llama a `crear_dia_asistible(...)`, inserta un `HistorialAsistencia` por cada matrícula con `estado = "Presente"` fijo, y ejecuta `self.session.commit()` (línea 67).

Un `GET` debe ser seguro e idempotente. Aquí, el simple hecho de **consultar** una fecha:

- Crea permanentemente un día asistible.
- Registra a la clase completa como presente en un día que quizá nunca ocurrió.
- Se dispara con un docente navegando a una fecha futura, con un *prefetch* del navegador o con un doble clic.

**Condición de carrera adicional:** `Database/schemas.sql:141` define `DiaAsistible` **sin** restricción `UNIQUE (id_curso, fecha)`, y `consultar_dia_asistible` usa `.first()`. Dos `GET` concurrentes para el mismo curso y fecha no ven ninguna fila y ambos insertan, generando días duplicados cuyas ediciones de asistencia divergen; a partir de ahí `.first()` elige uno de forma no determinista.

---

### H6 — HU6: `KeyError` (HTTP 500) cuando un estudiante se matricula después de crear el día

**Archivo:** `Backend/app/services/asistencia.py`, línea 97
**Severidad:** Alta

```python
"estado": estados[id_estudiante]
```

El diccionario `estados` (línea 82) se construye únicamente a partir de las filas de `HistorialAsistencia`, que se insertan **una sola vez**, al crear el `DiaAsistible`. En cambio, el bucle de la línea 87 recorre las matrículas **actuales** del grado.

**Secuencia de fallo:**

1. El docente abre el 2026-03-01 para el curso 5; se crean el día y el historial de los 20 estudiantes matriculados en ese momento.
2. Un administrador matricula a un estudiante número 21 mediante HU2.
3. El docente vuelve a abrir el 2026-03-01: el nuevo estudiante está en `matriculas` pero **no** en `estados` → `KeyError` → **500 no controlado**.

A partir de ese momento la página de asistencia de esa fecha queda rota para todo el curso. La matriculación a mitad de año es precisamente el flujo que HU2 y HU12 existen para soportar.

**Corrección sugerida:** usar `estados.get(id_estudiante, "Presente")` y crear la fila de historial faltante.

---

### H7 — HU9: el promedio grupal siempre devuelve 0.0 para un administrador

**Archivo:** `Backend/app/services/calificacion.py`, línea 196
**Severidad:** Alta

`obtener_promedio_grupal_materia` admite explícitamente al administrador (línea 189: `if usuario.rol not in ["Docente", "Administrador"]`) y el router también lo permite con `require_role("Administrador", "Docente")`. Sin embargo, después llama a:

```python
return self.nota_repo.obtener_promedio_grupal_materia(id_materia, usuario.id_usuario)
```

y el repositorio (`repositories/nota.py:73`) filtra por `Curso.id_docente == id_docente`.

El `id_usuario` de un administrador nunca aparece en `Curso.id_docente` (`schemas.sql:104` lo referencia contra `Docente`), así que la consulta no devuelve filas y el método retorna `0.0`, presentado al llamador como un promedio grupal legítimo de 0.0 en lugar de «no aplica». La persona administradora de HU9 está silenciosamente rota.

**Corrección sugerida:** omitir el filtro por docente (o ampliarlo a todos los cursos de la materia) cuando `usuario.rol == "Administrador"`.

---

### H8 — HU2 está marcada para el profesor, pero solo el administrador puede ejecutarla

**Archivo:** `Backend/app/services/curso.py`, línea 199
**Severidad:** Alta

HU2 dice «Como **profesor**, quiero asignar estudiantes a un grado académico». `routers/curso.py:113` permite `require_role("Administrador", "Docente")`, pero la primera instrucción de `crear_matricula` es:

```python
if usuario_actual is not None and usuario_actual.rol != "Administrador":
    raise HTTPException(status_code=403, detail="Solo los administradores pueden crear matrículas")
```

Un profesor autenticado que haga `POST /api/matriculas` recibe siempre un 403. La discrepancia entre router y servicio hace además que el endpoint anuncie una capacidad que nunca honra.

**Del lado de la interfaz:** la única pantalla de matrícula es `MatriculaPanel`, montada exclusivamente bajo `AdminCursos` (`admin/AdminCursos.jsx:43`) dentro del portal de administrador. `Frontend/src/modules/dashboard/pages/admin/AdminEstudiantes.jsx` sigue siendo un esqueleto que devuelve `<div>AdminEstudiantes</div>`.

**Veredicto:** HU2 está satisfecha únicamente para administradores. O se corrige el permiso, o se reescribe la historia con el actor correcto.

---

### H9 — HU6: ningún endpoint de asistencia verifica que el curso pertenezca al docente

**Archivo:** `Backend/app/routers/asistencia.py`, línea 21
**Severidad:** Alta (seguridad)

Las tres rutas de docente se protegen solo con `require_role("Docente")` y propagan `id_curso` / `id_dia` sin validación. `lista_asistencia`, `actualizar_asistencia` e `historial_dias_curso` nunca comparan `curso.id_docente` con `usuario.id_usuario`.

Esto contrasta con dos implementaciones ya existentes de esa misma regla RN-03 en el proyecto:

- `CalificacionService._validar_pertenencia_curso` (`services/calificacion.py:29`)
- `CursoService._obtener_curso_validado` (`services/curso.py:51`)

**Escenario:** el docente A hace `PUT /api/asistencias/listas/{id_dia}` sobre un día que pertenece al curso del docente B y reescribe la asistencia de toda la clase.

**Defecto adicional:** la línea 27 hace `curso = self.curso_repo.buscar_por_id(id_curso)` sin comprobar `None`, de modo que un `id_curso` inexistente llega a `curso.grado` y produce un 500 por `AttributeError` en lugar de un 404.

---

### H10 — HU8/HU9: el promedio ignora los porcentajes de sección y mezcla todos los periodos y años

**Archivo:** `Backend/app/repositories/nota.py`, línea 58
**Severidad:** Media-alta

Ambos métodos de promedio hacen `join` con `SeccionPorcentaje` solo para poder llegar a `Curso`, y luego calculan `sum(calificaciones) / len(calificaciones)`. La columna `porcentaje` **nunca se lee**, y no hay filtro por `Curso.id_periodo` ni por `PeriodoAcademico.anio`.

**Ejemplo numérico:** un curso con Examen = 60 % (una nota de 2.0) y Talleres = 40 % (cuatro notas de 5.0) debería promediar **3.2**, pero el sistema devuelve **4.4**.

Además, las notas de 2025 y 2026 de la misma materia se agrupan en un único número, lo que anula el propósito de **HU4** («almacene las calificaciones por periodo y año escolar, para conservar el historial académico»).

**El proyecto ya conoce la fórmula correcta:** `Frontend/src/modules/calificaciones/utils/notas.js:29` implementa `promedioPonderado` como `Σ(nota_seccion * porcentaje) / Σ(porcentaje)`. Backend y frontend van a discrepar sobre cuál es el promedio de un estudiante.

**HU9 lo agrava:** promedia filas de notas en bruto en vez de promediar los promedios por estudiante, así que un estudiante con 10 actividades pesa más que uno con 2.

---

### H11 — HU3/HU10: un docente puede listar todas las notas de la institución

**Archivo:** `Backend/app/services/calificacion.py`, línea 183
**Severidad:** Media-alta (seguridad)

`id_estudiante_filtro` solo se establece para el rol `Estudiante`; para un `Docente` queda en `None`, y `id_actividad` es `int | None = Query(default=None)` en el router. `NotaRepository.listar` (`repositories/nota.py:18`) añade cada cláusula `WHERE` solo cuando el argumento no es `None`, así que con ambos en `None` la consulta degenera en un `select(Nota)` sin filtros.

Cualquier profesor autenticado que haga `GET /api/notas` recibe **todas** las notas de todos los estudiantes, cursos y años, incluidos los cursos de sus colegas.

Es el mismo límite RN-03 que `crear_nota` y `cargar_notas_masivo` sí cuidan mediante `_validar_pertenencia_curso`, pero abandonado en la ruta de lectura. `listar_secciones` y `listar_actividades` presentan idéntico comportamiento y además están expuestas al rol `Estudiante`.

---

### H12 — Datos personales de estudiantes expuestos a cualquier estudiante

**Archivo:** `Backend/app/services/curso.py`, línea 227
**Severidad:** Media-alta (privacidad)

`routers/curso.py:134` protege `GET /api/grados/{id_grado}/estudiantes` con `require_role("Administrador", "Docente", "Estudiante")` y llama a `service.listar_estudiantes_por_grado(id_grado=id_grado, anio=anio)`. Nótese que, a diferencia de todas las llamadas hermanas de ese router, **no se propaga `usuario_actual`**, de modo que el servicio no puede acotar el resultado ni aunque quisiera.

El `SELECT` devuelve `Usuario.nombres`, `Usuario.apellidos` y `Usuario.correo`. Un estudiante que itere `id_grado` desde 1 en adelante obtiene el nombre completo y el correo de todo el colegio.

Contrasta con `obtener_curso` (línea 191), que se esfuerza en devolver 404 a un estudiante que fisgonea el curso de otro grado, precisamente para impedir este recorrido de identificadores.

---

### H13 — HU8/HU9: `0.0` se usa como marcador de «sin datos»

**Archivo:** `Backend/app/repositories/nota.py`, línea 56
**Severidad:** Media

`if not notas: return 0.0` se dispara en cuatro situaciones distintas e indistinguibles en la interfaz:

1. `id_estudiante` inexistente.
2. `id_materia` inexistente.
3. Estudiante no matriculado en la materia.
4. Materia en la que todos los estudiantes sacaron legítimamente 0.00.

Como `calificacion` es `NUMERIC(3,2)` con rango válido 0.00–5.00 (`services/calificacion.py:91`), **0.0 es una nota real alcanzable** y no puede servir como marcador nulo.

Ninguno de los dos métodos comprueba la existencia de los identificadores, así que `/api/notas/promedio?id_estudiante=999999&id_materia=999999` responde **HTTP 200 con `promedio: 0.0`** en lugar de 404.

**Corrección sugerida:** devolver `None` y tipar la respuesta como `Optional[float]`, para que el frontend pueda mostrar «sin datos».

---

### H14 — HU6: `estado` sin validar produce un 500 en lugar de un 422

**Archivo:** `Backend/app/schemas/asistencia.py`, línea 21
**Severidad:** Media

`Database/schemas.sql:153` restringe `estado` a `('Presente','Ausente','Retardo','Excusa')`, pero el esquema Pydantic acepta cualquier cadena:

```python
class AsistenciaRequest(BaseModel):
    id_estudiante : int
    estado : str
```

`PUT /api/asistencias/listas/1` con `[{"id_estudiante":7,"estado":"Enfermo"}]` pasa la validación, llega a `actualizar_registro_asistencia` y Postgres lanza un `CheckViolation`. `AsistenciaService.actualizar_asistencia` (`services/asistencia.py:129`) captura `SQLAlchemyError`, hace `rollback` y vuelve a lanzarlo con un `raise` desnudo, de modo que FastAPI responde **500 Internal Server Error** en vez de un 4xx que explique el problema.

**Corrección sugerida:** usar `Literal["Presente","Ausente","Retardo","Excusa"]` o un `StrEnum`.

**Brecha de cobertura relacionada:** `AsistenciaTable.jsx` solo ofrece `Presente` y `Ausente` en su desplegable, así que los estados `Retardo` y `Excusa` que el esquema soporta son inalcanzables desde la interfaz de HU6.

---

### H15 — HU8 y HU9 están marcadas como completadas pero no tienen interfaz de usuario

**Archivo:** `docs/historias-de-usuario-y-asignaciones.md`, líneas 22–23
**Severidad:** Media (completitud)

`grep -rn "promedio" Frontend/src/` no muestra ninguna llamada a `/api/notas/promedio` ni a `/api/materia/{id}/promedio-grupal`. Ninguno de los dos aparece en `calificacionService.js`, que sí exporta todas las demás llamadas del módulo de calificaciones.

**Evidencia complementaria:**

- El KPI «Promedio general» de `PortalDocente.jsx:45` es el literal `7.8` con subtítulo «Matemáticas». El propio encabezado del archivo lo admite: *«Actualmente es una vista estática»*.
- `DocenteReportes.jsx` — el lugar natural para estas cifras — es un esqueleto que devuelve `<div>DocenteReportes</div>`.
- `TablaNotas.jsx:75` recalcula por su cuenta un promedio por actividad con `promedioSimple`, duplicando HU8 en el cliente con una fórmula distinta a la del backend.

**Veredicto:** tal como está desplegado, un profesor **no puede ver** ni el promedio por estudiante ni el promedio grupal desde el producto. Ambas historias son solo backend.

---

## 3. Temas estructurales

Más allá de los hallazgos puntuales, se observan dos patrones de fondo:

### 3.1 Las reglas de negocio no se propagaron a los módulos nuevos

Las reglas **RN-03** (pertenencia del curso al docente) y **RN-04** (el estudiante solo ve lo suyo) están cuidadosamente implementadas en `CalificacionService` y `CursoService`, con comentarios explícitos que las citan. Sin embargo, nunca se trasladaron a `AsistenciaService` (H9) ni a las rutas de lectura añadidas después para HU8 y HU9 (H4, H11).

Las historias más recientes reabrieron límites que las anteriores ya habían cerrado. Conviene extraer estas validaciones a un mecanismo compartido —por ejemplo, una dependencia de FastAPI que resuelva y valide el curso— en lugar de reimplementarlas en cada servicio.

### 3.2 Backend y frontend no coinciden en qué es un promedio

El cálculo de HU8/HU9 en el backend ignora los pesos de `SeccionPorcentaje`, mientras que el helper `promedioPonderado` del frontend ya los aplica correctamente (H10). Mientras ambos coexistan, el sistema dará dos respuestas distintas a la misma pregunta.

---

## 4. Recomendaciones sobre el documento de historias

1. **Revertir a ⬜** el estado de **HU14** (sin implementación) y de **HU12** (sin persistencia).
2. **Revertir a ⬜**, o marcar como «solo backend», **HU8** y **HU9**, dado que no son alcanzables desde la interfaz.
3. **Corregir HU2**: o se habilita al docente en `crear_matricula`, o se reescribe la historia con el administrador como actor.
4. **Definir un criterio de aceptación explícito** para marcar ✅. La evidencia sugiere que hoy basta con que exista código en el backend; convendría exigir el recorrido completo backend + interfaz + prueba.
5. **Priorizar H3** (endpoint de contraseña sin autenticación) por encima de cualquier funcionalidad nueva del Sprint 3.
