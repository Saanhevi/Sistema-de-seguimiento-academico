# Resumen 10 - Alineación HU2 Matrículas (actor y permisos)

## Contexto
Se detectó una discrepancia entre router y servicio en la HU2:
- El endpoint `POST /api/matriculas` en router aceptaba `Administrador` y `Docente`.
- La lógica de negocio en servicio rechazaba todo usuario que no fuera `Administrador`.

Esto hacía que la API anunciara una capacidad para docentes que en ejecución real nunca se cumplía.

## Cambio aplicado
Se alineó el permiso en el router para que `POST /api/matriculas` requiera únicamente rol `Administrador`, en coherencia con la validación del servicio y con la interfaz disponible actualmente.

## Archivo modificado
- Backend/app/routers/curso.py

## Verificación realizada
Pruebas ejecutadas contra la API levantada con Docker Compose:

1. Servicios activos:
- `db`, `backend`, `frontend` en estado `Up`.

2. Disponibilidad:
- `GET /docs` -> `200`.

3. Autenticación:
- Login administrador (`admin_real@colegio.edu.co`) -> `200`.
- Login docente (`profesor_real@colegio.edu.co`) -> `200`.

4. Permiso de matrícula (HU2):
- `POST /api/matriculas` con token administrador -> `404 Estudiante no encontrado` (la autorización sí permitió entrar a regla de negocio).
- `POST /api/matriculas` con token docente -> `403 No tienes permiso para esta acción`.

## Conclusión
Con el estado actual del producto, HU2 queda implementada para `Administrador` y no para `Docente`.
La documentación de historias debe reflejar ese actor, o se debe planificar un cambio funcional adicional para habilitar la operación a docentes (backend + UI docente).
