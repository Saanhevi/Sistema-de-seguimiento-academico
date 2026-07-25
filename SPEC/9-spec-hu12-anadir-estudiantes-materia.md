# Spec HU12 — Añadir estudiantes a mi materia

**Historia de usuario:** HU12  
**Como profesor, quiero añadir estudiantes a mi materia, para gestionar correctamente los alumnos que la cursan.**

**Owner:** Rafael  
**Fecha:** 2026-07-24  
**Estado:** En desarrollo

---

## 1. Contexto

La historia HU12 debe implementarse dentro del módulo existente de cursos y matrículas del proyecto. El backend ya cuenta con modelos y servicios para:

- docentes,
- cursos,
- grados,
- materias,
- periodos académicos,
- estudiantes,
- matrículas.

El frontend ya dispone de una ruta de administración para cursos y un panel de matrículas, por lo que esta historia se integrará como una experiencia específica para que un docente pueda ver y gestionar los estudiantes asociados a un curso/materia que dicta.

---

## 2. Objetivo

Permitir que un profesor pueda:

1. ver los cursos que dicta,
2. seleccionar uno de esos cursos,
3. consultar los estudiantes matriculados en el grado asociado al curso,
4. añadir estudiantes al curso/materia desde una vista de gestión,
5. visualizar el resultado de la acción en una lista clara y consistente.

---

## 3. Alcance del MVP

### Incluye

- Nuevo endpoint backend para listar estudiantes disponibles por curso/grado.
- Nuevo endpoint backend para asociar un estudiante a un curso mediante la matrícula existente.
- Vista en el frontend para docentes donde puedan seleccionar un curso y gestionar estudiantes.
- Integración del frontend con el servicio del backend usando la estructura actual de Axios y rutas del proyecto.
- Uso de estilos y componentes alineados con el diseño del frontend actual y con la referencia del prototipo local.

### No incluye

- Eliminar estudiantes de un curso desde esta historia.
- Carga masiva de estudiantes desde Excel.
- Cambios de permisos diferentes a los ya usados en el proyecto.
- Reescritura completa del módulo de cursos.

---

## 4. Alineación con la arquitectura real del proyecto

### Backend

El desarrollo debe respetar la estructura actual:

- Router: [Backend/app/routers/curso.py](../../Backend/app/routers/curso.py)
- Servicio: [Backend/app/services/curso.py](../../Backend/app/services/curso.py)
- Esquemas: [Backend/app/schemas/curso.py](../../Backend/app/schemas/curso.py)
- Modelos: [Backend/app/models/curso.py](../../Backend/app/models/curso.py), [Backend/app/models/matricula.py](../../Backend/app/models/matricula.py) y [Backend/app/models/estudiante.py](../../Backend/app/models/estudiante.py)

La lógica debe reutilizar:

- el modelo de curso,
- el modelo de matrícula,
- el modelo de estudiante,
- y la relación existente entre grado y matrícula.

### Frontend

El frontend debe integrarse con la estructura actual:

- rutas de dashboard docente: [Frontend/src/routes/AppRouter.jsx](../../Frontend/src/routes/AppRouter.jsx)
- módulos de cursos: [Frontend/src/modules/cursos](../../Frontend/src/modules/cursos)
- servicio de cursos: [Frontend/src/modules/cursos/services/cursoService.js](../../Frontend/src/modules/cursos/services/cursoService.js)
- página docente: [Frontend/src/modules/dashboard/pages/docente/DocenteAsistencia.jsx](../../Frontend/src/modules/dashboard/pages/docente/DocenteAsistencia.jsx)

Se tomará como referencia visual el prototipo local ubicado en:

- C:\Users\madr\PrototipoSitioWebEducativo

La implementación debe adaptarse a React JS y CSS del proyecto actual, sin copiar el prototipo de forma literal.

---

## 5. Requisitos funcionales

### 5.1 Backend

1. El sistema debe exponer un endpoint para listar cursos asignados a un docente.
2. El sistema debe exponer un endpoint para listar los estudiantes que pueden añadirse a un curso, tomando como base los estudiantes matriculados en el grado del curso y el año vigente o el año del periodo asociado.
3. El sistema debe exponer un endpoint para asociar un estudiante a un curso, validando:
   - que el curso exista,
   - que el estudiante exista,
   - que la matrícula exista para el grado y año correspondiente,
   - y que la asociación no se duplique.
4. El endpoint debe responder con un payload claro que permita mostrar el estado de la operación en la interfaz.
5. El backend debe seguir el estilo de respuestas HTTP actual del proyecto: 200/201, 400, 404, 409 y 403 cuando aplique.

### 5.2 Frontend

1. El docente debe ver una lista de cursos que dicta.
2. El docente debe poder seleccionar un curso.
3. Al seleccionar un curso, la interfaz debe cargar los estudiantes disponibles para añadir.
4. La interfaz debe permitir seleccionar un estudiante y confirmar la acción.
5. La interfaz debe mostrar una lista con los estudiantes actualmente asociados al curso.
6. La interfaz debe mostrar mensajes claros de carga, éxito o error.

---

## 6. Reglas de negocio

- Un curso se identifica por su docente, grado, materia y periodo.
- Los estudiantes que pueden añadirse a un curso deben provenir de la matrícula del grado asociado.
- La historia no crea una nueva tabla de asociación entre curso y estudiante; se reutiliza la lógica de matrícula del grado para mantener la estructura real del proyecto.
- Si un estudiante ya está asociado al curso, no debe poder añadirse nuevamente.
- La acción debe estar restringida a docentes autenticados y a cursos que les pertenezcan.

---

## 7. Diseño de la interfaz

### Vista propuesta

En el panel de docente se añadirá una sección llamada “Gestión de estudiantes por materia”.

Debe incluir:

- selector de curso,
- lista de estudiantes disponibles,
- lista de estudiantes asociados al curso,
- botón para añadir estudiante,
- mensajes de estado.

### Estilo

- Se reutilizarán clases existentes de la UI de dashboard.
- Se mantendrá un diseño claro y limpio, similar al prototipo local, pero adaptado a las clases actuales del proyecto.

---

## 8. Entregables

1. Spec file creado en la carpeta SPEC/HU12.
2. Backend funcional con endpoints para consultar y añadir estudiantes a un curso.
3. Frontend funcional para seleccionar curso y gestionar estudiantes asociados.
4. Verificación con build de frontend y pruebas o validación básica del backend.

---

## 9. Criterios de aceptación

- Un docente puede ver los cursos que dicta.
- El docente puede seleccionar un curso y ver estudiantes disponibles.
- El docente puede añadir un estudiante al curso.
- La interfaz refleja el estado de la operación.
- El backend responde con los códigos HTTP esperados.
- La implementación no rompe el flujo actual del proyecto.
