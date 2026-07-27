# Resumen 19 - HU19 Retiro de estudiantes (eliminacion logica)

## Historia de usuario
Como administrador del colegio, quiero eliminar estudiantes que se han retirado de la institucion, para mantener actualizada la base de datos.

## Decision funcional aplicada
Se implemento retiro logico (estado Inactivo) en lugar de borrado fisico.

Motivo:
- El estudiante tiene historial academico y operativo en tablas relacionadas (matricula, asistencia, notas, alertas).
- El borrado fisico rompe trazabilidad y aumenta el riesgo de conflicto por llaves foraneas.

## Implementacion backend
Se agrego un modulo de gestion de estudiantes para administracion:

- Endpoint para listar estudiantes (incluyendo inactivos opcionalmente):
  - GET /api/estudiantes?incluir_inactivos=true|false
- Endpoint para retiro logico:
  - PATCH /api/estudiantes/{id_estudiante}/retiro
- Ambos endpoints protegidos con RBAC para rol Administrador.

## Implementacion frontend
Se reemplazo el placeholder de administracion de estudiantes por una pantalla funcional con:
- Resumen total/activos/retirados.
- Filtros por estado.
- Tabla con accion de retiro.
- Confirmacion previa de retiro.

## Archivos modificados
- Backend/app/main.py
- Backend/app/routers/estudiante.py
- Backend/app/schemas/estudiante.py
- Backend/app/services/estudiante.py
- Backend/app/tests/test_estudiante_service.py
- Frontend/src/App.jsx
- Frontend/src/modules/dashboard/pages/admin/AdminEstudiantes.jsx
- Frontend/src/modules/estudiantes/services/estudianteService.js
- Frontend/src/styles/EstudiantesAdmin.css

## Verificacion ejecutada
1. Pruebas unitarias de servicio:
- python -m unittest app/tests/test_estudiante_service.py
- Resultado: 3 pruebas OK.

2. Prueba runtime contra API levantada en Docker:
- Login admin: 200.
- Login docente: 200.
- GET /api/estudiantes con admin: 200.
- GET /api/estudiantes con docente: 403.
- PATCH /api/estudiantes/{id}/retiro con admin: 200.
- GET /api/auth/perfil-estudiante con token previo del estudiante retirado: 401 (usuario inactivo).

## Resultado
HU19 queda implementada con retiro logico administrado por Administrador, preservando integridad historica y actualizando la operacion del sistema segun el estado del estudiante.
