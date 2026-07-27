# Spec HU22 — Importar notas desde un archivo Excel

**Historia de usuario:** HU22 — *Como profesor, quiero importar notas desde un archivo Excel, para registrar calificaciones de forma masiva y eficiente.*
**Requerimiento funcional:** RF-11 — *Importar notas masivamente desde archivo Excel (.xlsx); el sistema valida el formato y reporta errores.*

**Owner:** Mariana
**Sprint:** 3
**Fecha:** 2026-07-27
**Repo:** `Saanhevi/Sistema-de-seguimiento-academico`
**Rama sugerida:** `feat/importar-notas-excel` (desde `main`)
**Complementa:** [`4-spec-registro-calificaciones.md`](4-spec-registro-calificaciones.md) (backend de calificaciones) y [`7-spec-frontend-calificaciones.md`](7-spec-frontend-calificaciones.md) (frontend docente)

---

## 1. Objetivo

Permitir que un docente suba un archivo `.xlsx` con las notas de una actividad y que el sistema:

1. lo interprete,
2. resuelva a qué estudiante corresponde cada fila,
3. le muestre una **vista previa** de lo que se va a guardar y un **reporte de errores** fila por fila,
4. y, solo si el docente confirma, persista las notas reutilizando la carga masiva que ya existe.

El spec 4 ya dejó anticipada esta historia (§3): *«el endpoint de carga masiva que se define aquí es el mismo que después recibiría las filas ya parseadas de un Excel»*. Este spec cumple esa promesa: **HU22 no reimplementa la escritura de notas**, solo la traducción de Excel → payload.

---

## 2. Los datos del estudiante: qué contempla HU22 y qué no

**Resumen: HU22 debe *identificar* estudiantes, nunca *crearlos ni matricularlos*. Y para identificarlos hace falta un dato que hoy no existe en la base de datos: el número de identificación.**

### 2.1 Por qué no se crean estudiantes

| Motivo | Evidencia |
|---|---|
| El requerimiento acota el alcance a notas | RF-11 dice «Importar **notas** masivamente». No menciona estudiantes. |
| Crear cuentas es del administrador | RF-04: «Crear, editar y eliminar cuentas de estudiantes y profesores» está bajo *Administrador institucional*. |
| Ya hay una historia dueña de eso | **HU20** — «Como administrador del colegio, quiero agregar nuevos estudiantes al sistema» — Sprint 3, **responsable Santiago**. |
| Matricular es de otra historia todavía | **HU2** (asignar estudiantes a un grado) y **HU12** (añadir estudiantes a mi materia). |
| Rompería RBAC | RNF-03: «ningún usuario puede operar fuera de su rol». Un docente subiendo un `.xlsx` que da de alta cuentas es escalada de privilegios por la puerta de atrás: crearía filas en `Usuario` + `Estudiante` + `Matricula` sin pasar por ningún control del administrador. |
| Es irreversible desde el producto | HU19 (eliminar estudiantes) también es de Santiago y está en ⬜. Un error de tipeo en un correo crearía una cuenta fantasma que nadie puede borrar desde la interfaz. |

### 2.2 El problema de identidad que HU22 **tiene que resolver**

El Excel de un docente identifica a sus estudiantes por nombre y por documento. La base de datos no puede hacer ni lo uno ni lo otro:

```sql
-- Database/schemas.sql:1
CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,     -- ← sin UNIQUE
    apellidos VARCHAR(100) NOT NULL,   -- ← sin UNIQUE
    correo VARCHAR(100) NOT NULL UNIQUE,
    ...
```

**No existe columna de documento de identidad**, y la única clave natural única es `correo`. Emparejar por `nombres + apellidos` es ambiguo por diseño del esquema: dos «Juan Pérez» en el mismo grado son perfectamente válidos, y asignarle la nota del uno al otro es un daño silencioso peor que rechazar la fila.

El correo funciona como clave técnica —y es la que usa la plantilla que genera el sistema (§7.2)—, pero no resuelve el otro camino: la planilla que un docente ya lleva en Excel tiene documento y nombre, casi nunca el correo institucional. Para ese archivo, hoy no hay con qué emparejar.

### 2.3 Decisión: se agrega el número de identificación

**Se añade la columna `documento` al modelo de usuario.** El detalle del cambio de esquema está en §3; las decisiones que ese cambio abre y hay que cerrar en el standup, en §12.A.

Con eso, la precedencia de emparejamiento queda (RN-j):

```
id_estudiante   →   documento   →   correo
(solo si el          (lo que el      (la clave que trae la
 docente lo trae      docente ya      plantilla del sistema,
 en su archivo)       tiene)          §7.2)
```

Cada clave cubre un camino distinto, y por eso conviven las tres:

- **`correo`** — lo que trae la plantilla del sistema (§7.2). Es el flujo principal y funciona desde el día uno.
- **`documento`** — lo que trae la planilla propia del docente. Es la razón de ser de este cambio de esquema.
- **`id_estudiante`** — solo si el docente lo agrega a mano; el sistema no lo exporta.

Como `documento` está vacío para todos los usuarios ya creados (§3.4), la importación no depende de él para funcionar: degrada al correo sin que nadie tenga que terminar de cargar los documentos del colegio primero.

**No se empareja por nombre**, ni siquiera teniendo documento (ver §12.B, pregunta 1).

> **El equipo ya daba por hecho este dato.** `Frontend/src/modules/dashboard/pages/docente/DocenteEstudiantes.jsx:255` — la interfaz de HU12, de Rafael — tiene un buscador cuyo marcador de posición dice **«Nombre o documento»**, pero el filtro de la línea 153 solo compara contra el nombre, porque el documento no existe en ninguna respuesta de la API. La interfaz ya promete algo que el esquema no puede cumplir; este cambio también cierra ese hueco.

### 2.4 Cómo se evita que el emparejamiento sea incómodo para el docente

Con el endpoint de **plantilla** (§8.1, `GET /api/notas/plantilla-excel`): el sistema genera el `.xlsx` ya con la lista de estudiantes del curso (nombre, apellido y **correo**) y una columna `calificacion` vacía. El docente solo escribe las notas y el correo hace el emparejamiento. Así deja de ser un problema en el flujo principal, y `documento`/`id_estudiante` quedan como red de seguridad para los archivos que el docente arma por su cuenta.

La lista sale de `GET /api/grados/{id_grado}/estudiantes?anio=` (`CursoService.listar_estudiantes_por_grado`), la misma fuente que usa `TablaNotas.jsx`, así que la plantilla y la tabla de notas muestran siempre la misma gente. Ese endpoint ya devuelve `correo`, así que la plantilla no necesita nada nuevo; se le agrega `documento` igualmente, para el emparejamiento del lado servidor y para el buscador de HU12 (§3.3).

### 2.5 Qué pasa con las filas de estudiantes desconocidos

Se reportan como error de fila, con mensaje accionable, y **no se escribe nada de ellas**:

| Situación | Mensaje al docente |
|---|---|
| El documento/correo no existe en el sistema | `No hay ningún estudiante registrado con el documento X. Pídele al administrador que cree la cuenta.` |
| Existe pero no está matriculado en el grado/año del curso | `X no está matriculado en el grado de este curso para el año N.` |
| Existe pero no tiene rol Estudiante | `X no es una cuenta de estudiante.` |
| Existe pero su ficha no tiene documento cargado | `X está registrado pero no tiene documento en el sistema. Usa el correo en esa fila, o pídele al administrador que complete su ficha.` |

### 2.6 Nota para el equipo (Santiago)

Si más adelante el equipo quiere **importar estudiantes desde Excel**, eso es una historia nueva colgando de HU20, con actor Administrador, no un ensanchamiento de HU22. El parser de este spec queda deliberadamente aislado en `services/importacion_excel.py` sin ninguna dependencia de notas ni de la BD (§9), justamente para que esa historia lo reutilice tal cual.

---

## 3. Cambio de esquema: `Usuario.documento`

Este es el único cambio de este spec que **sale de los límites del módulo de calificaciones**: toca una tabla que usan todos. Va en su propio commit, antes que nada.

### 3.1 La columna — decidido

```sql
-- Database/schemas.sql, dentro de CREATE TABLE Usuario
documento VARCHAR(20) UNIQUE,
```

| Decisión | Estado | Por qué |
|---|---|---|
| En **`Usuario`**, no en `Estudiante` | ✅ Decidido | Docentes y administradores también tienen documento. HU5 y HU21 lo van a querer, y el buscador de HU12 ya lo insinúa. En `Estudiante` habría que duplicar la columna en la primera historia que lo pida para otro rol. |
| **`VARCHAR(20)`**, nunca `INTEGER` | ✅ Decidido | (a) Los documentos llevan ceros a la izquierda y un `INTEGER` los borra. (b) Cédulas de extranjería y pasaportes llevan letras. (c) Nadie hace aritmética con un documento. (d) **Excel:** una celda numérica de 10 dígitos vuelve como `float` (`1023456789.0`) y los más largos salen en notación científica (`1,02E+09`). Guardando texto se conserva lo que la persona escribió. |
| **`UNIQUE` pero *nullable*** | ✅ Decidido | Postgres permite muchos `NULL` dentro de un `UNIQUE`: la columna se agrega sin tocar las filas existentes. Con `NOT NULL` el `ALTER TABLE` falla en cuanto haya un usuario creado. Sin `UNIQUE` no sirve para emparejar, que es justo para lo que se agrega. |
| **Sin `tipo_documento`** (TI / CC / CE / Pasaporte) | ✅ Decidido — no por ahora | Añadiría una columna y un `CHECK` que ninguna historia usa todavía. Si el colegio lo pide después, es una segunda migración de una línea. |

> **Sobre el cambio de TI a CC a los 18 años:** el número del documento cambia, pero las notas ya guardadas se referencian por `id_estudiante` en la base de datos, así que no se rompen. Basta con que el administrador pueda editar el documento (HU20). No hay nada que construir aquí.

### 3.2 Cómo se aplica — decidido: script `ALTER`

No hay Alembic en `requirements.txt`, y `Database/schemas.sql` **solo se ejecuta la primera vez que se crea el volumen de Postgres** (README, §2): un `docker compose up` sobre un volumen existente no aplica nada.

```sql
-- Database/migraciones/001-usuario-documento.sql
ALTER TABLE Usuario ADD COLUMN IF NOT EXISTS documento VARCHAR(20);
CREATE UNIQUE INDEX IF NOT EXISTS usuario_documento_key ON Usuario (documento);
```

```bash
docker compose exec -T db psql -U postgres -d gestion_academica < Database/migraciones/001-usuario-documento.sql
```

El cambio va **también** a `Database/schemas.sql`, para que las instalaciones nuevas nazcan con la columna. **En ambos sitios**, o el equipo termina con dos esquemas distintos según cuándo clonó.

`IF NOT EXISTS` en las dos sentencias: la migración se puede correr dos veces sin fallar, que es lo que va a pasar cuando alguien no recuerde si ya la corrió.

> Como el proyecto está en desarrollo y nadie depende de los datos, `docker compose down -v` también sirve. El script se agrega igual porque es lo que se va a necesitar la próxima vez, cuando sí haya datos.
>
> **Aviso al equipo:** quien haga `git pull` sin correr la migración verá `UndefinedColumn` en cualquier consulta que toque `Usuario` — o sea, **en el login**. Mariana avisa por el grupo al mergear.

### 3.3 Qué más hay que tocar para que la columna sirva

Agregar la columna no basta: hay que capturarla y exponerla. **La captura entra en el alcance de este spec** (decisión: se agrega al formulario de registro, no se delega).

| Archivo | Cambio | Dueño |
|---|---|---|
| `Backend/app/models/usuario.py` | Campo `documento` en el modelo ORM | Este spec |
| `Backend/app/schemas/auth.py` | `CrearCuentaEstudiantilRequest` agrega `documento: str` | Este spec |
| `Backend/app/services/auth.py` | `crear_cuenta_estudiantil` lo guarda en el `Usuario` que crea | Este spec |
| `Frontend/src/modules/auth/components/RegisterForm.jsx` | Campo «Número de documento» + su `useState`, y va en el payload de `registrar()` | Este spec |
| `Backend/app/services/curso.py:227` | `listar_estudiantes_por_grado` agrega `Usuario.documento` al `SELECT` y al dict de retorno | Este spec |
| `Backend/app/schemas/curso.py` | El schema de estudiante-de-grado incluye `documento: Optional[str]` | Este spec |
| HU20 «agregar nuevos estudiantes» | El alta por administrador debería capturarlo también | **Santiago** — coordinar |
| HU5 / HU21 (profesores) | Si se decide que aplica a docentes | **Samuel** — coordinar |

#### El formulario de registro (HU0a)

`RegisterForm.jsx` hoy tiene cuatro campos: nombres, apellidos, correo, contraseña. Se agrega un quinto.

Validación mínima, en el schema Pydantic y no en el router:

```python
documento: str = Field(min_length=5, max_length=20, pattern=r"^[0-9A-Za-z]+$")
```

- **Normalizado antes de guardar** con la misma función de RN-r (quitar espacios, puntos y guiones), para que el documento que se guarda tenga exactamente la misma forma que el que va a llegar desde un Excel. Si se guarda `1.023.456.789` y se busca `1023456789`, no empareja nunca — y el fallo es invisible.
- **Duplicado → 409**, no un 500 por violación de `UNIQUE`. `crear_cuenta_estudiantil` ya hace esa comprobación previa para el correo (`services/auth.py`); se replica para el documento con el mismo patrón.

> **Nota de alcance:** el campo se agrega **obligatorio en el formulario** pero la columna sigue siendo *nullable* en la base de datos. No es contradictorio: los usuarios que ya existen no tienen documento y no se les puede inventar uno. Obligarlo en la BD exigiría rellenar filas con datos falsos, que es peor que una columna con `NULL` honestos.

### 3.4 La columna nace vacía, y eso está bien

Ningún usuario existente tiene documento, y HU22 no puede llenárselo (eso sería editar datos del estudiante, §2.1). Solo lo tendrán los que se registren después del cambio. Por eso la precedencia de §2.3 mantiene `correo` como respaldo: **HU22 funciona igual el día uno**, y mejora sola a medida que se registran estudiantes nuevos.

Toda la lógica trata `documento` como opcional, y el mensaje de error de §2.5 le dice al docente qué hacer cuando el estudiante existe pero su ficha está incompleta.

---

## 4. Estado actual del que se parte

### Backend (ya en `main`)

| Pieza | Estado |
|---|---|
| `POST /api/notas/carga-masiva` | ✅ Funciona. Recibe `{id_actividad, notas: [{id_estudiante, calificacion, comentario?}]}`, valida todo antes de escribir y hace *upsert* con advisory lock (`services/calificacion.py:167`). **Es el destino final de este spec.** |
| `_validar_pertenencia_curso` (RN-03) | ✅ `services/calificacion.py:29` |
| `_validar_periodo_abierto` (RN-d / RN-01) | ✅ `services/calificacion.py:119` |
| `_validar_estudiante` (RN-e) | ✅ `services/calificacion.py:111` |
| `listar_estudiantes_por_grado` | ✅ `services/curso.py:227`, con el filtro RN-03 por docente ya aplicado |
| Soporte de `multipart/form-data` | ❌ **Falta `python-multipart`** en `requirements.txt` |
| Lectura de `.xlsx` | ❌ **Falta `openpyxl`** en `requirements.txt` |
| `Usuario.documento` | ❌ **No existe.** Se agrega en este spec (§3) |
| `DELETE /api/actividades/{id}`, `DELETE /api/secciones/{id}`, `PUT /api/notas` | ⚠️ Nuevos (HU15/HU16 parciales, merge #24). No afectan a este spec: `carga-masiva` quedó intacto. Ojo al rebase, tocan el mismo router. |

### Frontend (ya en `main`)

| Pieza | Estado |
|---|---|
| `CargaMasivaModal.jsx` | ✅ Modal de carga masiva manual. **Es el modelo visual y de interacción a seguir.** |
| `TablaNotas.jsx` | ✅ Tiene el botón «Carga masiva» por actividad en el `<tfoot>` (línea 236). Ahí va el botón nuevo. |
| `calificacionService.js` | ✅ Ya exporta `cargaMasiva()`, que se reutiliza en el paso de confirmación. |
| `Calificaciones.css` | ✅ Clases `cal-modal`, `cal-table`, `cal-error`, `cal-hint`, `cal-btn` ya existen y se reutilizan. |
| `services/api.js` | ⚠️ El cliente axios fija `Content-Type: application/json` **global**. Ver §10.1. |

---

## 5. Alcance

### 5.1 Incluye (MVP)

- **Columna `documento` en `Usuario`** (§3), su migración, y exponerla en el listado de estudiantes por grado.
- **Capturar el documento en el formulario de registro estudiantil** (`RegisterForm.jsx` + `CrearCuentaEstudiantilRequest`), §3.3.
- Dependencias nuevas en el backend (`openpyxl`, `python-multipart`) y rebuild de la imagen Docker.
- Endpoint de **plantilla**: descarga un `.xlsx` con la lista del curso ya escrita — nombre, apellido y correo, **sin documento** (§7.2).
- Endpoint de **previsualización**: recibe el `.xlsx`, lo valida y devuelve filas válidas + errores. **No escribe en la BD.**
- Modal en el frontend del docente: subir → ver vista previa y errores → confirmar.
- La confirmación reutiliza `POST /api/notas/carga-masiva` tal como está hoy.
- Un formato de archivo: **una actividad por archivo**, la que esté seleccionada en la interfaz.

### 5.2 No incluye

- **Crear, matricular o modificar estudiantes desde el archivo Excel** (§2). Pertenece a HU20 / HU2 / HU12. La importación lee `documento`, nunca lo escribe.
- Capturar `documento` en el alta por administrador (HU20, Santiago) ni en los formularios de profesores (HU5/HU21, Samuel). Este spec solo cubre el registro estudiantil que ya existe.
- Rellenar el documento de los usuarios ya creados. Es trabajo de datos, no de código.
- Crear secciones o actividades a partir del archivo. La actividad se elige en la interfaz y debe existir.
- Formato matriz (una columna por actividad). Ver §13 como extensión natural.
- Formatos `.xls` (Excel 97-2003) y `.csv`. RF-11 dice `.xlsx` explícitamente.
- Importar asistencia desde Excel. No hay requerimiento que lo pida.
- Deshacer una importación ya confirmada. Se corrige recargando el archivo (el upsert de RN-f lo permite) o con HU15/HU16.

---

## 6. Reglas de negocio

Las que ya existen y **se heredan sin reimplementar** (las aplica `cargar_notas_masivo` en la confirmación):

| Regla | Descripción |
|---|---|
| RN-a | `calificacion` entre 0.00 y 5.00. |
| RN-03 / RN-d | El docente solo opera sobre sus cursos, y solo con el periodo `'Abierto'`. |
| RN-e | El estudiante debe existir y tener rol `Estudiante`. |
| RN-f | *Upsert*: reimportar el mismo archivo actualiza, no duplica. |

Las que **agrega este spec**, todas en la fase de previsualización:

| Regla | Descripción |
|---|---|
| **RN-g** | Solo se acepta `.xlsx`. Se valida por contenido (firma ZIP `PK\x03\x04`), no por la extensión del nombre. |
| **RN-h** | Límites duros: **2 MB** de archivo y **1000 filas de datos**. Se comprueba el tamaño *antes* de abrir el archivo (un `.xlsx` es un ZIP y un archivo pequeño puede descomprimirse a gigas). |
| **RN-i** | El archivo debe traer al menos una columna de identidad: `id_estudiante`, `documento` o `correo`. Sin ninguna de las tres → 400, archivo rechazado completo. No se empareja por nombre (§2.2). |
| **RN-j** | Precedencia de emparejamiento, celda por celda: **`id_estudiante` → `documento` → `correo`**. Se usa la primera que esté presente y no vacía en esa fila; si esa falla, la fila es error y **no** se reintenta con la siguiente (probar todas las claves hasta que alguna pegue es cómo se le termina poniendo la nota a otro estudiante). |
| **RN-r** | Normalización del documento antes de comparar, **por ambos lados** (el del archivo y el de la BD): quitar espacios, puntos y guiones (`1.023.456.789` → `1023456789`). Si Excel entrega la celda como número, se convierte a entero antes de pasar a texto, para que `1023456789.0` no termine buscando el documento `"1023456789.0"`. |
| **RN-s** | Un documento que llega en notación científica (`1,02E+09`) **no se adivina**: es error de fila con el mensaje «formatea la columna documento como texto en Excel y vuelve a exportar». Reconstruir el número perdería los dígitos que Excel ya truncó. |
| **RN-t** | El `correo` se normaliza con `strip()` + minúsculas: `Usuario.correo` es `UNIQUE`, pero Postgres compara sensible a mayúsculas y el docente escribe como se le ocurra. |
| **RN-k** | El estudiante debe estar matriculado en el **grado y año del curso de la actividad**. Es el mismo alcance que ve `TablaNotas`: no se pueden importar notas de alguien que no aparece en la tabla. |
| **RN-l** | Celda de calificación vacía → la fila **se omite en silencio**, no es un error. Es la misma convención de `CargaMasivaModal.jsx:27` («los campos vacíos no se envían») y permite subir la plantilla a medio llenar. |
| **RN-m** | Dos filas para el mismo estudiante en el mismo archivo → **ambas son error**, no se aplica ninguna. Elegir «la última» en silencio es adivinar cuál nota quería el docente. |
| **RN-n** | Separador decimal: se aceptan coma y punto (`4,5` y `4.5`). Excel entrega las celdas numéricas como `float`; solo las celdas de texto necesitan esta normalización. |
| **RN-o** | La nota se redondea a **2 decimales** (la columna es `NUMERIC(3,2)`; sin redondear, Postgres lo haría igual pero de forma invisible). El valor redondeado es el que se muestra en la vista previa: lo que el docente aprueba es lo que se guarda. |
| **RN-p** | `comentario` de más de 100 caracteres → error de fila (`Nota.comentario` es `VARCHAR(100)`). Truncar en silencio altera lo que el docente escribió. |
| **RN-q** | **La previsualización no escribe absolutamente nada en la base de datos.** Es un `POST` por el tamaño del cuerpo, no por tener efectos. (Justo el defecto opuesto al hallazgo H5 de `docs/revision-completitud-historias-usuario.md`, donde un `GET` de asistencia sí escribía.) |
| **RN-u** | Se **avisa** de los estudiantes matriculados que el archivo no menciona y que siguen sin nota para esa actividad. No es un error ni bloquea nada: importar media clase es legítimo. Sin este aviso, una fila borrada por accidente es indetectable. |
| **RN-v** | Se permite **confirmar parcialmente**: las filas válidas se guardan aunque otras hayan fallado, siempre con el conteo de lo que queda fuera a la vista. Obligar a corregir el archivo entero por un documento mal escrito hace que el docente abandone la función y vuelva a teclear las notas a mano. |
| **RN-w** | El archivo **no lleva `id_actividad`** ni se le exige. La actividad destino es la seleccionada en la interfaz, y el docente la confirma explícitamente antes de guardar (§10.2). Meter el identificador en el archivo lo vuelve frágil (se copia y pega entre archivos, y deja de coincidir sin que nadie lo note). |

---

## 7. Formato del archivo

### 7.1 Columnas

Encabezados en la **primera fila**. Se leen normalizados: sin espacios sobrantes, en minúsculas y sin tildes.

| Columna | Alias aceptados | Obligatoria | Uso |
|---|---|---|---|
| `id_estudiante` | `id` | Una de las tres (RN-i) | Emparejamiento exacto — 1.ª prioridad |
| `documento` | `identificacion`, `cedula`, `num_documento`, `no_documento` | Una de las tres (RN-i) | Emparejamiento — 2.ª prioridad. Es la columna que el docente ya tiene en su planilla. |
| `correo` | `email`, `correo_electronico` | Una de las tres (RN-i) | Emparejamiento — 3.ª prioridad, **y la clave que trae la plantilla del sistema** (§7.2) |
| `calificacion` | `nota` | ✅ Sí | Valor a guardar |
| `comentario` | `observacion` | No | Comentario opcional |
| `nombre`, `apellido` | — | No | **Informativas.** Se ignoran para emparejar; solo hacen legible la plantilla. |

Las columnas desconocidas se ignoran sin error: los docentes suelen llevar columnas propias.

### 7.2 La plantilla que genera el sistema — nombre y correo

**Decisión: la plantilla descargable lleva nombre, apellido y correo. No lleva documento.**

| nombre | apellido | correo | calificacion | comentario |
|---|---|---|---|---|
| Ana | Gómez | ana.gomez@colegio.edu.co | 4.5 | |
| Luis | Peña | luis.pena@colegio.edu.co | 3,2 | Entregó tarde |
| Sara | Ríos | sara.rios@colegio.edu.co | | |

Resultado: filas 2 y 3 válidas (la 3 se normaliza a `3.20`), fila 4 omitida por RN-l.

**Por qué así:**

- **El `correo` es la clave de emparejamiento del archivo exportado.** Es `UNIQUE` en `Usuario`, así que empareja exacto, y es legible: el docente entiende qué es esa columna y por qué no debe tocarla. Un `id_estudiante` opaco invita a que alguien lo borre «porque no significa nada».
- **Sin `documento`.** Un `.xlsx` descargado **sale del sistema** y circula por correo, WhatsApp o una memoria USB, fuera de todo control de acceso; RNF-05 obliga a cumplir la normativa de protección de datos de menores. El correo institucional es dato de contacto y el docente ya lo maneja; el número de identificación es de otra categoría y no tiene por qué salir en un archivo.
- **Nombre y apellido** para que el docente sepa a quién le está poniendo cada nota. No se usan para emparejar (§2.2).

**El `documento` y el `id_estudiante` siguen siendo columnas válidas al importar** (§7.1). Los dos caminos quedan cubiertos:

| Caso | Cómo empareja |
|---|---|
| El docente usa la plantilla del sistema | `correo` — exacto, y ya viene escrito en el archivo |
| El docente sube su propia planilla | `documento` (o `id_estudiante`, o `correo`), lo que él ya tuviera — el sistema no se lo entregó |

### 7.3 Formato de las celdas al generar la plantilla

- La columna `correo` va como **texto**, y conviene desactivar el autoformato de hipervínculo: Excel convierte los correos en enlaces azules y algunos flujos de copiar/pegar arrastran el hipervínculo en vez del texto.
- Si alguna vez se decidiera incluir `documento`, tendría que ir **obligatoriamente** como texto (`cell.number_format = "@"`): sin eso Excel se come los ceros a la izquierda y muestra los documentos largos en notación científica, y el archivo devuelto ya no empareja con nada (RN-s).
- Los encabezados van en **negrita y con la fila congelada** (`ws.freeze_panes = "A2"`): con 40 estudiantes, el docente pierde de vista qué columna está llenando.
- La columna `calificacion` se deja vacía pero con el ancho suficiente para verse. Nada de validación de datos de Excel: no todos los editores la respetan, y la validación de verdad está en el servidor.

---

## 8. Endpoints

Prefijo `/api`, mismo router `calificacion.py`, mismo patrón `Depends(require_role(...))`.

### 8.1 `GET /api/notas/plantilla-excel`

| | |
|---|---|
| **Rol** | `Administrador`, `Docente` |
| **Query** | `id_actividad: int` (obligatorio, `gt=0, le=ID_MAXIMO`) |
| **Respuesta** | `200` con `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` y `Content-Disposition: attachment` |
| **Validaciones** | Actividad existe (404) · RN-03 pertenencia del curso (403) |
| **Contenido** | Columnas de §7.2 (nombre · apellido · correo · calificacion · comentario, **sin documento**) + una fila por estudiante matriculado en el grado/año del curso, con la calificación actual si ya tiene nota (así la plantilla sirve también para corregir) |

**El archivo dice a qué actividad pertenece, sin meterlo en los datos:**

- **Nombre del archivo:** `notas-<materia>-<grado>-<actividad>.xlsx`, p. ej. `notas-Matematicas-3A-Parcial1.xlsx`. Se sanitiza (sin tildes, espacios ni `/`), porque un `Content-Disposition` con caracteres raros se rompe en algunos navegadores.
- **Nombre de la hoja:** el de la actividad. Cuidado con dos límites de Excel: **máximo 31 caracteres** y prohibidos `[ ] : * ? / \`. openpyxl no siempre avisa y el archivo sale corrupto; hay que truncar y limpiar.

Ninguna de las dos cosas se lee al importar: son para que el docente no confunda archivos. La verificación de verdad la hace el frontend (§10.2, decisión de §12.B3).

> El periodo cerrado **no** bloquea la descarga de la plantilla: consultar no es escribir. El bloqueo aplica en la confirmación (RN-d).

### 8.2 `POST /api/notas/importar-excel`

| | |
|---|---|
| **Rol** | `Administrador`, `Docente` |
| **Cuerpo** | `multipart/form-data`: `id_actividad` (form field) + `archivo` (`UploadFile`) |
| **Efecto** | **Ninguno sobre la BD** (RN-q) |
| **Respuesta** | `200` con `ImportacionNotasResponse` |

Orden de validación (fallar barato primero):

1. Actividad existe → 404.
2. RN-03 pertenencia → 403.
3. RN-d periodo abierto → 400. *(Antes de leer el archivo: no tiene sentido parsear 1000 filas para un periodo cerrado.)*
4. RN-g/RN-h tipo y tamaño → 400.
5. Encabezados (RN-i) → 400.
6. Fila por fila → nunca lanzan; se acumulan en `errores`.

```jsonc
{
  "id_actividad": 7,
  "actividad": "Parcial 1",      // para que el frontend confirme el destino (§10.2)
  "total_filas": 25,
  "filas_validas": [
    { "id_estudiante": 12, "calificacion": 4.5, "comentario": null,
      "nombre": "Ana", "apellido": "Gómez", "fila": 2 }
  ],
  "filas_omitidas": 3,           // RN-l: sin calificación
  "errores": [
    { "fila": 5, "columna": "documento", "valor": "1023456789",
      "mensaje": "No hay ningún estudiante registrado con ese documento. Pídele al administrador que cree la cuenta." },
    { "fila": 9, "columna": "calificacion", "valor": "8",
      "mensaje": "La calificación debe estar entre 0.00 y 5.00." }
  ],
  "estudiantes_sin_nota": [      // matriculados que el archivo no menciona (RN-u)
    { "id_estudiante": 14, "nombre": "Sara", "apellido": "Ríos" }
  ]
}
```

`fila` es el número **tal como lo ve Excel** (encabezado = 1, primer dato = 2). Un mensaje que dice «fila 5» y en Excel es la 6 es peor que no decir nada.

`nombre`/`apellido` viajan en `filas_validas` solo para pintar la vista previa; el paso de confirmación los descarta.

**`estudiantes_sin_nota` (RN-u)** cubre el caso que ningún error de fila puede detectar: el estudiante que el archivo **no menciona**. Un docente que borró una fila sin darse cuenta, o que exportó su planilla filtrada, hoy no tendría forma de enterarse — la importación diría «10 notas guardadas» y todo parecería correcto. Se listan los matriculados que quedan sin nota para esa actividad, contando también las que ya estaban cargadas antes: si Sara ya tenía nota puesta a mano, no aparece.

Es un **aviso, no un error**: subir el archivo de media clase es legítimo.

### 8.3 Confirmación: `POST /api/notas/carga-masiva` (ya existe, no se toca)

El frontend arma `{id_actividad, notas: filas_validas.map(({id_estudiante, calificacion, comentario}) => ...)}` y lo envía al endpoint que ya está en `main`. Se hereda gratis: validación completa antes de escribir, *upsert*, una sola transacción y los tests que ya lo cubren.

**Por qué separar previsualización de escritura**, y no un solo endpoint que parsea y guarda:

- RF-11 pide explícitamente «valida el formato y **reporta errores**». Un reporte que solo se ve *después* de haber escrito llega tarde.
- El endpoint que escribe sigue siendo uno solo, con una sola ruta de validación. Cero riesgo de que la vía Excel se salte una regla que la vía manual sí aplica — que es exactamente el patrón de fondo §3.1 del documento de revisión de completitud («las reglas de negocio no se propagaron a los módulos nuevos»).
- El endpoint de parseo no toca la BD, así que se puede probar con un archivo de bytes y sin Postgres.

**Sobre la ventana entre previsualizar y confirmar:** el estado puede cambiar (se cierra el periodo, se desmatricula a alguien). No hace falta hacer nada: `cargar_notas_masivo` revalida todo, así que el peor caso es un 400 con mensaje claro, nunca una escritura inconsistente.

---

## 9. Archivos a crear / modificar (backend)

**Commit 1 — esquema (§3), va primero y separado:**

```
Database/schemas.sql                            (M) columna documento en Usuario
Database/migraciones/001-usuario-documento.sql  (N) ALTER para volúmenes ya creados
Backend/app/models/usuario.py                   (M) campo documento
Backend/app/services/curso.py                   (M) listar_estudiantes_por_grado devuelve documento
Backend/app/schemas/curso.py                    (M) documento: Optional[str] en la respuesta
```

**Commit 2 — importación:**

```
Backend/requirements.txt                      (M) + openpyxl, + python-multipart
Backend/app/services/importacion_excel.py     (N) parser puro: bytes -> filas crudas + errores.
                                                  Sin SQLAlchemy, sin FastAPI, sin notas.
Backend/app/services/calificacion.py          (M) previsualizar_importacion_notas()
                                                  generar_plantilla_notas()
Backend/app/schemas/calificacion.py           (M) ImportacionFilaValida, ImportacionErrorFila,
                                                  ImportacionNotasResponse
Backend/app/routers/calificacion.py           (M) los 2 endpoints de §8
Backend/app/tests/test_importacion_excel.py   (N) unitarios del parser (sin BD)
Backend/app/tests/test_importacion_notas.py   (N) unitarios del servicio (con dobles)
```

`importacion_excel.py` expone una única función pura:

```python
def parsear_notas_xlsx(contenido: bytes) -> tuple[list[FilaCruda], list[ErrorFila]]:
    """Traduce un .xlsx a filas crudas. No sabe qué es una nota ni consulta la BD."""
```

Notas de implementación:

- `load_workbook(BytesIO(contenido), read_only=True, data_only=True)`. `read_only` para no cargar la hoja entera en memoria; `data_only` para leer el **valor** de las fórmulas y no la fórmula en texto.
- Con `data_only=True`, una celda con fórmula que Excel nunca guardó en caché devuelve `None`. Se trata como celda vacía (RN-l) con una nota en la interfaz: «si usaste fórmulas, abre y guarda el archivo en Excel antes de subirlo».
- Solo se lee la **primera hoja** (`workbook.worksheets[0]`). Documentado en la interfaz.
- Cerrar siempre el workbook (`try/finally`); en modo `read_only` openpyxl deja descriptores abiertos.
- Un `.xlsx` corrupto hace que openpyxl lance excepciones variadas (`BadZipFile`, `KeyError`, ...). Capturar amplio y devolver 400 «El archivo no es un Excel válido», nunca un 500 — es el mismo defecto de H14 en asistencias.
- **No usar pandas.** Son ~50 MB de dependencia y un motor de inferencia de tipos que convertiría `"3,2"` en algo distinto a lo que el docente escribió.

> ⚠️ **`python-multipart` es obligatorio.** Sin él, FastAPI levanta un error al *importar* el router con un `UploadFile`, y se cae la API entera, no solo este endpoint. Después de tocar `requirements.txt` hay que reconstruir la imagen: las dependencias se instalan en el `docker build`, así que `docker compose up` a secas no las trae.
>
> ```bash
> docker compose build backend && docker compose up -d
> ```

---

## 10. Frontend

```
Frontend/src/modules/calificaciones/components/ImportarExcelModal.jsx   (N)
Frontend/src/modules/calificaciones/services/calificacionService.js     (M)
Frontend/src/modules/calificaciones/components/TablaNotas.jsx           (M)
Frontend/src/styles/Calificaciones.css                                  (M)
```

### 10.1 Servicio — dos llamadas nuevas

```js
async function importarExcel(idActividad, archivo) {
  const formData = new FormData();
  formData.append("id_actividad", idActividad);
  formData.append("archivo", archivo);
  const response = await api.post("/api/notas/importar-excel", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return response.data;
}
```

> ⚠️ **El `Content-Type: application/json` global de `services/api.js` no sirve aquí.** Hay que sobreescribirlo por petición. Axios 1.x detecta el `FormData` y rellena el `boundary` por su cuenta; lo que no puede es adivinar que este `POST` no es JSON.

```js
async function descargarPlantilla(idActividad) {
  const response = await api.get("/api/notas/plantilla-excel", {
    params: { id_actividad: idActividad },
    responseType: "blob"
  });
  return response.data;   // Blob
}
```

> ⚠️ **La plantilla no se puede descargar con un `<a href>` normal.** El endpoint exige `Authorization: Bearer`, y un enlace directo del navegador no pasa por el interceptor de axios: devolvería 401 o un archivo con el JSON del error dentro. Hay que pedirla como `blob`, crear la URL con `URL.createObjectURL`, disparar la descarga con un `<a>` sintético y liberar con `URL.revokeObjectURL`.

Ambas usan el mismo `try/catch` con `ERROR_CONEXION` que el resto del archivo.

### 10.2 `ImportarExcelModal.jsx`

Estructura visual calcada de `CargaMasivaModal.jsx` (`cal-modal-overlay` → `cal-modal` → `cal-modal-header` / cuerpo / `cal-modal-actions`).

**Props:** `{ actividad, onCerrar, onGuardadas }` — la misma firma que `CargaMasivaModal`, para que `TablaNotas` los monte igual.

**Tres estados:**

1. **Selección** — botón «Descargar plantilla», `<input type="file" accept=".xlsx">` y una nota corta con el formato esperado (§7.1) y el aviso de fórmulas.
2. **Vista previa** — resultado de `importarExcel`.
3. **Resultado** — tras `cargaMasiva()`: «Se guardaron N notas», y `onGuardadas(nuevas)` para que `TablaNotas` refresque su mapa sin recargar.

#### La vista previa, en orden de arriba abajo

La pantalla donde se juega la usabilidad de toda la historia. El docente tiene que poder responder tres preguntas sin leer nada dos veces: *¿a dónde va esto?*, *¿qué se va a guardar?*, *¿qué se está quedando por fuera?*

1. **Destino, arriba del todo y en grande** — `Vas a cargar notas en: Parcial 1 · Exámenes · Matemáticas 3°A`. Sale de la actividad seleccionada y de `actividad` en la respuesta.
2. **Resumen en una línea** — `18 notas listas · 2 filas con error · 3 sin nota · 1 estudiante sin mencionar`.
3. **Tabla de filas válidas** — estudiante · nota, con el `cal-badge` de siempre (`claseBadge` / `formatearNota`). Es la confirmación visual de que las notas cayeron donde debían.
4. **Errores**, cada uno con **fila de Excel, columna, valor y qué hacer**. Nunca un mensaje genérico: el docente tiene que poder ir a esa fila de su archivo y arreglarla.
5. **Estudiantes sin nota** (`estudiantes_sin_nota`, RN-u) — en tono de aviso, no de error: `Sara Ríos no aparece en el archivo y sigue sin nota en esta actividad.`
6. **Confirmación explícita del destino** — el botón dice **`Guardar 18 notas en «Parcial 1»`**, con el nombre de la actividad dentro del propio botón. Es lo que reemplaza a meter el `id_actividad` en el archivo (RN-w): el docente lee a dónde va justo cuando decide, en vez de confiar en que el archivo traiga el identificador correcto.

#### Reglas de interacción

- **Carga parcial (RN-v):** con errores y filas válidas a la vez, se guarda lo válido. El botón dice cuántas notas guarda, y al lado se ve cuántas filas quedan fuera. Nunca se guarda en silencio algo distinto de lo que anuncia el botón.
- Con 0 filas válidas, «Guardar» queda deshabilitado y el foco pasa a la lista de errores.
- Deshabilitar los botones mientras hay una petición en curso (`subiendo` / `guardando`), como hace `CargaMasivaModal` con `guardando`.
- **Se puede volver atrás:** «Elegir otro archivo» sin cerrar el modal. El flujo real es arreglar el Excel y reintentar dos o tres veces; obligar a reabrir el modal cada vez lo hace tedioso.
- Tras guardar, el modal **no se cierra solo**: muestra el resultado y deja cerrar al docente. Un modal que desaparece deja la duda de si guardó.
- Reimportar el archivo corregido es seguro: `carga-masiva` hace *upsert* (RN-f), así que las notas ya guardadas se actualizan en vez de duplicarse.

### 10.3 `TablaNotas.jsx`

Un segundo botón «Importar Excel» junto a «Carga masiva» en el `<tfoot>` (línea ~236), con la misma condición `periodoAbierto &&` y un estado `modalImportar` paralelo a `modalMasiva`. `onGuardadas` reutiliza el callback que ya existe.

### 10.4 Reglas del repo que hay que respetar

- Nada de `setState` síncrono dentro de `useEffect` (regla `react-hooks/set-state-in-effect`, ya en rojo en otros archivos — ver §13 del spec 7). Aquí sale gratis: todo el estado se mueve desde manejadores de eventos, no desde efectos.
- Un archivo de componente exporta **solo** el componente (`react-refresh/only-export-components`). Cualquier helper va a `utils/`.
- `npm run lint` no debe subir el conteo de errores respecto a `main`.

---

## 11. Seguridad y privacidad

| Riesgo | Mitigación |
|---|---|
| Zip bomb / archivo gigante | RN-h: 2 MB y 1000 filas, comprobados **antes** de abrir el ZIP. |
| XXE en el XML del `.xlsx` | openpyxl usa `defusedxml` cuando está instalado y desactiva entidades externas; no construir el parseo XML a mano. |
| Docente importando a un curso ajeno | RN-03 vía `_validar_pertenencia_curso`, igual que `cargar_notas_masivo`. |
| Fuga de datos de otros estudiantes | La respuesta solo incluye estudiantes del grado/año del curso de la actividad. El emparejamiento por documento o correo **no** confirma existencia fuera de ese conjunto: un documento de otro grado devuelve el mismo mensaje que uno inexistente (evita usar el importador como oráculo de enumeración, el problema de H3). |
| **Datos personales en archivos que salen del sistema** (RNF-05) | La plantilla descargable lleva nombre, apellido y correo, **nunca el documento** (§7.2). Un `.xlsx` circula fuera de todo control de acceso, así que el número de identificación no sale del sistema por esa vía: viaja solo por la API, dentro de la sesión autenticada del docente. El correo institucional sí va en el archivo — es dato de contacto que el docente ya maneja, y es lo que permite emparejar el archivo de vuelta. |
| Escritura por una ruta sin validar | La escritura sigue siendo exclusivamente `cargar_notas_masivo`. |
| `Content-Type` mentiroso del cliente | RN-g valida por firma de bytes, no por `filename` ni por el header. |

---

## 12. Preguntas abiertas

Ordenadas por lo que bloquean. Las de **A** hay que cerrarlas antes de escribir código, porque cambian el esquema y afectan a otras personas. Las de **B** se pueden cerrar mientras se programa. Las de **C** son coordinación con otros dueños.

### A. Sobre el número de identificación — ✅ todas cerradas (2026-07-27)

| # | Pregunta | Decisión | Dónde quedó |
|---|---|---|---|
| **A1** | ¿La columna va en `Usuario` o en `Estudiante`? | **`Usuario`** | §3.1 |
| **A2** | ¿`NOT NULL` o *nullable*? | ***Nullable* + `UNIQUE`** | §3.1 |
| **A3** | ¿Cómo se aplica la migración? | **Script `ALTER`** (`Database/migraciones/001-usuario-documento.sql`) + la columna en `schemas.sql`. El proyecto está en desarrollo y nadie depende de los datos; Mariana avisa al equipo al mergear. | §3.2 |
| **A4** | ¿Se guarda el **tipo** de documento (TI / CC / CE / Pasaporte)? | **No por ahora** | §3.1 |
| **A5** | El número cambia al pasar de TI a CC a los 18 años. | Nada que construir: el emparejamiento real usa `id_estudiante`, y editar el documento es de HU20. | §3.1 |
| **A6** | **¿Quién llena la columna?** | **Se agrega al formulario de registro estudiantil**, dentro de este spec. HU20 (Santiago) y los formularios de profesores (Samuel) quedan como coordinación, no como bloqueo. | §3.3 |
| **A7** | ¿Y los usuarios que ya existen? | Se quedan sin documento; la precedencia cae al `correo`. Rellenarlos es trabajo de datos. | §3.4 |
| **A8** | ¿El documento va en la plantilla descargable? | **No.** La plantilla lleva **nombre, apellido y correo**; el correo es la clave de emparejamiento del archivo exportado. El documento viaja por la API dentro de la sesión autenticada, nunca en un archivo que sale del sistema (RNF-05). | §7.2, §11 |

### B. Sobre el diseño de la importación

| # | Pregunta | Estado |
|---|---|---|
| **B1** | ¿Emparejar por **nombre y apellido** como último recurso? | ✅ **No.** El esquema no garantiza unicidad y una coincidencia errónea le pone la nota a otro estudiante — el peor fallo posible aquí, porque es silencioso. En su lugar se **avisa**: por fila cuando la identidad no empareja (§2.5) y en bloque con `estudiantes_sin_nota` cuando el archivo ni siquiera menciona a alguien (RN-u). |
| **B2** | ¿Confirmar **parcialmente** o exigir un archivo sin errores? | ✅ **Parcial** (RN-v). Se guarda lo válido, con el conteo de lo que queda fuera siempre a la vista. §10.2 desarrolla la vista previa con ese objetivo. |
| **B3** | ¿Qué pasa si el docente sube por error el archivo de **otra actividad**? | ✅ **Se confirma en el frontend, no en el archivo** (RN-w). El botón de guardar nombra la actividad destino; el `.xlsx` no lleva `id_actividad` ni se le exige. El nombre del archivo y el de la hoja lo dicen, pero solo como ayuda visual. §8.1, §10.2. |
| **B4** | ¿Estudiantes con `Estudiante.estado = 'Inactivo'`? `_validar_estudiante` hoy no mira el estado. | ⬜ **Abierta.** Sugerencia: **aceptarlos** —la nota de alguien que se retiró a mitad de periodo es un dato histórico legítimo— pero **marcarlos** en la vista previa. |
| **B5** | ¿La plantilla debe traer las **notas ya cargadas**? | ⬜ **Abierta.** Sugerencia: sí, la convierte en herramienta de corrección y no solo de carga inicial. Nota: el archivo descargado ya lleva nombres, correos y —si se acepta esto— las notas del curso. |
| **B6** | ¿Son razonables los límites de **2 MB y 1000 filas** (RN-h)? | ⬜ **Abierta.** Un grado no pasa de 40 estudiantes, así que 1000 es holgadísimo. Confirmar que nadie espera importar varias materias de una vez — eso sería el formato matriz de §13, otra historia. |
| **B7** | ¿Y si el archivo trae **fórmulas sin valor en caché**? | ⬜ **Abierta.** Sugerencia: tratarlas como celda vacía (RN-l) y avisarlo en la interfaz. Rechazar el archivo entero es más ruidoso y menos útil. |

### C. Coordinación con otras personas

| # | Con quién | Qué hay que confirmar |
|---|---|---|
| **C1** | **Samuel** (HU0a, HU5, HU21) | Que el campo nuevo del registro estudiantil no choque con lo que tenga en curso — `RegisterForm.jsx`, `schemas/auth.py` y `services/auth.py` son suyos. Y si la columna debe capturarse también para docentes. |
| **C2** | **Santiago** (HU20, HU2, HU19) | Que el alta de estudiantes por administrador capture `documento`. Y si va a necesitar el parser de Excel para importar estudiantes: si sí, acordar desde el primer commit una firma genérica (`parsear_xlsx(contenido, columnas_esperadas)`) en vez de refactorizar después. |
| **C3** | **Laura** (HU13, HU18) | Que el bloqueo por corte/año cerrado viva en `_validar_periodo_abierto` del servicio y no en el router. Si vive ahí, la importación lo hereda gratis; si lo pone en el router, HU22 se salta el bloqueo. Es exactamente el patrón de fallo de §3.1 del documento de revisión de completitud. |
| **C4** | **Rafael** (HU12) | Que `DocenteEstudiantes.jsx` empiece a filtrar de verdad por documento cuando la columna exista (§2.3). Es un cambio de una línea en su filtro, pero es suyo. |
| **C5** | **Todo el equipo** | ✅ Resuelto: Mariana avisa por el grupo al mergear el commit del esquema. Quien haga `pull` sin correr la migración verá `UndefinedColumn` en el login. |

### D. Estado del proyecto que este spec da por supuesto

| # | Supuesto | Riesgo si cambia |
|---|---|---|
| **D1** | «Los estudiantes de una materia» = los matriculados en el grado y año del curso (RN-k). | HU12 sigue guardando la asociación curso–estudiante en un `set` en memoria (`services/curso.py:23`, hallazgo H2 sin resolver). Si alguien la lleva a una tabla real, RN-k debería pasar a leer de ahí. Mientras tanto, la fuente correcta es `Matricula`, que es de donde lee `TablaNotas`. |
| **D2** | `POST /api/notas/carga-masiva` no cambia. | El merge #24 agregó `PUT /api/notas` y dos `DELETE` en el mismo router; `carga-masiva` quedó intacto, pero hay que revisar el rebase antes de mergear. |

---

## 13. Extensión natural (fuera del MVP)

**Formato matriz:** una fila por estudiante y una columna por actividad (`correo | Taller 1 | Parcial | Quiz`), que es como los docentes llevan sus planillas de verdad. Requiere emparejar el encabezado con `ActividadEvaluativa.nombre` dentro de la sección, y decidir qué hacer con las columnas que no coinciden con ninguna actividad (¿error, o crearlas?). Es una historia propia, no un ajuste: multiplica los modos de fallo y el MVP por actividad ya cierra HU22 y RF-11.

Solo cuando el flujo por actividad esté probado con docentes reales vale la pena abrirlo.

---

## 14. Definition of Done

**Esquema (commit 1)**

- [ ] `documento VARCHAR(20) UNIQUE` en `Database/schemas.sql` **y** en `Database/migraciones/001-usuario-documento.sql`.
- [ ] La migración corre sobre un volumen existente sin borrar datos, y es idempotente (correrla dos veces no falla).
- [ ] Una instalación limpia (`docker compose down -v && docker compose up -d && docker compose run --rm seed`) nace con la columna.
- [ ] El login y el resto de la app siguen funcionando con la columna vacía en todas las filas.
- [ ] `GET /api/grados/{id}/estudiantes` devuelve `documento` (o `null`) y `TablaNotas` no se rompe con el campo nuevo.
- [ ] Avisado en el grupo del equipo antes de mergear (§12.C5).

**Registro estudiantil (commit 1, §3.3)**

- [ ] `RegisterForm.jsx` pide el documento y lo manda en el payload; crear una cuenta nueva lo guarda.
- [ ] El documento se **normaliza igual que en la importación** (RN-r): registrar `1.023.456.789` y luego importar un Excel con `1023456789` empareja.
- [ ] Registrar dos cuentas con el mismo documento devuelve **409**, no un 500 por violación de `UNIQUE`.
- [ ] Registrar sin documento devuelve 422 (el campo es obligatorio en el formulario aunque la columna sea *nullable*).
- [ ] Las cuentas creadas **antes** del cambio siguen pudiendo iniciar sesión y aparecen normalmente en la tabla de notas.

**Backend (commit 2)**

- [ ] `openpyxl` y `python-multipart` en `requirements.txt`; `docker compose build backend` reconstruye sin error.
- [ ] `GET /api/notas/plantilla-excel` devuelve un `.xlsx` que abre en Excel/LibreOffice con la lista real del curso: nombre, apellido y correo, **sin columna de documento** (§7.2).
- [ ] El nombre del archivo y el de la hoja identifican la actividad; el nombre de hoja se trunca a 31 caracteres y se limpian `[ ] : * ? / \`.
- [ ] `POST /api/notas/importar-excel` devuelve filas válidas, errores y `estudiantes_sin_nota`, y **no escribe nada** (verificado comparando `SELECT count(*) FROM Nota` antes y después).
- [ ] RN-g a RN-w implementadas en el servicio/parser, no en el router.
- [ ] Ningún archivo malformado produce un 500: `.txt` renombrado a `.xlsx`, ZIP corrupto, hoja vacía, archivo sin encabezados y archivo de 3 MB devuelven 4xx con mensaje entendible.
- [ ] RN-03 verificada: un docente ajeno recibe 403 tanto en plantilla como en importación.
- [ ] Tests unitarios del parser con archivos generados en memoria (sin BD, `unittest` de la stdlib, como el resto de `app/tests/`).
- [ ] Test de integración: plantilla → llenar → importar → confirmar → `GET /api/notas` muestra las notas; reimportar el mismo archivo no duplica (RN-f).

**Frontend**

- [ ] Botón «Importar Excel» visible por actividad solo con el periodo abierto.
- [ ] La plantilla se descarga con el token puesto y el nombre de archivo correcto.
- [ ] La vista previa muestra, en este orden: destino, resumen, filas válidas, errores con número de fila de Excel, y estudiantes sin nota.
- [ ] **El botón de guardar nombra la actividad destino** y el número de notas (RN-w): `Guardar 18 notas en «Parcial 1»`.
- [ ] **Carga parcial (RN-v):** con 2 filas con error y 18 válidas, se guardan las 18 y la interfaz dice claramente que 2 quedaron fuera.
- [ ] «Elegir otro archivo» permite reintentar sin cerrar el modal, y el modal no se cierra solo tras guardar.
- [ ] Confirmar guarda y la tabla se actualiza sin recargar la página.
- [ ] `npm run build` pasa y `npm run lint` no sube el conteo de errores respecto a `main`.

**Prueba manual de extremo a extremo** (contra Docker Compose, con el seed del README)

- [ ] Archivo con 3 notas válidas → se guardan las 3.
- [ ] Archivo con una nota `8`, un correo inexistente, una fila duplicada y una celda vacía → 3 errores + 1 omitida, y la interfaz explica cada uno.
- [ ] Archivo sin ninguna columna de identidad → rechazado completo con el mensaje de §6 (RN-i).
- [ ] **Emparejamiento por documento:** registrar un estudiante con documento, subir un archivo que solo traiga `documento` y `calificacion` → empareja.
- [ ] **Degradación:** el mismo archivo con un estudiante **sin** documento en la BD → esa fila da el error de §2.5 y las demás se procesan.
- [ ] **Formato de Excel:** un documento con ceros a la izquierda (`0012345678`) escrito a mano en el archivo del docente empareja sin perder dígitos (RN-r/RN-s).
- [ ] **Aviso de faltantes (RN-u):** borrar una fila de la plantilla antes de subirla → ese estudiante aparece en «sin nota», sin bloquear la carga.
- [ ] Periodo cerrado → la importación se bloquea antes de leer el archivo.

**Cierre**

- [ ] PR contra `main` con al menos un review (regla 4 del README).
- [ ] `docs/historias-de-usuario-y-asignaciones.md`: HU22 pasa a ✅ **solo si el recorrido completo backend + interfaz + prueba está hecho** (recomendación 4 del documento de revisión de completitud).
- [ ] Resumen de implementación en `SPEC/10-summary-hu22-importar-notas-excel.md`, siguiendo el formato de los anteriores.
