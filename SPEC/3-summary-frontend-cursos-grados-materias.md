# Resumen 3: Frontend de Cursos, Grados, Materias y Matrículas

## Objetivo
Implementar la interfaz administrativa para gestionar grados, materias, periodos académicos, cursos y matrículas, consumiendo los endpoints del backend del módulo.

## Cambios principales
- Se creó el servicio de acceso al backend en Frontend/src/modules/cursos/services/cursoService.js siguiendo el patrón de axios ya usado en el proyecto.
- Se implementaron 5 paneles de gestión dentro del módulo de cursos:
  - GradoPanel
  - MateriaPanel
  - PeriodoPanel
  - CursoPanel
  - MatriculaPanel
- Se reemplazó el placeholder de AdminCursos por una vista con tabs simples para navegar entre los 5 paneles.
- Se reutilizaron las clases .panel, .panel-header y .panel-title del dashboard, además de variables CSS del sistema visual existente.
- Se creó un archivo de estilos propio para el módulo en Frontend/src/styles/Cursos.css.
- Se importó el CSS del módulo desde Frontend/src/App.jsx.
- Se dejó documentado como TODO el uso de selectores reales para docente y estudiante, dado que el backend no expone aún un endpoint de listado de usuarios por rol.

## Archivos clave
- Frontend/src/modules/cursos/services/cursoService.js
- Frontend/src/modules/cursos/components/
- Frontend/src/modules/dashboard/pages/admin/AdminCursos.jsx
- Frontend/src/styles/Cursos.css
- Frontend/src/App.jsx

## Nota de implementación
- El frontend usa inputs temporales para id_docente e id_estudiante, siguiendo la decisión del spec para no bloquear el MVP.
- No se tocaron AppRouter.jsx ni PortalAdmin.jsx.
- El export nombrado de AdminCursos se mantuvo intacto.
