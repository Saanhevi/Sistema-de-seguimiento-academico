# Resumen de implementación — HU22: Importar notas desde un archivo Excel

**Spec:** [10-spec-hu22-importar-notas-excel.md](10-spec-hu22-importar-notas-excel.md)
**Requerimiento:** RF-11 — importar notas masivamente desde `.xlsx`, validando el formato y reportando errores.
**Rama:** `feat/importar-notas-excel`
**Estado:** Implementado y verificado con 75 tests unitarios y un recorrido completo contra Postgres.

---

## 1. Qué se implementó

### Commit 1 — esquema (`documento`)

| Archivo | Cambio |
|---|---|
| `Database/schemas.sql` | `documento VARCHAR(20) UNIQUE` en `Usuario` |
| `Database/migraciones/001-usuario-documento.sql` | `ALTER` idempotente para bases ya creadas |
| `Backend/app/core/identidad.py` | **Nuevo.** Normalización de documento y correo (RN-r, RN-s, RN-t) |
| `Backend/app/models/usuario.py` | Campo `documento` (nullable) |
| `Backend/app/repositories/usuario.py` | `buscar_por_documento` |
| `Backend/app/schemas/auth.py` | `documento` obligatorio en el registro, normalizado por un validador |
| `Backend/app/services/auth.py` | Lo guarda; documento repetido → **409** |
| `Backend/app/services/curso.py`, `schemas/curso.py` | `listar_estudiantes_por_grado` devuelve `documento` |
| `Frontend/.../RegisterForm.jsx` | Campo «Número de documento» |
| `README.md` | Sección de migraciones |

### Commit 2 — importación

| Archivo | Cambio |
|---|---|
| `Backend/requirements.txt` | `openpyxl`, `python-multipart` (+ `et-xmlfile`) |
| `Backend/app/services/importacion_excel.py` | **Nuevo.** Parser puro: bytes → filas crudas + errores |
| `Backend/app/services/calificacion.py` | `previsualizar_importacion_notas`, `generar_plantilla_notas` |
| `Backend/app/schemas/calificacion.py` | Esquemas del reporte de importación |
| `Backend/app/routers/calificacion.py` | Los dos endpoints |
| `Frontend/.../ImportarExcelModal.jsx` | **Nuevo.** Modal de tres estados |
| `Frontend/.../utils/descargas.js` | **Nuevo.** Descarga de un Blob autenticado |
| `Frontend/.../calificacionService.js` | `importarExcel`, `descargarPlantilla` |
| `Frontend/.../TablaNotas.jsx` | Botón «Importar Excel» por actividad |

---

## 2. Cómo quedó el flujo

1. El docente abre «Importar Excel» en una actividad (solo con el periodo abierto).
2. Descarga la plantilla: un `.xlsx` con la lista real del curso —nombre, apellido y correo— y la columna `calificacion` vacía.
3. Escribe las notas y sube el archivo.
4. Ve la vista previa: **destino**, resumen en una línea, filas válidas, errores con número de fila de Excel, y estudiantes que el archivo no menciona.
5. Confirma con un botón que nombra el destino: `Guardar 18 notas en «Parcial 1»`.

La escritura la hace `POST /api/notas/carga-masiva`, el endpoint que ya existía. **HU22 no reimplementa nada de la escritura de notas**, solo traduce Excel → payload.

---

## 3. Las tres decisiones que más condicionaron el resultado

**No se empareja por nombre.** El esquema no garantiza que `nombres + apellidos` sean únicos —dos «Juan Pérez» en el mismo grado son válidos— y una coincidencia errónea le pone la nota a otro estudiante en silencio, que es el peor fallo posible aquí. En su lugar se agregó la columna `documento` y se avisa: por fila cuando la identidad no empareja, y en bloque (`estudiantes_sin_nota`) cuando el archivo ni siquiera menciona a alguien.

**Previsualizar y escribir están separados.** RF-11 pide reportar errores, y un reporte que se ve *después* de escribir llega tarde. Además el endpoint que escribe sigue siendo uno solo, con una sola ruta de validación: la vía Excel no puede saltarse una regla que la vía manual sí aplica — que es el patrón de fallo señalado en §3.1 del documento de revisión de completitud.

**La plantilla no lleva el documento.** Un `.xlsx` descargado sale del sistema y circula por correo o WhatsApp, fuera de todo control de acceso; RNF-05 obliga a cuidar los datos de menores. El correo institucional basta para emparejar de vuelta y es dato de contacto que el docente ya maneja. El documento viaja solo por la API, dentro de la sesión autenticada.

---

## 4. Reglas de negocio

Heredadas sin reimplementar (las aplica `cargar_notas_masivo` al confirmar): **RN-a** (0.00–5.00), **RN-03/RN-d** (curso propio y periodo abierto), **RN-e** (estudiante válido), **RN-f** (*upsert*).

Nuevas, todas en el parser o el servicio, **ninguna en el router**:

| Regla | Dónde |
|---|---|
| RN-g firma ZIP · RN-h 2 MB / 1000 filas · RN-i columna de identidad | `importacion_excel.py` |
| RN-j precedencia `id_estudiante → documento → correo`, sin reintentos | `importacion_excel.py` |
| RN-l celda vacía se omite · RN-n coma y punto · RN-o redondeo a 2 decimales · RN-p comentario ≤ 100 | `importacion_excel.py` |
| RN-r normalización · RN-s notación científica · RN-t correo en minúsculas | `core/identidad.py` |
| RN-k grado y año del curso · RN-m duplicados · RN-u avisos · RN-q sin efectos | `calificacion.py` |
| RN-v carga parcial · RN-w destino confirmado en la interfaz | `ImportarExcelModal.jsx` |

---

## 5. Validación

**Tests automáticos — 75, todos en verde** (`unittest` de la stdlib, como el resto de `app/tests/`):

- `test_importacion_excel.py` (34): el parser, con archivos generados en memoria y sin base de datos.
- `test_importacion_notas.py` (41): el servicio con dobles, más seis por HTTP con `TestClient` que cubren `multipart/form-data`, la descarga del `.xlsx` y el RBAC de ambos endpoints.

El resto de la suite sigue igual que en `main`. `test_curso_service_regression.py` falla en `main` y sigue fallando aquí por la misma razón, ajena a esta historia: llama a `agregar_estudiante_a_curso`, un método que no existe (se llama `asociar_estudiante_a_curso`).

**Recorrido completo contra Postgres real**, cubriendo la DoD:

| Comprobación | Resultado |
|---|---|
| Migración sobre una base con datos, corrida dos veces | Idempotente, no pierde filas |
| Esquema migrado vs. instalación limpia | Columnas idénticas |
| Varios `NULL` en el `UNIQUE`; documento repetido | Conviven; el repetido falla |
| Plantilla → llenar → importar → confirmar | 3 notas guardadas |
| Reimportar el mismo archivo | Siguen siendo 3, no 6 (RN-f) |
| `SELECT count(*) FROM Nota` antes/después de previsualizar | Sin cambios (RN-q) |
| Archivo con nota `8`, documento ajeno y celda vacía | 2 errores + 1 omitida, filas de Excel correctas |
| Emparejar `1.023.456.789` (BD) con `1023456789` (archivo) | Empareja (RN-r) |
| Ceros a la izquierda (`0012345678`) | Sin perder dígitos |
| Docente ajeno en plantilla e importación | 403 en ambos |
| Periodo cerrado | Bloquea la importación; permite descargar la plantilla |
| Registro: documento con puntos, repetido, ausente | Normalizado, 409, 422 |
| Login de una cuenta sin documento | 200 |

**Frontend:** `npm run build` correcto. `npm run lint` da **16 problemas, los mismos 16 que en `main`** (verificado haciendo checkout de `main` y comparando); ninguno en los archivos nuevos.

---

## 6. Pendiente y coordinación

**No se pudo verificar en este entorno:** el recorrido por interfaz contra Docker Compose. `docker compose build` falla en esta máquina por un problema de red del demonio (`failed to add the host <=> sandbox pair interfaces: operation not supported`), que se reproduce hasta con un `RUN echo hola` sobre `alpine`: es del entorno, no del proyecto. Por eso la verificación de base de datos se hizo levantando un Postgres local contra el mismo `schemas.sql` y la misma migración. **Queda pendiente probar el modal en el navegador** antes de marcar HU22 como ✅.

**Al mergear:** avisar por el grupo (§12.C5). Quien haga `git pull` sin correr la migración verá `UndefinedColumn` **en el login**.

**Preguntas abiertas del spec que siguen abiertas:** B4 (estudiantes inactivos), B6 (límites de 2 MB / 1000 filas) y B7 (fórmulas sin valor en caché, hoy tratadas como celda vacía y avisado en la interfaz). B5 se cerró implementándola: la plantilla trae las notas ya cargadas, así que sirve también para corregir.

**Coordinación:** Santiago (que HU20 capture `documento` al crear estudiantes), Samuel (`RegisterForm.jsx`, `schemas/auth.py` y `services/auth.py` son suyos; y si el documento aplica a docentes), Rafael (el buscador de `DocenteEstudiantes.jsx` ya puede filtrar por documento: el endpoint ahora lo devuelve).
