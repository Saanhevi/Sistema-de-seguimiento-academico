# Spec: Frontend --- Gestión de Asistencias

**Owner:** Samuel\
**Repo:** `Saanhevi/Sistema-de-seguimiento-academico`\
**Complementa:** `docs/Historias de usuario.md` y
`docs/sprint-2-asignacion-tareas.md`\
**Rama sugerida:** `feat/asistencias-frontend`

------------------------------------------------------------------------

# 0. Contexto y estado actual

Este sprint contempla la implementación del módulo de asistencias
asociado a las siguientes historias de usuario:

-   HU6 -- Como profesor, quiero registrar inasistencias de los
    estudiantes.
-   HU14 -- Como profesor, quiero eliminar registros de inasistencias.
-   HU7 -- Como estudiante, quiero consultar mis inasistencias.

Estado actual:

-   Existe una implementación preliminar del backend para asistencias.
-   Existen modelos y schemas iniciales para Día Asistible y Asistencia.
-   El frontend aún no posee una interfaz funcional para estas
    historias.
-   El proyecto utiliza React + CSS manual + FastAPI.

La meta es construir un frontend completamente preparado para integrarse
con el backend existente.

------------------------------------------------------------------------

# 1. Objetivo

Construir el módulo de gestión de asistencias para profesores y
estudiantes reutilizando el diseño del Dashboard actual.

El módulo debe permitir:

-   Registrar asistencias.
-   Eliminar registros.
-   Consultar historial.
-   Dejar preparada la integración con el backend.

------------------------------------------------------------------------

# 2. Alcance del MVP

## Incluye

-   Página DocenteAsistencia.
-   Página EstudianteAsistencia.
-   Registro de asistencias por curso.
-   Eliminación de registros.
-   Historial de inasistencias.
-   Servicios preparados para consumir FastAPI.

## No incluye

-   Estadísticas.
-   Reportes PDF.
-   Alertas automáticas.
-   Notificaciones a acudientes.
-   Justificación de inasistencias.

------------------------------------------------------------------------

# 3. Diseño de la interfaz

## Docente

Ruta:

`/dashboard/docente/asistencia`

Debe contener:

-   Selector de curso.
-   Selector de fecha.
-   Tabla de estudiantes.
-   Estado Presente/Ausente.
-   Botón Guardar.
-   Historial del día.
-   Acción Eliminar.

## Estudiante

Ruta:

`/dashboard/estudiante/asistencia`

Debe mostrar:

-   Fecha.
-   Curso.
-   Estado.

Ordenado por fecha descendente.

------------------------------------------------------------------------

# 4. Componentes

``` text
Frontend/src/modules/asistencia/
    components/
        AsistenciaTable.jsx
        AsistenciaRow.jsx
        HistorialAsistencia.jsx
        ConfirmDeleteModal.jsx
    services/
        asistenciaService.js

Frontend/src/modules/dashboard/pages/docente/
        DocenteAsistencia.jsx

Frontend/src/modules/dashboard/pages/estudiante/
        EstudianteAsistencia.jsx
```

## Responsabilidades

-   DocenteAsistencia.jsx coordina toda la vista.
-   AsistenciaTable renderiza la tabla.
-   AsistenciaRow maneja cada estudiante.
-   HistorialAsistencia muestra registros existentes.
-   ConfirmDeleteModal confirma eliminaciones.
-   asistenciaService encapsula el acceso al backend.

------------------------------------------------------------------------

# 5. Comportamiento

## Registrar

1.  Seleccionar curso.
2.  Seleccionar fecha.
3.  Marcar presente/ausente.
4.  Guardar.

Debe mostrarse un mensaje de éxito.

## Eliminar

Cada fila del historial tendrá un botón Eliminar.

Debe solicitar confirmación antes de borrar.

## Consultar

El estudiante solamente puede consultar sus propias asistencias.

No puede editar.

------------------------------------------------------------------------

# 6. Servicios

Crear:

``` js
listarEstudiantesCurso(idCurso)
registrarAsistencias(idDia,data)
eliminarAsistencia(idAsistencia)
obtenerMisAsistencias()
```

Todos deben reutilizar `Frontend/src/services/api.js`.

Mientras el backend no esté completamente integrado pueden utilizar
datos mock dejando TODOs.

------------------------------------------------------------------------

# 7. Integración futura

Preparar llamadas para:

POST /asistencias/{id_dia}

DELETE /asistencias/{id_asistencia}

GET /asistencias/estudiante

No manejar tokens directamente.

------------------------------------------------------------------------

# 8. Estilos

Reutilizar:

-   Dashboard.css
-   variables.css

No introducir Tailwind.

La interfaz debe ser consistente con el resto del sistema.

------------------------------------------------------------------------

# 9. Criterios de aceptación

-   [ ] El docente puede registrar asistencias.
-   [ ] El docente puede eliminar registros.
-   [ ] El estudiante puede consultar sus inasistencias.
-   [ ] La UI reutiliza el Dashboard existente.
-   [ ] El código queda preparado para conectar con FastAPI.
-   [ ] Los datos mock pueden reemplazarse sin reescribir la vista.

------------------------------------------------------------------------

# 10. Definition of Done

-   [ ] Existe una vista funcional para docentes.
-   [ ] Existe una vista funcional para estudiantes.
-   [ ] El módulo está dividido por componentes.
-   [ ] Los servicios están aislados.
-   [ ] Se documentan los TODO de integración.
-   [ ] PR listo para revisión sobre develop.
