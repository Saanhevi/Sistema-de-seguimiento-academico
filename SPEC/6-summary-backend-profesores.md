# Resumen de implementación — Backend de Profesores (spec 6)

**Estado:** Implementado en el PR de docentes/profesores, con endpoints reales para listar, crear, editar y cambiar estado de docentes, conectados al modelo actual de Usuario y Docente.

---

## 1. Qué se implementó

Se desarrolló la lógica de backend real para el módulo de gestión de profesores, dejando el frontend preparado para consumir un contrato estable y coherente con el esquema actual del proyecto.

### Cambios principales
- Se creó el router de docentes bajo /api/docentes en Backend/app/routers/docente.py.
- Se implementó el servicio de negocio en Backend/app/services/docente.py con las operaciones de listar, crear, actualizar y cambiar estado.
- Se definieron los schemas de entrada/salida en Backend/app/schemas/docente.py.
- Se integró el módulo con las tablas reales Usuario y Docente, usando el modelo ORM ya existente del proyecto.
- Se aplicó hashing real de contraseñas utilizando la utilidad de seguridad del backend.
- Se protegieron los endpoints con RBAC básico usando el sistema de autenticación y dependencias del proyecto.

## 2. Alcance cubierto

### Incluye
- Listar docentes en un endpoint GET /api/docentes.
- Crear docentes en un endpoint POST /api/docentes.
- Editar docentes en un endpoint PUT /api/docentes/{id}.
- Cambiar estado de acceso en un endpoint PATCH /api/docentes/{id}/estado.
- Persistencia de datos en las tablas Usuario y Docente.
- Contrato compatible con el frontend actual para nombres, apellidos, correo, password y estado.

### No incluido en esta iteración
- Asignación compleja de materias o cursos.
- Permisos granulares por recurso.
- Eliminación definitiva de docentes desde la interfaz.

## 3. Decisiones de diseño

- Se respetó el modelo actual del sistema: los docentes se crean como usuarios con rol Docente y además se insertan en la tabla Docente.
- Las contraseñas se guardan como hash real, no como texto plano.
- La respuesta del backend se mantiene alineada con el formato esperado por el frontend para no reescribir la vista.
- Se mantuvieron los campos del contrato actual del MVP y se evitó introducir atributos no soportados por la base de datos.

## 4. Archivos clave

- Backend/app/routers/docente.py
- Backend/app/services/docente.py
- Backend/app/schemas/docente.py
- Backend/app/models/docente.py
- Backend/app/models/usuario.py
- Backend/app/main.py

## 5. Validación realizada

Se verificó el comportamiento esperado del módulo con inspección directa de los archivos y el flujo de la implementación, incluyendo:
- rutas expuestas para docentes,
- uso de dependencias de autenticación y roles,
- generación de hash de contraseña,
- persistencia de datos en las tablas relacionadas.

## 6. Estado final

El backend del módulo de profesores quedó listo para ser consumido por la interfaz frontend. La parte de asistencia permanece fuera de este alcance y se dejó separada como trabajo posterior.
