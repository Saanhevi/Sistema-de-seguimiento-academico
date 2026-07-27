# Revisión de código — rama `revert-23-revert-22-origin/feat/vistacalificaciones`

**Rama revisada:** `revert-23-revert-22-origin/feat/vistacalificaciones` (commit `035c7b9`, revert-del-revert que restaura el PR #22)
**Base de comparación:** `main`
**Fecha de la revisión:** 2026-07-27
**Documento de historias contrastado:** `docs/historias-de-usuario-y-asignaciones.md`
**Alcance del diff:** 11 archivos, +562 / −102 líneas (módulo de calificaciones, backend y frontend)

---

## 1. Resumen ejecutivo

La rama toca **tres historias de usuario, todas asignadas a Snehider y todas marcadas ⬜** en el documento de asignaciones: HU11, HU15 y HU16. Ninguna queda completa.

Lo que realmente entrega la rama es **eliminación de actividades y secciones para el docente** —una funcionalidad que **no corresponde a ninguna de las 24 historias listadas**— más una implementación parcial de HU11.

### 1.1 Estado declarado vs. estado real

| Historia | Enunciado | Declarado | Estado real | % estimado |
|---|---|---|---|---|
| **HU11** | Estudiante consulta porcentaje, nota, comentario, nombre de la entrega y estudiante asociado | ⬜ | Comentario, nota, nombre de actividad y porcentaje de sección visibles. Falta *estudiante asociado*. Introduce una regresión en HU10. | **~80 %** |
| **HU15** | Profesor modifica las notas del periodo actual | ⬜ | `PUT /api/notas` es una copia literal de `POST /api/notas`. La edición **ya funcionaba** antes de la rama vía el upsert de `_preparar_nota`. | **0 % de capacidad nueva** |
| **HU16** | Profesor elimina notas del periodo actual | ⬜ | **No implementada.** La sección del servicio está rotulada `# --- Eliminaciones (HU16) ---` pero solo expone `DELETE /api/actividades/{id}` y `DELETE /api/secciones/{id}`. No existe ningún borrado de nota individual. | **0 %** |

### 1.2 Hallazgos

Se identificaron **15 hallazgos**. Los cuatro que deberían resolverse antes de integrar a `main`:

- **H1** — HU16 está rotulada en el código pero no implementada, y el sustituto disponible es destructivo: la única forma de quitar una nota es borrar la actividad completa, lo que borra la nota de **todos** los estudiantes.
- **H2** — El layout nuevo de `.cal-actividad-item` es **CSS muerto**: un selector idéntico y posterior en el mismo archivo lo sobreescribe. La fila de tres columnas nunca se renderiza como se diseñó.
- **H3 / H4** — Las dos rutas nuevas de borrado no toman el advisory lock del módulo ni hacen `rollback`; una carrera con un upsert concurrente termina en HTTP 500 con la transacción en estado fallido.
- **H5** — Se perdió el marcador «—» de las actividades sin calificar, lo que **regresa HU10**, ya marcada ✅.

Adicionalmente: dos endpoints de borrado en cascada e irreversibles se integran **sin una sola prueba**, y la rama no aporta el par `SPEC/N-spec-*.md` / `N-summary-*.md` que acompaña a todas las funcionalidades anteriores del repositorio.

---

## 2. Resumen por historia de usuario

### 2.1 HU11 — Estudiante consulta el detalle de cada calificación

> *Como estudiante, quiero consultar el porcentaje, nota, comentario, nombre de la entrega y estudiante asociado a cada calificación, para comprender el detalle de mis evaluaciones.*

**Qué hace la rama.** `EstudianteCalificaciones.jsx:38` cambia `mapa[nota.id_actividad] = nota.calificacion` por `mapa[nota.id_actividad] = nota`, de modo que la vista del estudiante recibe el objeto completo y no solo el número. `SeccionPanel.jsx:247-262` aprovecha eso para renderizar `nota.comentario`, y en modo `readOnly` lo vuelve clicable para abrir un popup con el texto completo (`SeccionPanel.jsx:307-319`). `Calificaciones.css` añade el truncado con elipsis y los estilos `cal-popup-*`.

**Cobertura de los cinco datos exigidos:**

| Dato exigido | ¿Visible? | Dónde |
|---|---|---|
| Porcentaje | Sí, a nivel de sección | `SeccionPanel.jsx:212` — `{Number(seccion.porcentaje).toFixed(2)}%` en el encabezado del acordeón |
| Nota | Sí | `SeccionPanel.jsx:244-246` — badge con `formatearNota` |
| Comentario | **Sí (nuevo en esta rama)** | `SeccionPanel.jsx:247-262` + popup |
| Nombre de la entrega | Sí | `SeccionPanel.jsx:239` — `{actividad.nombre}` |
| **Estudiante asociado** | **No** | No se renderiza en ninguna parte |

**Veredicto: ~80 %.** El aporte real de la rama es el comentario, que era el único de los cinco datos que faltaba junto con el estudiante asociado. Queda pendiente el estudiante asociado y hay que revertir la regresión **H5**, que empeora la vista respecto a `main`.

### 2.2 HU15 — Profesor modifica las notas del periodo actual

> *Como profesor, quiero modificar las notas del periodo actual, para corregir errores o actualizar evaluaciones.*

**Qué hace la rama.** Añade `PUT /api/notas` (`routers/calificacion.py:93-100`) y cambia `TablaNotas.jsx` para llamar `actualizarNota` en lugar de `registrarNota`.

**Por qué no aporta capacidad nueva.** El handler nuevo ejecuta exactamente la misma línea que el `POST`:

```python
return service.crear_nota(payload.id_actividad, payload.id_estudiante, payload.calificacion, payload.comentario, usuario)
```

Y `crear_nota` delega en `_preparar_nota` (`services/calificacion.py:134-150`), que **ya era un upsert**: si existe nota para el par `(id_actividad, id_estudiante)`, actualiza `calificacion` y `comentario`. Es decir, el docente ya podía modificar notas desde `main` reabriendo la celda en `TablaNotas`. Lo único que cambia es el verbo HTTP.

**Veredicto: 0 % de capacidad nueva.** La historia estaba funcionalmente satisfecha antes de la rama; lo que falta es darle a `PUT` semántica real de actualización (ver **§4.2**) y cubrirla con pruebas.

### 2.3 HU16 — Profesor elimina notas del periodo actual

> *Como profesor, quiero eliminar notas del periodo actual, para corregir registros erróneos o duplicados.*

**Qué hace la rama.** `services/calificacion.py:222` abre una sección rotulada `# --- Eliminaciones (HU16) ---` que contiene `eliminar_actividad` y `eliminar_seccion`, expuestas como `DELETE /api/actividades/{id_actividad}` y `DELETE /api/secciones/{id_seccion}`. En el frontend, `SeccionPanel.jsx` añade una «×» por actividad y un botón «Eliminar sección».

**Por qué no es HU16.** Verificado: no existe ningún `DELETE /api/notas`, ni un método `eliminar_nota` en el servicio, ni un `borrar(nota)` de nota individual en `NotaRepository` (solo `borrar_por_actividad`, `repositories/nota.py:94`). Además `TablaNotas.guardarNota` rechaza la calificación vacía (`TablaNotas.jsx:93-96`), así que tampoco se puede «vaciar» una celda para borrarla.

El resultado es que el docente que se equivocó con **un** estudiante solo tiene un camino: borrar la actividad entera y perder las notas de **todo el curso**.

**Veredicto: 0 %.** La historia sigue abierta y el rótulo del código induce a pensar lo contrario.

---

## 3. Hallazgos detallados

> Los números de línea corresponden al estado de la rama en el commit `035c7b9`.

---

### H1 — HU16 rotulada pero no implementada; el sustituto es destructivo

- **Archivo:** `Backend/app/services/calificacion.py`
- **Línea:** 222
- **Categoría:** desalineación con la especificación / pérdida de datos

**Resumen.** La sección está rotulada `# --- Eliminaciones (HU16) ---` («eliminar notas del periodo actual») pero ningún endpoint ni método de servicio elimina una nota individual; la única eliminación disponible destruye la actividad o la sección completa.

**Escenario de falla.** El docente registra 4.5 al estudiante equivocado y quiere borrar esa única nota. No existe `DELETE /api/notas`, y `TablaNotas.guardarNota` (`TablaNotas.jsx:93-96`) rechaza una calificación vacía, así que el único camino es la «×» nueva de la actividad, que ejecuta `borrar_por_actividad` y elimina la nota de **todos** los estudiantes de esa actividad. Se pierde información de terceros para corregir un dato de uno.

**Corrección sugerida.** Implementar el borrado de nota individual, que es lo que pide la historia:

```python
# repositories/nota.py
def borrar(self, nota: Nota):
    try:
        self.session.delete(nota)
        self.session.flush()
    except Exception:
        self.session.rollback()
        raise

# services/calificacion.py
def eliminar_nota(self, id_nota: int, usuario: Usuario) -> None:
    nota = self.nota_repo.buscar_por_id(id_nota)
    if not nota:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nota no encontrada")

    actividad = self.actividad_repo.buscar_por_id(nota.id_actividad)
    self._validar_pertenencia_curso(actividad.seccion.curso, usuario)   # RN-03
    self._validar_periodo_abierto(actividad)                            # RN-d
    self._bloquear_nota(nota.id_actividad, nota.id_estudiante)           # RN-f

    try:
        self.nota_repo.borrar(nota)
        self.session.commit()
    except Exception:
        self.session.rollback()
        raise
```

```python
# routers/calificacion.py
@router.delete("/notas/{id_nota}", status_code=204)
def eliminar_nota(
    id_nota: int = Path(gt=0, le=ID_MAXIMO),
    service: CalificacionService = Depends(get_calificacion_service),
    usuario=Depends(require_role("Administrador", "Docente")),
):
    service.eliminar_nota(id_nota, usuario)
```

Mientras eso no exista, cambiar el rótulo de la línea 222 para que no declare una historia que no cumple (p. ej. `# --- Eliminación de actividades y secciones ---`).

---

### H2 — El layout nuevo de `.cal-actividad-item` es CSS muerto

- **Archivo:** `Frontend/src/styles/Calificaciones.css`
- **Línea:** 516 (sobreescrito desde 597)
- **Categoría:** corrección / CSS

**Resumen.** El bloque nuevo `.cal-actividad-item { display: grid; grid-template-columns: minmax(0,1fr) auto auto }` queda anulado por un `.cal-actividad-item { display: flex; justify-content: space-between }` **preexistente, de igual especificidad y posterior** en el mismo archivo (línea 597), así que el layout nuevo nunca se aplica.

**Escenario de falla.** Mismo selector, misma especificidad: gana la regla posterior. `display` resuelve a `flex`, `grid-template-columns` queda inerte, y `.cal-actividad-item button.cal-btn.icon { justify-self: end }` (línea 578) no hace nada porque `justify-self` no aplica a ítems flex. La fila con comentario de 100 caracteres + badge + botón de borrado se reparte por `space-between` en lugar de las tres columnas previstas, y el `max-width: 50%` del comentario en modo lectura se calcula contra la línea flex y no contra la pista de la grilla. Los selectores `.cal-actividad-item:last-child` (582/608) y `.cal-actividad-fecha` (586/612) también están duplicados literalmente.

**Corrección sugerida.** Eliminar el bloque antiguo (líneas 597-616: el `.cal-actividad-item` flex y las repeticiones de `:last-child` y `.cal-actividad-fecha`), conservando `.cal-actividad-list` que está intercalado, y dejar una sola definición de cada selector. Verificar después en el navegador que la fila queda en tres columnas tanto en la vista del docente como en la del estudiante.

---

### H3 — `eliminar_actividad` no toma el advisory lock: carrera con el upsert de notas

- **Archivo:** `Backend/app/services/calificacion.py`
- **Línea:** 233
- **Categoría:** concurrencia

**Resumen.** `eliminar_actividad` borra las notas sin tomar el `pg_advisory_xact_lock` que sí usa `_preparar_nota`, de modo que un upsert concurrente puede insertar una nota para la actividad que se está eliminando.

**Escenario de falla.** Petición A: `DELETE /api/actividades/7` selecciona y borra las notas de la actividad 7. Petición B, en paralelo: `PUT /api/notas` con `id_actividad=7` toma el advisory lock, no encuentra nota existente e inserta una, tomando un FK-share lock sobre la fila 7 de `actividadevaluativa`. El `DELETE FROM actividadevaluativa` de A se bloquea y falla con violación de llave foránea cuando B hace commit → `IntegrityError` no capturado → HTTP 500. El módulo introdujo los advisory locks (`_bloquear_nota`, líneas 125-132, RN-f) precisamente para serializar el par `(id_actividad, id_estudiante)`; la ruta nueva de borrado se salta esa protección.

**Corrección sugerida.** Tomar el mismo lock antes de borrar, sobre el `id_actividad` afectado. Como el borrado abarca a todos los estudiantes, sirve un lock por actividad con la segunda clave fija:

```python
self.session.execute(
    text("SELECT pg_advisory_xact_lock(:id_actividad, 0)"),
    {"id_actividad": actividad.id_actividad},
)
```

y hacer que `_bloquear_nota` documente esa convención, o bien tomar el lock por cada `(id_actividad, id_estudiante)` de las notas que se van a borrar antes de eliminarlas.

---

### H4 — Las rutas nuevas de borrado no hacen `rollback` ante fallo

- **Archivo:** `Backend/app/services/calificacion.py`
- **Línea:** 235 (y 258 para `eliminar_seccion`)
- **Categoría:** manejo de errores

**Resumen.** Ni `eliminar_actividad` ni `eliminar_seccion` envuelven su `flush`/`commit` en `try/except` con `rollback`, a diferencia del resto de las rutas de escritura del proyecto.

**Escenario de falla.** Si `session.delete`/`flush` lanza `IntegrityError` —por la carrera de **H3**, o por una actividad de la sección que `actividad_repo.listar` no devolvió, lo que hace que SQLAlchemy emita `UPDATE actividadevaluativa SET id_seccion = NULL` contra una columna `NOT NULL`— la excepción escapa como un 500 pelado, con la transacción en estado fallido y sin rollback. Comparar con `repositories/curso.py:14-22` y `repositories/matricula.py:10-18`, que ambos hacen `except Exception: self.session.rollback(); raise`.

**Corrección sugerida.** Envolver el bloque de escritura en ambos métodos:

```python
try:
    self.nota_repo.borrar_por_actividad(actividad.id_actividad)
    self.actividad_repo.borrar(actividad)
    self.session.commit()
except Exception:
    self.session.rollback()
    raise
```

Idealmente moviendo el `rollback` a los repositorios `borrar` para que la convención quede en un solo lugar.

---

### H5 — Regresión: las actividades sin calificar pierden el marcador «—»

- **Archivo:** `Frontend/src/modules/calificaciones/components/SeccionPanel.jsx`
- **Línea:** 242
- **Categoría:** regresión (afecta HU10, ya marcada ✅)

**Resumen.** Cambiar la guarda de `notaPorActividad &&` a `nota &&` elimina el badge «—» que el estudiante veía antes en las actividades todavía sin nota.

**Escenario de falla.** El estudiante expande una sección con 3 actividades y solo la primera está calificada. Antes: las actividades 2 y 3 renderizaban `claseBadge(undefined)` = `"empty"` y `formatearNota(undefined)` = `"—"`, señalando visualmente «aún sin calificar». Ahora todo el fragmento se omite, así que esas filas muestran solo nombre y fecha, indistinguibles de una interfaz que falló al cargar la nota. Esto degrada HU10 («consultar mis calificaciones… para conocer mi desempeño»), que ya está marcada ✅ en el documento de asignaciones.

**Corrección sugerida.** Separar las dos condiciones: el badge siempre se renderiza, el comentario solo si existe.

```jsx
{notaPorActividad && (
  <span className={`cal-badge ${claseBadge(nota?.calificacion)}`}>
    {formatearNota(nota?.calificacion)}
  </span>
)}
{nota?.comentario && (
  <p className={`cal-actividad-comment${readOnly ? " read-only" : ""}`} /* … */>
    {nota.comentario}
  </p>
)}
```

---

### H6 — `comentarios[index]` lanza `IndexError` con más de 3 estudiantes

- **Archivo:** `Backend/app/tests/prueba_modulo_calificaciones.py`
- **Línea:** 231
- **Categoría:** corrección

**Resumen.** `comentarios[index]` indexa una lista de 3 elementos escrita a mano usando la posición del estudiante, así que cualquier curso con más de 3 estudiantes lanza `IndexError`.

**Escenario de falla.** Se agrega un cuarto estudiante a cualquier entrada de `COURSES` (p. ej. `estudiante1d_notas@colegio.edu.co`). En la cuarta iteración `index == 3` y `comentarios[3]` lanza `IndexError`, abortando la carga a mitad del curso y dejando la base de datos con secciones y actividades pero sin notas. La lista además se reconstruye desde cero en cada iteración de estudiante en lugar de estar izada fuera del bucle.

**Corrección sugerida.** Izar la lista fuera del bucle y ciclarla con módulo, o derivar el comentario de la nota:

```python
COMENTARIOS = ["Buen trabajo", "Debe mejorar la argumentación", "Entrega incompleta"]
...
comentario = COMENTARIOS[index % len(COMENTARIOS)]
```

---

### H7 — Los fallos al crear matrícula se silencian y el script reporta éxito

- **Archivo:** `Backend/app/tests/prueba_modulo_calificaciones.py`
- **Línea:** 185
- **Categoría:** manejo de errores

**Resumen.** `except Exception: session.rollback()` se traga cualquier fallo de creación de matrícula, así que los estudiantes quedan cargados sin matrícula y luego desaparecen de la tabla de notas del docente.

**Escenario de falla.** `crear_matricula` lanza `HTTPException 409` cuando el estudiante ya tiene *cualquier* matrícula para ese año (`repositories/curso.py:214-216` valida por estudiante + año, no por estudiante + grado + año), mientras que `obtener_o_crear_matricula` solo busca por estudiante + grado + año. Cualquier solapamiento produce un 409 silenciado, el script imprime un limpio «Datos finales cargados correctamente», y `TablaNotas` muestra después «No hay estudiantes matriculados en el grado de este curso» porque `listar_estudiantes_de_grado` hace join con `Matricula`. Fallo de carga de datos silencioso con mensaje de éxito.

**Corrección sugerida.** No capturar de forma genérica: distinguir el 409 esperado (idempotencia de la carga) de cualquier otro error, y en el resto propagar:

```python
except HTTPException as exc:
    session.rollback()
    if exc.status_code != status.HTTP_409_CONFLICT:
        raise
    print(f"  · matrícula ya existente para {correo}, se reutiliza")
```

y al final del script, verificar que cada estudiante creado tenga matrícula antes de imprimir el mensaje de éxito.

---

### H8 — Las rutas DELETE nuevas no acotan el id (`gt=0, le=ID_MAXIMO`)

- **Archivo:** `Backend/app/routers/calificacion.py`
- **Línea:** 56 (y 67)
- **Categoría:** validación de entrada

**Resumen.** Las dos rutas DELETE nuevas reciben `id_actividad: int` / `id_seccion: int` pelados, sin la cota `gt=0, le=ID_MAXIMO` que sigue toda ruta del archivo.

**Escenario de falla.** `DELETE /api/actividades/99999999999999` llega a la base de datos con un valor por encima del `INTEGER` de Postgres; psycopg lanza `NumericValueOutOfRange` y el cliente recibe un 500 en lugar de 422/404. `schemas/calificacion.py:6` documenta exactamente por qué existe `ID_MAXIMO` («Postgres INTEGER (4 bytes) es el tipo de todas las columnas id_* de este módulo») y las líneas 29, 47-51, 105 y 113-114 lo aplican. Los ids cero y negativos también pasan de largo.

**Corrección sugerida.**

```python
from fastapi import Path

@router.delete("/actividades/{id_actividad}", status_code=204)
def eliminar_actividad(
    id_actividad: int = Path(gt=0, le=ID_MAXIMO),
    ...
```

Igual para `/secciones/{id_seccion}`, y aprovechar para acotar también `id_materia` en `/materia/{id_materia}/promedio-grupal` (línea 127), que arrastra el mismo problema.

---

### H9 — Dos endpoints de borrado en cascada sin ninguna prueba

- **Archivo:** `Backend/app/tests/prueba_modulo_calificaciones.py`
- **Línea:** 263
- **Categoría:** cobertura de pruebas

**Resumen.** La reescritura elimina la verificación de upsert (RN-f) y no agrega ninguna cobertura para los dos endpoints destructivos nuevos ni para `PUT /notas`; el archivo pasa de ser un script que verifica a ser un sembrador de datos sin una sola aserción.

**Escenario de falla.** El script anterior recargaba una nota para el mismo par `(estudiante, actividad)` e imprimía `Notas después del upsert (N — debe seguir siendo M)` como comprobación explícita de idempotencia, documentada como la compuerta end-to-end en `SPEC/4-summary-registro-calificaciones.md:65`. Eso desapareció. Un `grep` sobre `Backend/app/tests/` no encuentra referencia alguna a `eliminar_actividad`, `eliminar_seccion`, `DELETE /api/actividades`, `DELETE /api/secciones` ni `PUT /api/notas`: dos endpoints irreversibles y en cascada se integran sin prueba. Una regresión que borrara las notas de la sección equivocada pasaría el CI sin ruido.

**Corrección sugerida.** Restaurar la verificación de upsert y añadir, como mínimo, tres comprobaciones: (a) al borrar una actividad desaparecen sus notas y ninguna otra; (b) al borrar una sección desaparecen sus actividades y sus notas y ninguna otra; (c) el borrado devuelve 400 con periodo cerrado y 403 para un docente que no dicta el curso.

---

### H10 — `PUT /api/notas` es un duplicado literal de `POST /api/notas`

- **Archivo:** `Backend/app/routers/calificacion.py`
- **Línea:** 93
- **Categoría:** simplificación / diseño de API

**Resumen.** `PUT /api/notas` es una copia textual de `POST /api/notas` —mismo tipo de payload, misma llamada al servicio, mismo guard de rol—, así que el endpoint no aporta comportamiento y además crea filas en un `PUT`.

**Escenario de falla.** Ambos handlers ejecutan `service.crear_nota(payload.id_actividad, payload.id_estudiante, payload.calificacion, payload.comentario, usuario)`. HU15 («modificar las notas») ya estaba satisfecha por el `POST`, cuyo `_preparar_nota` hace upsert. El resultado son dos rutas que mantener, dos lugares donde una regla futura puede divergir, un `PUT` que devuelve 200-con-creación en lugar de 201/404, y ninguna forma de distinguir «actualizar una nota existente» de «crear».

**Corrección sugerida.** Darle a `PUT` semántica real de actualización, con el id de la nota en la ruta, y dejar `POST` solo para creación:

```python
@router.put("/notas/{id_nota}", response_model=NotaResponse)
def actualizar_nota(
    payload: NotaUpdate,                      # calificacion + comentario
    id_nota: int = Path(gt=0, le=ID_MAXIMO),
    ...
):
    return service.actualizar_nota(id_nota, payload.calificacion, payload.comentario, usuario)
```

donde `actualizar_nota` devuelve 404 si `buscar_por_id` no encuentra nada. Alternativa mínima, si se quiere conservar el upsert por par: eliminar el `PUT` y volver a `registrarNota` en el frontend, que es lo que ya funcionaba.

---

### H11 — `registrarNota` queda sin ningún llamador

- **Archivo:** `Frontend/src/modules/calificaciones/services/calificacionService.js`
- **Línea:** 74
- **Categoría:** código muerto

**Resumen.** `registrarNota` queda como código muerto cuando `TablaNotas` pasa a `actualizarNota`, pero sigue exportada, dejando `POST /api/notas` sin ningún llamador en el frontend.

**Escenario de falla.** Un `grep` sobre `Frontend/src` encuentra `registrarNota` solo en su definición (línea 74) y en su export (línea 134): cero sitios de uso. La función y el endpoint que envuelve quedan alcanzables únicamente desde el script de pruebas, así que una rotura futura en `POST /api/notas` no la detectaría ningún flujo de la interfaz, mientras la función sigue siendo superficie pública del módulo de servicios.

**Corrección sugerida.** Depende de cómo se resuelva **H10**: si `PUT` pasa a ser actualización por id, `registrarNota` vuelve a tener sentido para la creación y `TablaNotas` debe elegir entre las dos según exista o no nota en la celda. Si se elimina el `PUT`, borrar `actualizarNota` y volver a `registrarNota`. En cualquier caso, no dejar las dos exportadas con una sin uso.

---

### H12 — `borrar_por_actividad` emite un `DELETE` por fila

- **Archivo:** `Backend/app/repositories/nota.py`
- **Línea:** 94
- **Categoría:** eficiencia

**Resumen.** `borrar_por_actividad` carga todas las notas en la sesión y emite un `DELETE` por fila, y `eliminar_seccion` repite eso por cada actividad, donde bastarían dos sentencias masivas.

**Escenario de falla.** Borrar una sección con 3 actividades y 30 estudiantes matriculados ejecuta 3 `SELECT` más ~90 `DELETE` individuales más 6 `flush`, todo dentro de una sola petición. Un `delete(Nota).where(Nota.id_actividad.in_([...]))` seguido de `delete(ActividadEvaluativa).where(ActividadEvaluativa.id_seccion == id)` hace el mismo trabajo en dos idas y vueltas. El costo escala con el tamaño del curso, que es justo la dimensión que crece en producción.

**Corrección sugerida.**

```python
from sqlalchemy import delete

def borrar_por_actividades(self, ids_actividad: list[int]) -> int:
    if not ids_actividad:
        return 0
    resultado = self.session.execute(
        delete(Nota).where(Nota.id_actividad.in_(ids_actividad))
    )
    self.session.flush()
    return resultado.rowcount
```

Nota: con `delete()` masivo hay que pasar `synchronize_session=False` o expirar la sesión si las notas ya estaban cargadas en el identity map.

---

### H13 — El popup de comentario reimplementa el modal existente y pierde semántica de diálogo

- **Archivo:** `Frontend/src/modules/calificaciones/components/SeccionPanel.jsx`
- **Línea:** 307
- **Categoría:** reutilización / accesibilidad

**Resumen.** El popup de comentario construye un modal a mano, con una familia de clases `cal-popup-*` nueva, en lugar de reutilizar el patrón de modal ya existente en el módulo, y descarta la semántica de diálogo que el resto del archivo sí aporta.

**Escenario de falla.** `Calificaciones.css:264-315` ya define `.cal-modal-overlay`, `.cal-modal`, `.cal-modal-header`, `.cal-modal-title`, `.cal-modal-close` y `.cal-modal-actions`, usadas por `ActividadModal.jsx` y `CargaMasivaModal.jsx`. El diff añade ~40 líneas de CSS casi idéntico más el JSX inline, así que el estilo del overlay pasa a tener dos fuentes de verdad. El diálogo nuevo tampoco tiene `role="dialog"`, ni `aria-modal`, ni manejo de `Escape`, ni gestión de foco, mientras el mismo archivo sí se toma el trabajo de dar `role`/`tabIndex`/`onKeyDown` a `cal-seccion-header` (líneas 199-209): un usuario de teclado que abre el comentario no puede cerrarlo sin tabular hasta la «×».

**Corrección sugerida.** Extraer el patrón a un componente `ModalBase` reutilizado por los tres modales, o como mínimo reutilizar las clases `cal-modal-*` y añadir al popup `role="dialog"`, `aria-modal="true"`, cierre con `Escape` y foco inicial en el botón de cerrar.

---

### H14 — `eliminar_seccion` duplica la validación de periodo abierto

- **Archivo:** `Backend/app/services/calificacion.py`
- **Línea:** 246
- **Categoría:** reutilización

**Resumen.** `eliminar_seccion` reimplementa la regla de periodo abierto en línea en lugar de reutilizar `_validar_periodo_abierto`, duplicando tanto la condición como el mensaje de error.

**Escenario de falla.** La comparación `periodo.estado != "Abierto"` y el mensaje «El período académico de este curso no está abierto» existen ahora en dos lugares (líneas 121-123 y 246-248). HU13 y HU18 tratan precisamente de endurecer esta regla para cortes y años finalizados; el próximo cambio sobre ella —por ejemplo bloquear también «En revisión», o pasar a una validación por rango de fechas— se aplicará a `_validar_periodo_abierto` y omitirá silenciosamente `eliminar_seccion`.

**Corrección sugerida.** Extraer la validación al nivel del curso y hacer que la variante de actividad delegue:

```python
def _validar_periodo_abierto_curso(self, curso: Curso) -> None:
    if curso.periodo.estado != "Abierto":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="El período académico de este curso no está abierto")

def _validar_periodo_abierto(self, actividad: ActividadEvaluativa) -> None:
    self._validar_periodo_abierto_curso(actividad.seccion.curso)
```

---

### H15 — BOM UTF-8 agregado al inicio del archivo Python

- **Archivo:** `Backend/app/tests/prueba_modulo_calificaciones.py`
- **Línea:** 1
- **Categoría:** corrección / higiene

**Resumen.** Se agregó por accidente un BOM UTF-8 (`EF BB BF`) al comienzo del archivo fuente.

**Escenario de falla.** `head -c 20 | xxd` confirma que el archivo ahora empieza con `efbb bf66 726f 6d20` en lugar de `from`. CPython tolera un BOM inicial, pero rompe cualquier herramienta que lea el archivo como UTF-8 plano o compare bytes de la primera línea, agrega ruido permanente al `git diff` de la línea 1, y rompe heredocs de shell y las invocaciones tipo `python - < archivo`. Nada en el cambio requería tocar la codificación.

**Corrección sugerida.**

```bash
sed -i '1s/^\xEF\xBB\xBF//' Backend/app/tests/prueba_modulo_calificaciones.py
```

y configurar el editor para guardar UTF-8 sin BOM.

---

## 4. Qué falta para completar las historias

Esta sección lista el trabajo pendiente, separado por capa, para que HU11, HU15 y HU16 puedan marcarse ✅.

### 4.1 HU11 — Detalle de la calificación para el estudiante

**Backend**

| Pendiente | Detalle |
|---|---|
| Exponer el estudiante asociado en la respuesta | `NotaResponse` (`schemas/calificacion.py:47-54`) solo devuelve ids. Agregar `nombre_estudiante` (y opcionalmente `nombre_actividad`, `porcentaje_seccion`) para que la vista no tenga que resolver esos datos por su cuenta. |
| Evitar el N+1 de la vista del estudiante | `EstudianteCalificaciones.jsx:34` hace `lista.map((act) => listarNotas(act.id_actividad))`: una petición HTTP por actividad. Ya existía antes de la rama, pero es el mismo endpoint que HU11 necesita. Conviene aceptar `id_seccion` en `GET /api/notas` (o añadir `GET /api/notas/mis-calificaciones`) para traer todas las notas de la sección en una sola llamada, respetando RN-04. |
| Cobertura | Una prueba que verifique que el estudiante recibe `comentario` y que **no** recibe notas de otros estudiantes (RN-04) sobre el mismo endpoint. |

**Frontend**

| Pendiente | Detalle |
|---|---|
| Mostrar el estudiante asociado | Es el quinto dato exigido por la historia y hoy no aparece. Lo más simple: rotular la vista con el nombre del usuario autenticado (`useAuth().user`) en el encabezado de `EstudianteCalificaciones.jsx:138`, o mostrarlo en el popup de detalle junto con la nota y el porcentaje. |
| Revertir la regresión del «—» | Ver **H5**. |
| Arreglar el CSS muerto | Ver **H2**; hasta entonces el layout de tres columnas no existe. |
| Accesibilidad y reutilización del popup | Ver **H13**. |
| Porcentaje a nivel de cada calificación | Hoy el porcentaje solo se ve en el encabezado de la sección. Si se interpreta la historia al pie de la letra («el porcentaje… a cada calificación»), el popup de detalle debería mostrar el porcentaje de la sección a la que pertenece esa nota. |
| Marcar la historia | Actualizar HU11 en `docs/historias-de-usuario-y-asignaciones.md:25` solo cuando lo anterior esté cerrado. |

### 4.2 HU15 — El profesor modifica notas del periodo actual

**Backend**

| Pendiente | Detalle |
|---|---|
| Semántica real de actualización | Ver **H10**: `PUT /api/notas/{id_nota}` con 404 si la nota no existe, y un `NotaUpdate` que solo lleve `calificacion` y `comentario`. Hoy `PUT` y `POST` son indistinguibles. |
| Cota de id en la ruta | `Path(gt=0, le=ID_MAXIMO)` como el resto del archivo (ver **H8**). |
| Pruebas | Modificar una nota existente y verificar que **no** se crea una fila nueva; verificar 400 con periodo cerrado (RN-d) y 403 para docente ajeno al curso (RN-03) sobre la ruta de modificación. |

**Frontend**

| Pendiente | Detalle |
|---|---|
| Un solo camino de guardado | Resolver el código muerto de **H11** y decidir en `TablaNotas.guardarNota` entre crear (`POST`) y actualizar (`PUT /{id_nota}`) según exista nota en la celda. |
| Confirmación visible de la modificación | La celda actualiza el estado local pero no distingue «guardado» de «sin cambios»; un aviso breve tras el `PUT` cierra la historia desde la perspectiva del docente. |

### 4.3 HU16 — El profesor elimina notas del periodo actual

Es la historia que falta por completo. El trabajo mínimo:

**Backend**

| Pendiente | Detalle |
|---|---|
| `NotaRepository.borrar(nota)` | Borrado de una nota individual con `rollback` en el `except`, siguiendo la convención de `repositories/curso.py:14-22`. Ver **H1**. |
| `CalificacionService.eliminar_nota(id_nota, usuario)` | Con las cuatro validaciones del módulo: existencia (404), pertenencia del curso (RN-03), periodo abierto (RN-d) y advisory lock (RN-f). Ver **H1**. |
| `DELETE /api/notas/{id_nota}` | `status_code=204`, `require_role("Administrador", "Docente")`, `Path(gt=0, le=ID_MAXIMO)`. |
| Rótulo del código | La sección `# --- Eliminaciones (HU16) ---` debe cubrir efectivamente HU16 o cambiar de nombre. |
| Pruebas | Borrar una nota y verificar que solo desaparece esa; 400 con periodo cerrado; 403 para docente ajeno; 404 con id inexistente. |

**Frontend**

| Pendiente | Detalle |
|---|---|
| `eliminarNota(idNota)` en el servicio | Envolviendo `api.delete('/api/notas/${idNota}')` con el mismo manejo de error que el resto del archivo. |
| Botón «Eliminar nota» en la celda | En el editor de celda de `TablaNotas.jsx` (junto a guardar/cancelar), visible solo si la celda ya tiene nota y `periodoAbierto`, con `window.confirm` y limpieza de `notas[claveNota(...)]` en el estado tras el 204. |
| Diferenciar de la eliminación de actividad | La «×» de la actividad y el botón de sección borran en cascada. Su confirmación debería indicar cuántas notas se van a perder, para que no se usen como sustituto de borrar una nota. |

### 4.4 Pendientes transversales

- **Documentación de especificación.** La rama no aporta el par `SPEC/N-spec-*.md` / `N-summary-*.md` que acompaña a todas las funcionalidades previas (ver `SPEC/`, con numeración hasta `9-*`). Corresponde un `10-spec-hu11-hu15-hu16-*.md` con las reglas de negocio del borrado.
- **Funcionalidad no mapeada.** La eliminación de actividades y secciones para el docente no corresponde a ninguna de las 24 historias del documento. Si el equipo la quiere conservar, debe registrarse como historia nueva; si no, es alcance no solicitado.
- **Estado en el documento de asignaciones.** HU11, HU15 y HU16 siguen ⬜, lo cual hoy es correcto: ninguna está terminada.
