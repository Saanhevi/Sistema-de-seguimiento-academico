# Spec: Backend — Gestión de Profesores

**Owner:** Samuel  
**Repo:** Saanhevi/Sistema-de-seguimiento-academico  
**Complementa:** SPEC 5: Frontend — Gestión de Profesores

---

## 0. Contexto

La interfaz de profesores ya fue implementada en el frontend con una experiencia de crear, listar, editar y activar/desactivar docentes. Ahora se debe conectar esa UI con un backend real que persista los datos en la base de datos existente del proyecto.

La implementación debe respetar el esquema actual de la base de datos y no introducir campos no soportados como especialidad.

---

## 1. Objetivo

Implementar la lógica de backend real para el módulo de gestión de profesores, conectando la interfaz con la base de datos existente y exponiendo endpoints REST que permitan:

- listar profesores,
- crear un profesor,
- editar un profesor,
- activar/desactivar un profesor.

---

## 2. Alcance del MVP

### Incluye

- Endpoints para gestionar docentes desde el backend.
- Integración con las tablas existentes: Usuario y Docente.
- Hash real de contraseñas usando la utilidad existente de seguridad.
- Validación básica de datos y manejo de errores.
- Compatibilidad con el contrato esperado por el frontend actual.
- Protección básica por rol usando el sistema de autenticación existente: solo administradores pueden crear, editar o cambiar estado; docentes, estudiantes y administradores pueden consultar la lista.

### No incluye

- Asignación de materias o cursos compleja.
- Reglas de RBAC complejas ni permisos granulares por recurso.
- Eliminación definitiva de profesores desde la interfaz.

---

## 3. Requisitos funcionales

### 3.1 Listar profesores

Endpoint para obtener todos los docentes del sistema.

Respuesta esperada:

- id
- nombres
- apellidos
- correo
- estado

### 3.2 Crear profesor

Endpoint para crear un docente nuevo.

Debe crear:
- un registro en la tabla Usuario,
- un registro en la tabla Docente,
- y guardar la contraseña con hash real.

Campos esperados del request:
- nombres
- apellidos
- correo
- password
- estado

### 3.3 Editar profesor

Endpoint para actualizar datos de un docente existente.

Debe actualizar:
- nombres
- apellidos
- correo
- estado

Si se envía una nueva contraseña, debe hashearse.

### 3.4 Activar / desactivar

Endpoint para cambiar el estado de acceso del docente.

---

## 4. Alineación con el modelo actual

El backend debe trabajar con las tablas reales:

- Usuario:
  - nombres
  - apellidos
  - correo
  - password_hash
  - rol

- Docente:
  - id_docente
  - estado

No se debe enviar ni persistir campos como especialidad.

---

## 5. Estructura propuesta

### Archivos a modificar

- Backend/app/routers/docente.py o equivalente si ya existe el router
- Backend/app/services/docente.py o servicio de profesores
- Backend/app/repositories/docente.py o similar
- Backend/app/schemas/docente.py o esquema de profesores
- Backend/app/main.py para registrar rutas si es necesario

### Reglas de arquitectura

- El router debe exponerse bajo un prefijo coherente con el frontend.
- El servicio debe encapsular la lógica de negocio.
- El repositorio debe manejar acceso a la base de datos.
- Los esquemas deben reflejar los campos usados por la interfaz.

---

## 6. Integración con el frontend

El frontend ya espera un contrato basado en estos campos:

- id
- nombres
- apellidos
- correo
- password
- estado

Por lo tanto, los endpoints deben responder en ese formato para no reescribir la vista.

Se recomienda que la ruta del backend sea compatible con:

- GET /api/docentes
- POST /api/docentes
- PUT /api/docentes/{id}
- PATCH /api/docentes/{id}/estado

---

## 7. Criterios de aceptación

- [ ] El backend expone endpoints reales para listar, crear, editar y cambiar estado de docentes.
- [ ] Los endpoints están protegidos con RBAC básico usando los roles existentes.
- [ ] Los datos se persisten en la base de datos existente.
- [ ] Las contraseñas se guardan como hash real.
- [ ] El frontend puede consumir estos endpoints sin reescribir la lógica de la vista.
- [ ] La implementación es consistente con el esquema actual de Usuario y Docente.
- [ ] No se agregan campos no soportados por la base de datos.

---

## 8. Definition of Done

- [ ] Se implementa la lógica real del backend para profesores.
- [ ] Se conecta con la base de datos existente.
- [ ] Se verifican los endpoints con una ejecución real.
- [ ] La implementación queda lista para ser usada por la interfaz actual.
