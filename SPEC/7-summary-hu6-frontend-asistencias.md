# Summary — HU6: Registrar inasistencias

## Historia de usuario

HU6: Como profesor, quiero registrar inasistencias de los estudiantes, para llevar un control de asistencia de mis clases.

## Objetivo alcanzado

Se implementó la interfaz de frontend para que el docente pueda registrar asistencias desde la plataforma, apoyándose en la estructura ya existente del dashboard y en la API del backend.

## Alcance desarrollado

### Funcionalidades implementadas

- Vista de asistencia para docentes en la ruta `/dashboard/docente/asistencia`
- Selección de curso asociado al docente autenticado
- Visualización del historial de fechas registradas por curso
- Carga de la lista de estudiantes para una fecha específica
- Cambio de estado por estudiante: Presente, Ausente o Tardanza
- Guardado de la información de asistencia en el backend
- Mensajes de éxito y error en la interfaz

### Archivos principales modificados

- `Frontend/src/modules/dashboard/pages/docente/DocenteAsistencia.jsx`
- `Frontend/src/modules/asistencias/services/asistenciaService.js`
- `Frontend/src/modules/asistencias/components/AsistenciaTable.jsx`
- `Frontend/src/modules/asistencias/components/HistorialDias.jsx`
- `Frontend/src/modules/asistencias/components/CursoSelector.jsx`
- `Frontend/src/modules/asistencias/styles/Asistencia.css`

## Integración con backend

La vista se conectó con los endpoints del backend para:

- Obtener los cursos del docente
- Consultar el historial de fechas por curso
- Cargar la lista de asistencia para una fecha
- Guardar los cambios de asistencia

## Estado de verificación

Se validó la implementación ejecutando la compilación del frontend:

```bash
cd c:\Users\madr\Sistema-de-seguimiento-academico\Frontend && npm run build
```

Resultado:
- Compilación exitosa con Vite
- Sin errores de build reportados

## Observación

La implementación deja el módulo de asistencias preparado para continuar con mejoras posteriores, incluyendo la vista de estudiante para la HU7 y la gestión adicional de registros.
