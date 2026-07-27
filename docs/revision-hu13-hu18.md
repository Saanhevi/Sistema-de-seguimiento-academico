# Revisión de código: HU13 y HU18

**Rama:** `feature/hu13-hu18-bloqueo-notas`
**Commit revisado:** `d10aecf` — *feat: adicionar validaciones HU13 y HU18 para bloquear notas en cortes o periodos cerrados a docentes*
**Responsable:** Laura
**Fecha de revisión:** 2026-07-27

---

## Resumen ejecutivo

| Historia | Estado real | Motivo |
|---|---|---|
| **HU13** — bloquear notas de un **corte** finalizado | ❌ **No implementada** | La validación es código muerto: `SeccionPorcentaje` no tiene columna `estado` ni en el modelo ni en `Database/schemas.sql`, y no existe endpoint para cerrar un corte. |
| **HU18** — bloquear notas de un **periodo y año escolar** finalizado | ⚠️ **Parcial** | La validación del periodo sí funciona para docentes, pero no existe endpoint para que el administrador cierre un periodo, no se valida el año escolar, y la parte de "eliminar" no está cubierta. |

Además, **un test de integración existente queda roto** (`test_07_periodo_cerrado_bloquea_notas`) y el documento de seguimiento `docs/historias-de-usuario-y-asignaciones.md` sigue marcando ambas historias como `⬜`.

**Total de hallazgos:** 21 — 14 de backend (4 críticos, 5 medios, 5 menores) y 7 de frontend (sección final).

---

## Hallazgos críticos

### 1. HU13 es código muerto: `SeccionPorcentaje` no tiene columna `estado`

- **Archivo:** `Backend/app/services/calificacion.py`
- **Línea:** 115

**Resumen**
La validación del corte usa `getattr(seccion, "estado", "Abierto")`. Como el atributo no existe, `getattr` siempre devuelve el valor por defecto `"Abierto"`, por lo que la comparación con `"Cerrado"` nunca es verdadera y la excepción nunca se lanza. HU13 no está implementada.

**Escenario de fallo**
`Database/schemas.sql:167-175` define la tabla con solo cuatro columnas:

```sql
CREATE TABLE IF NOT EXISTS SeccionPorcentaje (
    id_seccion INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_seccion VARCHAR(50) NOT NULL,
    porcentaje NUMERIC(5,2) NOT NULL,
    id_curso INTEGER NOT NULL,
    ...
);
```

Y `Backend/app/models/seccion_porcentaje.py` mapea exactamente esas cuatro. No hay `estado` en ninguna parte.

Flujo concreto: el administrador "finaliza" un corte → el docente hace `POST /api/notas` con una actividad de ese corte → `getattr` devuelve `"Abierto"` → `"Abierto" == "Cerrado"` es `False` → no se lanza excepción → **la nota se guarda igual**.

**Sugerencia de corrección**
Se necesitan tres cambios coordinados:

1. **Migración de base de datos** — agregar la columna en `Database/schemas.sql`:

```sql
CREATE TABLE IF NOT EXISTS SeccionPorcentaje (
    id_seccion INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_seccion VARCHAR(50) NOT NULL,
    porcentaje NUMERIC(5,2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Abierto' CHECK(
        estado IN ('Abierto', 'Cerrado')
    ),
    id_curso INTEGER NOT NULL,

    FOREIGN KEY (id_curso)
        REFERENCES Curso(id_curso)
);
```

2. **Modelo** — en `Backend/app/models/seccion_porcentaje.py`:

```python
estado: Mapped[str] = mapped_column(String(20), default="Abierto")
```

3. **Endpoint de cierre** — agregar `PATCH /api/secciones/{id_seccion}/estado` en `Backend/app/routers/calificacion.py`, restringido a `require_role("Administrador")`, siguiendo el patrón que ya existe en `Backend/app/routers/docente.py:41` (`@router.patch("/{id_docente}/estado")`).

Sin los tres, HU13 no puede funcionar.

---

### 2. Se rompe el test de integración `test_07_periodo_cerrado_bloquea_notas`

- **Archivo:** `Backend/app/tests/test_calificaciones_integracion.py`
- **Línea:** 338

**Resumen**
El nuevo camino que devuelve 403 rompe un test existente que espera 400.

**Escenario de fallo**
El test inicia sesión con `self.token_docente` (rol `Docente`) y hace `POST /api/notas` contra `id_curso_cerrado`. Ahora `_validar_bloqueos` se ejecuta primero (`calificacion.py:161`), el atajo de `Administrador` no aplica, `periodo.estado != "Abierto"` → se lanza `HTTPException` con **403**. El test hace `self.assertEqual(status, 400)` → **falla**.

**Sugerencia de corrección**
Hay que decidir cuál es el contrato correcto y dejar uno solo (ver hallazgo #6). Recomendación: unificar en **403** (es una restricción de autorización, no de formato de datos) y actualizar el test:

```python
def test_07_periodo_cerrado_bloquea_notas(self):
    """RN-d / HU18: con el periodo del curso 'Cerrado' no se pueden registrar notas (403)."""
    ...
    self.assertEqual(status, 403)
```

Y actualizar también el docstring del módulo en la línea 15 y el de `test_calificacion_service.py:8`.

---

### 3. HU18 no es accionable: no existe endpoint para cerrar un periodo

- **Archivo:** `Backend/app/routers/curso.py`
- **Línea:** 61

**Resumen**
El actor de HU18 es el administrador ("quiero **bloquear** a los profesores..."), pero no tiene ninguna forma de cerrar un periodo que ya está abierto.

**Escenario de fallo**
Solo existen `POST /periodos` (crear) y `GET /periodos` (listar). En `Backend/app/services/curso.py` solo están `crear_periodo` (línea 124) y `listar_periodos` (línea 133). En `Backend/app/repositories/periodo_academico.py` solo hay `crear`, `buscar_por_id` y `listar`. No hay ningún `PUT`/`PATCH`.

Consecuencia: un periodo creado como `'Abierto'` al inicio del semestre, con cursos y notas asociadas, **nunca puede pasar a `'Cerrado'`**. La regla solo se dispara para periodos creados como `'Cerrado'` desde el principio, que es un caso que ningún flujo real produce.

**Sugerencia de corrección**
Agregar el método al repositorio, al servicio y un endpoint restringido a administrador:

```python
# Backend/app/services/curso.py
def actualizar_estado_periodo(self, id_periodo: int, estado: str) -> PeriodoAcademico:
    if estado not in {"Abierto", "Cerrado"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El estado debe ser Abierto o Cerrado")
    periodo = self.periodo_repo.buscar_por_id(id_periodo)
    if not periodo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Periodo académico no encontrado")
    periodo.estado = estado
    self.session.commit()
    self.session.refresh(periodo)
    return periodo
```

```python
# Backend/app/routers/curso.py
@router.patch("/periodos/{id_periodo}/estado", response_model=PeriodoAcademicoResponse)
def actualizar_estado_periodo(
    id_periodo: int,
    payload: PeriodoEstadoUpdate,
    service: CursoService = Depends(get_curso_service),
    usuario=Depends(require_role("Administrador")),
):
    return service.actualizar_estado_periodo(id_periodo, payload.estado)
```

Nota: la validación de `estado` ya existe duplicada en `crear_periodo` (línea 127-128); conviene extraerla a un helper `_validar_estado_periodo`.

---

### 4. El orden de validaciones está invertido: se filtra información de cursos ajenos

- **Archivo:** `Backend/app/services/calificacion.py`
- **Línea:** 161 (y 177 en `cargar_notas_masivo`)

**Resumen**
`_validar_bloqueos` se llama **antes** que `_validar_pertenencia_curso`. La autorización debe ir siempre antes que las reglas de negocio.

**Escenario de fallo**
El Docente A (id 3) hace `POST /api/notas` con un `id_actividad` que pertenece a un curso del Docente B, cuyo periodo está `'Cerrado'`. En lugar de recibir `403 "No tienes permiso sobre este curso"`, recibe:

```
403 "HU18: No se pueden registrar o modificar notas de un período finalizado (2026)"
```

Esto le confirma a A que la actividad existe y le revela el año académico de un curso al que no tiene acceso. El mismo problema está en `cargar_notas_masivo` (línea 177 antes de 178).

**Sugerencia de corrección**
Invertir el orden en ambos métodos:

```python
# crear_nota (líneas 161-165)
self._validar_pertenencia_curso(actividad.seccion.curso, usuario)
self._validar_bloqueos(actividad, usuario)
self._validar_calificacion(calificacion)
self._validar_estudiante(id_estudiante)
```

```python
# cargar_notas_masivo (líneas 177-179)
self._validar_pertenencia_curso(actividad.seccion.curso, usuario)
self._validar_bloqueos(actividad, usuario)
```

---

## Hallazgos medios

### 5. La excepción para `Administrador` queda anulada por `_validar_periodo_abierto`

- **Archivo:** `Backend/app/services/calificacion.py`
- **Línea:** 110 (en conflicto con 165 y 179)

**Resumen**
`_validar_bloqueos` exime explícitamente al administrador, pero justo después se llama a `_validar_periodo_abierto`, que no tiene esa excepción. El administrador queda bloqueado igual.

**Escenario de fallo**
Un `Administrador` hace `POST /api/notas` para un curso con periodo `'Cerrado'`:
1. `_validar_bloqueos` retorna temprano en la línea 111 (no bloquea). ✅
2. La línea 165 llama a `_validar_periodo_abierto`, que lanza `400 "El período académico de este curso no está abierto"`. ❌

El resultado neto es que el administrador sigue bloqueado; lo único que cambió fue el código de estado y el mensaje. El `if usuario.rol == "Administrador": return` no tiene ningún efecto real.

**Sugerencia de corrección**
Hay que decidir la regla de negocio y aplicarla en un solo lugar:

- **Si el administrador SÍ debe poder corregir notas en periodos cerrados** (interpretación coherente con "el admin es quien decide qué se bloquea"): eliminar la llamada a `_validar_periodo_abierto` de `crear_nota` y `cargar_notas_masivo`, y dejar que `_validar_bloqueos` sea la única validación (ver hallazgo #6).
- **Si el administrador NO debe poder**: eliminar el atajo de las líneas 110-111, que solo confunde.

Cualquiera de las dos es válida, pero hay que documentarla como regla de negocio (`RN-d` actualizada) y cubrirla con un test.

---

### 6. Validación de periodo duplicada con dos códigos de estado distintos

- **Archivo:** `Backend/app/services/calificacion.py`
- **Línea:** 123 (duplica la línea 105)

**Resumen**
La misma condición de negocio devuelve 403 o 400 según el rol de quien la dispare.

**Escenario de fallo**
- `_validar_bloqueos`, línea 123: `if periodo.estado != "Abierto"` → **403** `"HU18: No se pueden registrar o modificar notas de un período finalizado (2026)"`
- `_validar_periodo_abierto`, línea 105: `if periodo_estado != "Abierto"` → **400** `"El período académico de este curso no está abierto"`

Es literalmente la misma comparación. Un `Docente` recibe 403; un `Administrador` cae hasta el 400. Cualquier cliente o test que ramifique según el código de estado ahora tiene que manejar los dos.

**Sugerencia de corrección**
Consolidar en un único método. Propuesta: eliminar el bloque HU18 de `_validar_bloqueos` y mover la lógica de rol dentro de `_validar_periodo_abierto`:

```python
def _validar_periodo_abierto(self, actividad: ActividadEvaluativa, usuario: Usuario) -> None:
    # RN-d / HU18: no se pueden registrar ni modificar notas si el periodo del
    # curso no está 'Abierto'. El Administrador queda exento porque es quien
    # administra el cierre.
    if usuario.rol == "Administrador":
        return
    periodo = actividad.seccion.curso.periodo
    if periodo.estado != "Abierto":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No se pueden registrar ni modificar notas del periodo "
                   f"'{periodo.nombre} {periodo.anio}' porque está finalizado",
        )
```

Y actualizar las dos llamadas (`calificacion.py:165` y `:179`) para pasar `usuario`. Así queda un solo contrato: **403** siempre.

---

### 7. `crear_seccion` y `crear_actividad` no están bloqueadas

- **Archivo:** `Backend/app/services/calificacion.py`
- **Líneas:** 37 (`crear_seccion`) y 69 (`crear_actividad`)

**Resumen**
Un docente puede seguir creando secciones y actividades dentro de un corte o periodo finalizado. Ninguno de los dos métodos llama a `_validar_bloqueos` ni a `_validar_periodo_abierto`.

**Escenario de fallo**
Lo demuestra el propio test de integración del repositorio. En `test_calificaciones_integracion.py:323`, `test_07_periodo_cerrado_bloquea_notas` hace:

```python
seccion = self._crear("/api/secciones", self.token_docente,
                      {"nombre_seccion": "Cerrada", "porcentaje": 50, "id_curso": self.id_curso_cerrado})
actividad = self._crear("/api/actividades", self.token_docente,
                        {"nombre": "Fuera de plazo", "fecha": "2026-03-20", "id_seccion": seccion["id_seccion"]})
```

`_crear` hace `assert status == 200`, o sea que **ambas creaciones son exitosas** sobre un curso con periodo cerrado. Solo la nota se bloquea.

Impacto: HU13 y HU18 dicen "bloquear... la posibilidad de **subir**, modificar o eliminar notas". Crear secciones con porcentaje en un periodo cerrado altera la ponderación que usan los promedios de HU8/HU9, aunque no se puedan agregar notas.

**Sugerencia de corrección**
Agregar la validación en ambos métodos, después de la de pertenencia:

```python
# crear_seccion, después de la línea 50
self._validar_pertenencia_curso(curso, usuario)
self._validar_curso_editable(curso, usuario)   # nuevo helper sobre curso.periodo

# crear_actividad, después de la línea 79
self._validar_pertenencia_curso(seccion.curso, usuario)
self._validar_seccion_editable(seccion, usuario)  # valida corte + periodo
```

---

### 8. El bloqueo se cablea por llamada en vez de centralizarse (la parte de "eliminar" queda descubierta)

- **Archivo:** `Backend/app/services/calificacion.py`
- **Línea:** 161 y 177

**Resumen**
`_validar_bloqueos` se invoca manualmente en dos sitios. Ambas historias dicen explícitamente "subir, modificar o **eliminar** notas", y hoy la parte de eliminar no está cubierta.

**Escenario de fallo**
No existe ruta de borrado (en `routers/calificacion.py` solo hay `POST` y `GET`; `NotaRepository` no tiene método `eliminar`), así que "eliminar" está sin enforcar **por accidente, no por diseño**. Cuando entre HU16 ("eliminar notas del periodo actual"), quien la implemente tiene que acordarse de agregar una tercera llamada a `_validar_bloqueos`. Si se olvida, HU13 y HU18 quedan violadas en silencio.

**Sugerencia de corrección**
Aplicar la guarda en el punto más profundo del flujo, no en cada endpoint. Opción recomendada: un único helper que toda ruta de escritura deba atravesar.

```python
def _validar_escritura_nota(self, actividad: ActividadEvaluativa, usuario: Usuario) -> None:
    """Puerta única de escritura de notas: pertenencia + corte + periodo.
    Toda ruta que cree, modifique o elimine notas debe pasar por aquí."""
    self._validar_pertenencia_curso(actividad.seccion.curso, usuario)
    self._validar_corte_abierto(actividad.seccion, usuario)     # HU13
    self._validar_periodo_abierto(actividad, usuario)           # HU18
```

Y que `crear_nota`, `cargar_notas_masivo` y las futuras `modificar_nota` / `eliminar_nota` llamen solo a este método. Resuelve de paso los hallazgos #4 y #6.

---

### 9. No se agregaron pruebas para `_validar_bloqueos`

- **Archivo:** `Backend/app/services/calificacion.py`
- **Línea:** 108

**Resumen**
El método nuevo no tiene ninguna prueba, rompiendo la convención del archivo de tests. Una sola prueba habría detectado el hallazgo #1.

**Escenario de fallo**
`Backend/app/tests/test_calificacion_service.py` tiene una clase por regla (`PertenenciaCursoTests`/RN-03, `CalificacionRangoTests`/RN-a, `PeriodoAbiertoTests`/RN-d, `ListarNotasRolTests`/RN-04) y las enumera en el docstring del módulo (líneas 4-9). `_validar_bloqueos` no aparece referenciado en ningún test del repositorio.

**Ojo con un detalle importante:** un test basado en `Mock()` también habría ocultado el hallazgo #1, porque `Mock().estado` autocrea un atributo que no es igual a `"Cerrado"` y la validación pasaría de todos modos. El test de HU13 **debe construir un `SeccionPorcentaje` real**, que es exactamente lo que habría dejado en evidencia la columna faltante.

**Sugerencia de corrección**
Agregar una clase de pruebas usando objetos reales para la sección:

```python
class BloqueoCorteYPeriodoTests(unittest.TestCase):
    """HU13 (corte cerrado) y HU18 (periodo cerrado)."""

    def setUp(self):
        self.service = CalificacionService(Mock())
        self.docente = Usuario(id_usuario=3, rol="Docente")
        self.admin = Usuario(id_usuario=1, rol="Administrador")

    def _actividad_real(self, estado_seccion="Abierto", estado_periodo="Abierto"):
        # SeccionPorcentaje real: si la columna 'estado' no existe, esto falla
        # y el bug queda expuesto en vez de quedar enmascarado por un Mock.
        seccion = SeccionPorcentaje(nombre_seccion="Corte 1", porcentaje=50, id_curso=10)
        seccion.estado = estado_seccion
        seccion.curso = _curso(id_docente=3, estado_periodo=estado_periodo)
        actividad = Mock()
        actividad.seccion = seccion
        return actividad

    def test_hu13_corte_cerrado_bloquea_al_docente(self):
        with self.assertRaises(HTTPException) as exc:
            self.service._validar_bloqueos(self._actividad_real(estado_seccion="Cerrado"), self.docente)
        self.assertEqual(exc.exception.status_code, 403)

    def test_hu18_periodo_cerrado_bloquea_al_docente(self):
        with self.assertRaises(HTTPException) as exc:
            self.service._validar_bloqueos(self._actividad_real(estado_periodo="Cerrado"), self.docente)
        self.assertEqual(exc.exception.status_code, 403)

    def test_corte_y_periodo_abiertos_pasan(self):
        self.service._validar_bloqueos(self._actividad_real(), self.docente)  # no lanza
```

Y agregar las reglas al docstring del módulo (líneas 4-9).

---

## Hallazgos menores

### 10. El documento de seguimiento no fue actualizado

- **Archivo:** `docs/historias-de-usuario-y-asignaciones.md`
- **Líneas:** 27 (HU13) y 37 (HU18)

**Resumen**
Ambas historias siguen marcadas como `⬜` y HU18 no tiene responsable asignado.

**Escenario de fallo**
- Línea 27 (Sprint 2): `| ⬜ | HU13 | ... corte finalizado ... | Laura |`
- Línea 37 (Sprint 3): `| ⬜ | HU18 | ... periodo y año escolar finalizado ... | — |`

El commit `d10aecf` dice implementar ambas, pero ninguna fila fue actualizada y HU18 sigue sin responsable. El documento y el mensaje del commit se contradicen.

**Sugerencia de corrección**
Asignar responsable a HU18 y dejar ambas filas en `⬜` hasta que se cierren los hallazgos #1 y #3; recién ahí pasarlas a `✅` (ver "Definición de terminado" al final).

---

### 11. `getattr` con valor por defecto hace que un control de integridad falle "abierto"

- **Archivo:** `Backend/app/services/calificacion.py`
- **Línea:** 115

**Resumen**
`getattr(seccion, "estado", "Abierto")` silencia hoy el atributo faltante y silenciará mañana un valor `NULL`.

**Escenario de fallo**
- **Hoy:** el atributo no existe, y el valor por defecto suprime el `AttributeError` que habría apuntado directamente a la columna faltante (hallazgo #1).
- **Después de la migración:** si `estado` se agrega como nullable y las filas existentes quedan en `NULL`, entonces `None == "Cerrado"` es `False` → el corte se trata como abierto y las notas se pueden modificar.

Un control que decide si se pueden alterar calificaciones debe fallar **cerrado**, no abierto.

**Sugerencia de corrección**
Leer una columna real (hallazgo #1) y usar la forma negativa, igual que ya hace la validación del periodo en la línea 123:

```python
if seccion.estado != "Abierto":
    raise HTTPException(...)
```

Además, declarar la columna `NOT NULL DEFAULT 'Abierto'` en el esquema para que nunca haya `NULL`.

---

### 12. HU18 pide "periodo **y año escolar** finalizado", pero el año nunca se valida

- **Archivo:** `Backend/app/services/calificacion.py`
- **Línea:** 123

**Resumen**
Solo se compara `periodo.estado`. El año escolar nunca se contrasta contra el año actual, pese a que el enunciado de HU18 lo menciona explícitamente.

**Escenario de fallo**
Un registro de periodo con `anio=2020` que nunca pasó a `'Cerrado'` (muy probable, dado el hallazgo #3: no existe endpoint para cerrarlo) sigue siendo totalmente editable. Un docente hace `POST /api/notas` contra un curso de 2020 estando en 2026: `periodo.estado == "Abierto"` → tanto `_validar_bloqueos` como `_validar_periodo_abierto` pasan → **la nota se escribe en el histórico de un año escolar anterior**. Esto también socava HU4 ("conservar el historial académico"). El año se lee en la línea 126 solo para el mensaje, nunca como condición.

**Sugerencia de corrección**
Agregar la validación de año como red de seguridad independiente del estado:

```python
from datetime import date

# HU18: además del estado, ningún docente escribe en un año escolar anterior.
if periodo.anio < date.today().year:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"No se pueden registrar ni modificar notas del año escolar {periodo.anio}",
    )
```

Ojo: confirmar con el equipo si el año escolar coincide con el año calendario antes de fijar la comparación.

---

### 13. Los identificadores internos de historias se filtran a los mensajes de error de la API

- **Archivo:** `Backend/app/services/calificacion.py`
- **Líneas:** 118 y 126

**Resumen**
Los `detail` incluyen los prefijos `"HU13: "` y `"HU18: "`, y el frontend los muestra tal cual al usuario final.

**Escenario de fallo**
`Frontend/src/modules/calificaciones/components/CargaMasivaModal.jsx:46` hace `setError(err.detail || "No se pudo completar la carga masiva")` y la línea 85 lo renderiza. El docente ve literalmente en pantalla:

> HU18: No se pueden registrar o modificar notas de un período finalizado (2026)

Todos los demás mensajes de este servicio (líneas 33, 40, 43, 48, 72, 77, 92, 100, 106, 182) son texto limpio sin prefijo de historia.

**Sugerencia de corrección**
Mover la referencia a la historia al comentario y dejar el mensaje limpio:

```python
# HU13: no se registran ni modifican notas de un corte finalizado.
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="No se pueden registrar ni modificar notas de un corte finalizado",
)
```

---

### 14. El mensaje de HU18 usa `periodo.anio` en vez de `periodo.nombre`

- **Archivo:** `Backend/app/services/calificacion.py`
- **Línea:** 126

**Resumen**
El mensaje identifica el periodo solo por su año, lo que es ambiguo cuando un año tiene varios periodos.

**Escenario de fallo**
`PeriodoAcademico` tiene tanto `nombre` (ej. `"Periodo 1"`) como `anio`. El propio setup del test de integración crea dos periodos con el **mismo** `nombre` y el **mismo** `anio`, diferenciados solo por `estado` (`test_calificaciones_integracion.py:108-115`). Un docente con cuatro bimestres en 2026 recibe `"período finalizado (2026)"` para todos y no puede saber cuál fue rechazado.

**Sugerencia de corrección**
Incluir ambos campos:

```python
detail=f"No se pueden registrar ni modificar notas del periodo "
       f"'{periodo.nombre} {periodo.anio}' porque está finalizado",
```

---

## Cambios necesarios en el frontend

Esta sección cubre lo que falta para que HU13 y HU18 sean **usables por una persona real**, no solo correctas a nivel de API.

### Estado actual del frontend

Buena noticia: **la mitad del trabajo de HU18 ya está hecha en el frontend.** El flujo de "periodo cerrado → solo lectura" ya está cableado de punta a punta:

| Componente | Qué ya hace | Línea |
|---|---|---|
| `DocenteCalificaciones.jsx` | Calcula `periodoAbierto = curso?.periodo?.estado === "Abierto"` y lo baja como prop | 24, 91, 117 |
| `EstadoPeriodo.jsx` | Banner "Periodo activo — edición habilitada" / "Periodo cerrado — solo lectura" | 21-23 |
| `SeccionPanel.jsx` | `puedeEditar = !readOnly && periodoAbierto` oculta los botones "Nueva sección" y "Nueva actividad" | 34, 103, 207 |
| `TablaNotas.jsx` | Deshabilita las celdas (`disabled={!periodoAbierto}`), muestra un candado, bloquea `abrirEditor` y oculta "Carga masiva" | 81, 205-210, 230 |

Mala noticia: **HU13 no tiene absolutamente nada en el frontend.** La palabra "corte"/`estado` de sección no aparece en ningún componente. Y el administrador —el actor de ambas historias— no tiene ninguna pantalla desde donde ejecutar el bloqueo.

---

### 15. El administrador no puede cerrar un periodo desde la interfaz

- **Archivo:** `Frontend/src/modules/cursos/components/PeriodoPanel.jsx`
- **Líneas:** 89-95 (tabla) y 92-104 de `Frontend/src/modules/cursos/services/cursoService.js`

**Resumen**
El panel de periodos solo **muestra** el estado como texto plano. No hay ninguna forma de cambiarlo.

**Escenario de fallo**
El administrador entra a *Gestión académica → Períodos*, ve la tabla con las columnas ID / Nombre / Año / **Estado**, y la celda dice `Abierto`. No hay botón, ni selector, ni acción. La única manera de tener un periodo `'Cerrado'` es crearlo así desde el formulario (líneas 65-71), lo cual no sirve: los cursos y las notas ya están colgando del periodo abierto. **HU18 es literalmente inejecutable desde la interfaz**, aunque se arregle el backend (hallazgo #3).

**Sugerencia de corrección**
1. Agregar la llamada al servicio, siguiendo el patrón que ya existe en `Frontend/src/modules/profesores/services/profesorService.js:18-21`:

```js
// Frontend/src/modules/cursos/services/cursoService.js
async function actualizarEstadoPeriodo(idPeriodo, estado) {
  if (useMocks) {
    const periodo = mockPeriodos.find((p) => p.id_periodo === Number(idPeriodo));
    if (periodo) periodo.estado = estado;
    return periodo;
  }
  try {
    const response = await api.patch(`/api/periodos/${idPeriodo}/estado`, { estado });
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: "Error de conexión con el servidor" };
  }
}
```

Recordar exportarla en el bloque `export { ... }` de la línea 254.

2. Agregar la columna de acción en la tabla, reutilizando el patrón de toggle de `ProfesorCard.jsx:25-31`:

```jsx
// Frontend/src/modules/cursos/components/PeriodoPanel.jsx
const handleToggleEstado = async (periodo) => {
  const nuevoEstado = periodo.estado === "Abierto" ? "Cerrado" : "Abierto";
  const verbo = nuevoEstado === "Cerrado" ? "cerrar" : "reabrir";
  // Cerrar un periodo bloquea la edición de notas a TODOS los docentes: se confirma.
  if (!window.confirm(
    `¿Seguro que quieres ${verbo} "${periodo.nombre} ${periodo.anio}"?\n\n` +
    (nuevoEstado === "Cerrado"
      ? "Los docentes ya no podrán registrar ni modificar notas de este periodo."
      : "Los docentes volverán a poder registrar y modificar notas.")
  )) return;

  try {
    await actualizarEstadoPeriodo(periodo.id_periodo, nuevoEstado);
    await cargarPeriodos();
  } catch (error) {
    alert(error.detail || "No se pudo cambiar el estado del periodo");
  }
};
```

```jsx
<td>
  <span className={`status-pill ${periodo.estado === "Abierto" ? "active" : "inactive"}`}>
    {periodo.estado}
  </span>
</td>
<td>
  <button
    type="button"
    className={`status-btn ${periodo.estado === "Abierto" ? "desactivar-btn" : "activar-btn"}`}
    onClick={() => handleToggleEstado(periodo)}
  >
    {periodo.estado === "Abierto" ? "Cerrar periodo" : "Reabrir periodo"}
  </button>
</td>
```

Las clases `status-pill`, `status-btn`, `activar-btn` y `desactivar-btn` ya existen en `Frontend/src/styles/Profesores.css:84,164-183`; conviene moverlas a `global.css` o duplicar las reglas en `Cursos.css` para no acoplar el módulo de cursos a la hoja de profesores.

3. Agregar el `<th>Acciones</th>` correspondiente en el `<thead>` (línea 81-86).

---

### 16. No existe ninguna interfaz para cerrar un corte (HU13)

- **Archivo:** `Frontend/src/modules/calificaciones/components/SeccionPanel.jsx`
- **Líneas:** 154-172 (encabezado de cada sección)

**Resumen**
Las secciones de porcentaje (los "cortes") se renderizan mostrando solo nombre y porcentaje. No hay estado ni acción de cierre en ninguna parte del frontend.

**Escenario de fallo**
El administrador quiere "finalizar el primer corte" y no encuentra dónde hacerlo: el panel de secciones vive dentro de la vista del **docente** (`/dashboard/docente/calificaciones`), a la que el administrador ni siquiera tiene acceso (ver hallazgo #18). HU13 no tiene punto de entrada en la UI.

**Sugerencia de corrección**
Requiere tres piezas, en este orden:

1. **Backend — exponer el campo.** Sin esto el frontend no puede saber el estado. En `Backend/app/schemas/calificacion.py`:

```python
class SeccionPorcentajeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_seccion: int
    nombre_seccion: str
    porcentaje: float
    estado: str          # <-- nuevo (HU13)
    id_curso: int
    advertencia: Optional[str] = None
```

2. **Servicio del frontend** — en `calificacionService.js`, junto a `crearSeccion` (línea 38):

```js
async function actualizarEstadoSeccion(idSeccion, estado) {
  try {
    const response = await api.patch(`/api/secciones/${idSeccion}/estado`, { estado });
    return response.data;
  } catch (error) {
    throw error.response?.data || ERROR_CONEXION;
  }
}
```

3. **UI** — mostrar el estado en el encabezado del acordeón y, si el usuario es administrador, el botón de cierre:

```jsx
// dentro del map de secciones, en el header
<span className="cal-seccion-name">{seccion.nombre_seccion}</span>
<span className="cal-seccion-pct">{Number(seccion.porcentaje).toFixed(2)}%</span>
{seccion.estado !== "Abierto" && (
  <span className="cal-seccion-estado closed">Corte finalizado</span>
)}
```

El botón "Cerrar corte" debe ir en la vista de administrador (hallazgo #18), no en la del docente: es el administrador quien bloquea, no el profesor.

---

### 17. El bloqueo del corte no se propaga a la tabla de notas ni a los formularios

- **Archivo:** `Frontend/src/modules/calificaciones/components/TablaNotas.jsx`
- **Líneas:** 14 (firma), 81, 205, 230

**Resumen**
Toda la lógica de "solo lectura" del frontend depende de una sola variable, `periodoAbierto`. Cuando exista `seccion.estado`, un corte cerrado dentro de un periodo abierto dejará la tabla **completamente editable**.

**Escenario de fallo**
El administrador cierra el primer corte pero el periodo sigue abierto (que es exactamente el caso de uso de HU13, distinto del de HU18). El docente abre *Calificaciones*, selecciona el curso: `curso.periodo.estado === "Abierto"` → `periodoAbierto` es `true` → el banner dice "Periodo activo — edición habilitada", las celdas están habilitadas, el botón "Carga masiva" aparece y "Nueva actividad" también. El docente escribe una nota, presiona Guardar, y **recién ahí** recibe un 403 del backend. La interfaz le prometió algo que el servidor le niega.

**Sugerencia de corrección**
Reemplazar la prop booleana única por una noción de "se puede editar esta sección", calculada en el padre:

```jsx
// Frontend/src/modules/dashboard/pages/docente/DocenteCalificaciones.jsx
const periodoAbierto = curso?.periodo?.estado === "Abierto";
const corteAbierto = seccionActiva ? seccionActiva.estado === "Abierto" : true;
const puedeCalificar = periodoAbierto && corteAbierto;

// motivo del bloqueo, para poder explicarlo en pantalla
const motivoBloqueo = !periodoAbierto
  ? `El periodo "${curso.periodo?.nombre} ${curso.periodo?.anio}" está finalizado.`
  : !corteAbierto
    ? `El corte "${seccionActiva?.nombre_seccion}" está finalizado.`
    : null;
```

Y pasar `puedeCalificar` + `motivoBloqueo` a `TablaNotas` en lugar de `periodoAbierto` (línea 117). Dentro de `TablaNotas`, renombrar la prop y ajustar las cuatro referencias (81, 205, 206, 210, 230); el `title` del botón de celda pasa a usar `motivoBloqueo` para que el tooltip diga la razón concreta en vez del genérico "Periodo cerrado" de la línea 206.

Lo mismo en `SeccionPanel.jsx:34`: `puedeEditar` debe considerar el estado de cada sección para ocultar "Nueva actividad" (línea 207) en los cortes cerrados, dejando visible "Nueva sección" solo si el periodo está abierto.

---

### 18. El administrador no tiene ninguna vista de calificaciones

- **Archivos:** `Frontend/src/routes/AppRouter.jsx` (líneas 71-76) y `Frontend/src/modules/dashboard/components/Navbar.jsx` (líneas 156-168)

**Resumen**
Las rutas y el menú del administrador solo contemplan Cursos, Estudiantes y Profesores. No hay pantalla de calificaciones para ese rol.

**Escenario de fallo**
Dos consecuencias:
1. **HU13 no tiene dónde vivir.** El cierre de cortes se administra por curso y por sección, y esa vista solo existe bajo `/dashboard/docente/calificaciones`, ruta a la que el administrador no llega desde el menú.
2. **La excepción de `Administrador` del backend es inalcanzable.** El hallazgo #5 discute si el administrador debe poder corregir notas en un periodo cerrado; hoy la discusión es teórica, porque no tiene ninguna pantalla donde escribir una nota.

**Sugerencia de corrección**
Agregar una pantalla de administración de cortes y periodos. Lo más económico es una pestaña nueva en `AdminCursos.jsx`, que ya tiene la infraestructura de tabs:

```jsx
// Frontend/src/modules/dashboard/pages/admin/AdminCursos.jsx
const tabs = [
  { key: "grados", label: "Grados" },
  { key: "materias", label: "Materias" },
  { key: "periodos", label: "Períodos" },
  { key: "cortes", label: "Cortes" },        // <-- nuevo (HU13)
  { key: "cursos", label: "Cursos" },
  { key: "matriculas", label: "Matrículas" }
];
...
{tabActiva === "cortes" && <CortePanel />}
```

`CortePanel` sería un componente nuevo en `Frontend/src/modules/cursos/components/`: selector de curso, lista de sus secciones con el porcentaje y un botón "Cerrar corte" / "Reabrir corte" por fila. Reutiliza `listarSecciones` (ya existe en `calificacionService.js:29`) y la nueva `actualizarEstadoSeccion`.

Si se prefiere no crear pantalla nueva, la alternativa es habilitar `/dashboard/admin/calificaciones` reutilizando `DocenteCalificaciones` con una prop `esAdmin`, pero eso exige que el selector de cursos deje de filtrar por `id_docente` (`SelectorCurso` recibe `idDocente={user?.id_usuario}` en `DocenteCalificaciones.jsx:77`), lo cual es más invasivo.

---

### 19. El estado del periodo queda cacheado en el state: la UI no se entera del cierre

- **Archivo:** `Frontend/src/modules/calificaciones/components/TablaNotas.jsx`
- **Línea:** 108

**Resumen**
`curso.periodo.estado` se lee una sola vez al seleccionar el curso y vive en el state de React. Si el administrador cierra el periodo o el corte mientras el docente tiene la pantalla abierta, la interfaz sigue mostrándose editable indefinidamente.

**Escenario de fallo**
El docente abre *Calificaciones* a las 10:00. A las 10:05 el administrador cierra el periodo. El docente sigue viendo el banner verde "Periodo activo", las celdas habilitadas y el botón de carga masiva. Escribe cinco notas y todas fallan una por una con el 403; `setErrorCelda(err.detail ...)` muestra el mensaje pero **no actualiza el banner ni deshabilita nada**, así que el docente puede seguir intentando en bucle sin entender qué cambió.

**Sugerencia de corrección**
Tratar el 403 como una señal de que el estado local quedó obsoleto y forzar la resincronización:

```js
// TablaNotas.jsx, dentro de guardarNota
} catch (err) {
  setErrorCelda(err.detail || "No se pudo guardar la nota");
  // Un 403 aquí significa que el corte o el periodo se cerró después de
  // que cargamos el curso: el estado local quedó obsoleto.
  if (err.status === 403 || err.codigo === "BLOQUEADO") {
    onEstadoObsoleto?.();   // el padre recarga el curso y la sección
  }
}
```

Para que esto funcione hay que propagar el código de estado HTTP, que hoy se pierde: `calificacionService.js` hace `throw error.response?.data` (líneas 78, 87), descartando `error.response.status`. Conviene enriquecer el objeto lanzado:

```js
// calificacionService.js — aplicar en las 9 funciones del archivo
} catch (error) {
  if (!error.response) throw ERROR_CONEXION;
  throw { ...error.response.data, status: error.response.status };
}
```

Esto sirve a todo el módulo, no solo a HU13/HU18.

---

### 20. Los mensajes con prefijo "HU13:" / "HU18:" se muestran tal cual al docente

- **Archivos:** `Frontend/src/modules/calificaciones/components/CargaMasivaModal.jsx` (línea 46) y `Frontend/src/modules/calificaciones/components/TablaNotas.jsx` (línea 108)

**Resumen**
Es la cara visible del hallazgo #13: ambos componentes renderizan `err.detail` sin transformarlo.

**Escenario de fallo**
`CargaMasivaModal.jsx:46` hace `setError(err.detail || "No se pudo completar la carga masiva")` y lo pinta en la línea 85. `TablaNotas.jsx:108` hace lo mismo con `setErrorCelda`. El docente ve en pantalla el texto crudo:

> HU18: No se pueden registrar o modificar notas de un período finalizado (2026)

**Sugerencia de corrección**
La corrección principal es en el backend (hallazgo #13): quitar el prefijo del `detail`. Una vez hecho eso, el frontend no necesita cambios aquí y el mensaje que ya llega es adecuado.

Como mejora adicional de accesibilidad, conviene que estos errores de bloqueo no se muestren como un `<p className="cal-error">` suelto sino con `role="alert"`, para que los lectores de pantalla los anuncien:

```jsx
{error && <p className="cal-error" role="alert">{error}</p>}
```

Aplica a `TablaNotas.jsx:126-127`, `SeccionPanel.jsx:114,149`, `CargaMasivaModal.jsx:85` y `ActividadModal.jsx:66`.

---

### 21. El banner de estado no distingue periodo cerrado de corte cerrado

- **Archivo:** `Frontend/src/modules/calificaciones/components/EstadoPeriodo.jsx`
- **Líneas:** 5-25

**Resumen**
El componente solo conoce dos estados posibles del periodo. Con HU13 hay tres situaciones distintas que el docente necesita diferenciar.

**Escenario de fallo**
Con el periodo abierto y el primer corte cerrado, el banner dice "Periodo activo — edición habilitada" mientras la tabla de ese corte está bloqueada. El mensaje contradice lo que el docente ve, y no le explica que puede seguir calificando en los otros cortes del mismo curso.

**Sugerencia de corrección**
Generalizar el componente para que reciba el motivo del bloqueo calculado en el padre (hallazgo #17):

```jsx
export default function EstadoPeriodo({ periodo, seccionActiva }) {
  const periodoAbierto = periodo?.estado === "Abierto";
  const corteAbierto = seccionActiva ? seccionActiva.estado === "Abierto" : true;
  const editable = periodoAbierto && corteAbierto;

  const mensaje = !periodoAbierto
    ? `Periodo "${periodo?.nombre} ${periodo?.anio}" finalizado — solo lectura`
    : !corteAbierto
      ? `Corte "${seccionActiva?.nombre_seccion}" finalizado — solo lectura`
      : "Periodo activo — edición habilitada";

  return (
    <div className={`cal-period-banner ${editable ? "open" : "closed"}`} role="status">
      {/* el icono de candado abierto/cerrado ya existe en las líneas 11-20 */}
      {mensaje}
    </div>
  );
}
```

Las clases `.cal-period-banner.open` y `.closed` ya están definidas en `Frontend/src/styles/Calificaciones.css:251-262`, así que no hace falta CSS nuevo. El `role="status"` hace que el cambio de estado se anuncie a lectores de pantalla.

Conviene aplicar lo mismo en la vista del estudiante (`EstudianteCalificaciones.jsx`), que hoy usa `SeccionPanel` en modo `readOnly`: mostrarle "Corte finalizado" le explica por qué su nota ya no va a cambiar.

---

## Resumen de archivos a tocar en el frontend

| Archivo | Cambio | Historia |
|---|---|---|
| `modules/cursos/services/cursoService.js` | `actualizarEstadoPeriodo()` + export | HU18 |
| `modules/cursos/components/PeriodoPanel.jsx` | Columna de acciones con botón Cerrar/Reabrir | HU18 |
| `modules/calificaciones/services/calificacionService.js` | `actualizarEstadoSeccion()` + propagar `status` en los catch | HU13 + ambas |
| `modules/cursos/components/CortePanel.jsx` | **Nuevo**: administración de cortes por curso | HU13 |
| `modules/dashboard/pages/admin/AdminCursos.jsx` | Pestaña "Cortes" | HU13 |
| `modules/calificaciones/components/SeccionPanel.jsx` | Mostrar estado del corte; `puedeEditar` por sección | HU13 |
| `modules/calificaciones/components/TablaNotas.jsx` | Prop `puedeCalificar`/`motivoBloqueo`; resync ante 403 | HU13 + HU18 |
| `modules/calificaciones/components/EstadoPeriodo.jsx` | Distinguir corte vs periodo; `role="status"` | HU13 + HU18 |
| `modules/dashboard/pages/docente/DocenteCalificaciones.jsx` | Calcular `puedeCalificar` y `motivoBloqueo` | HU13 + HU18 |
| `modules/dashboard/pages/estudiante/EstudianteCalificaciones.jsx` | Mostrar estado del corte (opcional) | HU13 |

---

## Orden sugerido de trabajo

### Backend (primero: el frontend no puede avanzar sin esto)

1. **#1** — migración + modelo + endpoint de cierre de corte (desbloquea HU13 por completo).
2. **#3** — endpoint de cierre de periodo (desbloquea HU18 por completo).
3. **#8 + #6 + #4 + #5** — refactor a un único `_validar_escritura_nota` con orden correcto y un solo código de estado. Estos cuatro se resuelven juntos.
4. **#2** — actualizar el test de integración al contrato definitivo.
5. **#7** — extender el bloqueo a `crear_seccion` y `crear_actividad`.
6. **#9** — agregar la clase de pruebas unitarias (con objetos reales, no `Mock`).
7. **#11, #12, #13, #14** — endurecimiento y limpieza de mensajes.
   Ojo: **#13 debe hacerse antes de dar por cerrado el frontend**, porque el prefijo "HU18:" llega hasta la pantalla del docente.
   Ojo: exponer `estado` en `SeccionPorcentajeResponse` es requisito del punto 8.

### Frontend

8. **#15** — botón de cerrar/reabrir periodo en `PeriodoPanel`. Con esto HU18 queda **completa y usable**.
9. **#16 + #18** — exponer `estado` en la respuesta de secciones y crear la pestaña "Cortes" del administrador. Con esto HU13 queda **ejecutable**.
10. **#17 + #21** — propagar el bloqueo del corte a la tabla y al banner. Con esto HU13 queda **completa y usable** para el docente.
11. **#19 + #20** — propagar el código HTTP, resincronizar ante 403 y agregar `role="alert"` / `role="status"`. Robustez y accesibilidad.

### Cierre

12. **#10** — actualizar `docs/historias-de-usuario-y-asignaciones.md` al final, cuando backend y frontend estén ambos listos.

### Definición de "terminado"

HU13 y HU18 se pueden marcar como `✅` cuando un administrador pueda, **sin tocar la base de datos a mano**:
- cerrar un corte desde la interfaz y ver que el docente deja de poder calificar ese corte (y solo ese);
- cerrar un periodo desde la interfaz y ver que el docente deja de poder calificar todo el curso;
- y que en ambos casos el docente reciba una explicación clara en pantalla **antes** de intentar escribir, no después.
