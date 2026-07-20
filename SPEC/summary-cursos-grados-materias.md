# Resumen del módulo de Cursos, Grados y Materias

## Objetivo
Implementar el backend base para gestionar grados, materias, periodos académicos, cursos y matrículas de estudiantes, siguiendo el patrón repository-service-router del proyecto y el spec del módulo.

## Cambios principales
- Se agregaron los modelos ORM para Grado, Materia, PeriodoAcademico, Curso y Matricula.
- Se actualizaron los imports del paquete de modelos para que las nuevas entidades queden disponibles en la app.
- Se añadieron repositorios con operaciones básicas de crear, listar y buscar por id, además de filtros para cursos y matrículas.
- Se creó un servicio único de cursos con validaciones de negocio para:
  - nombres obligatorios,
  - existencia de docente/grado/materia/período,
  - duplicidad de cursos,
  - validación de rol de docente y estudiante,
  - evitar dobles matrículas en el mismo año.
- Se implementaron endpoints REST para crear y listar grados, materias, periodos, cursos y matrículas, además de consultar estudiantes por grado y año.
- Se registró el router del módulo en la aplicación principal y se añadió la dependencia de inyección del servicio de cursos.
- Se añadieron scripts de prueba manual para validar el flujo completo con la base de datos.

## Archivos clave
- Backend/app/models/
- Backend/app/repositories/
- Backend/app/schemas/curso.py
- Backend/app/services/curso.py
- Backend/app/routers/curso.py
- Backend/app/core/dependencies.py
- Backend/app/main.py
- Backend/app/tests/

## Verificación realizada
Se validó el módulo con:
- compilación de los archivos Python nuevos,
- ejecución del flujo de prueba manual contra PostgreSQL mediante Docker Compose,
- creación de grado, materia, periodo, curso y matrícula.
