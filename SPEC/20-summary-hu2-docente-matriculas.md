# Resumen 20 - HU2 para Docente (matriculas por grado)

## Objetivo
Corregir la inconsistencia de HU2 para que un docente autenticado pueda asignar estudiantes a un grado academico, sin abrir permisos globales que comprometan seguridad.

## Problema detectado
- El router permitia Docente en algunos puntos, pero la logica de servicio bloqueaba la creacion de matriculas para cualquier rol distinto de Administrador.
- En frontend, la accion de matricula estaba disponible principalmente desde el flujo administrativo.

## Solucion implementada
Se habilito HU2 para Docente en backend y se expuso la accion en la vista docente, con restriccion de alcance:

- Un Docente puede crear matriculas solo para grados y anios donde tiene cursos asignados.
- Si intenta matricular fuera de su alcance, recibe 403.

## Cambios backend
- Se actualizo la autorizacion del endpoint de matriculas para aceptar Administrador y Docente.
- Se agrego validacion de negocio para Docente en el servicio de cursos:
  - Verifica existencia de al menos un curso del docente para el grado y anio solicitados.
  - Mantiene validaciones de estudiante, grado y unicidad de matricula por anio.
- Se incluyo validacion de anio en creacion de matricula reutilizando la validacion central.

## Cambios frontend
- Se extendio la vista docente de estudiantes para incluir un bloque de matricula por grado:
  - Usa el curso seleccionado para fijar el grado.
  - Permite definir ID de estudiante y anio.
  - Invoca el endpoint real de creacion de matricula.
- Se corrigio un bug de carga en la vista (`Loader2` no definido), reemplazado por el icono local existente.

## Archivos modificados
- Backend/app/routers/curso.py
- Backend/app/services/curso.py
- Backend/app/tests/test_hu2_docente_matricula.py
- Frontend/src/modules/dashboard/pages/docente/DocenteEstudiantes.jsx
- Frontend/src/styles/Cursos.css

## Verificacion ejecutada
1. Pruebas unitarias:
- python -m unittest app/tests/test_hu2_docente_matricula.py
- Resultado: 2 pruebas OK.

2. Prueba runtime con Docker (API real):
- Login admin: 200.
- Login docente: 200.
- Se creo grado, materia, periodo y curso para el docente.
- Se creo estudiante de prueba y login exitoso.
- POST /api/matriculas con docente en grado/anio asignado: 200.
- POST /api/matriculas con docente fuera de su grado: 403.

## Resultado
HU2 queda efectivamente implementada para Docente, con control de alcance por grado y anio para preservar seguridad y coherencia del dominio.
