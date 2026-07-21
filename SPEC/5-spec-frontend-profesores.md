# Spec: Frontend — Gestión de Profesores

**Owner:** Samuel  
**Repo:** `Saanhevi/Sistema-de-seguimiento-academico`  
**Complementa:** `docs/sprint-2-asignacion-tareas.md` y `docs/Historias de usuario.md`  
**Rama sugerida:** `feat/profesores-frontend`

---

## 0. Contexto y estado actual

El sprint 2 asigna a Samuel la historia de “Agregar profesores al sistema” dentro del módulo de Gestión de Profesores.

Estado real del proyecto al iniciar esta tarea:

- El login y la autenticación por roles ya están funcionando en el backend.
- La ruta administrativa `/dashboard/admin/profesores` ya existe en el router y apunta a un placeholder en `Frontend/src/modules/dashboard/pages/admin/AdminProfesores.jsx`.
- El panel administrativo general ya existe en el proyecto, con estilos reutilizables en `Frontend/src/styles/Dashboard.css` y variables en `Frontend/src/styles/variables.css`.
- No hay todavía una implementación real del módulo de profesores en el frontend ni un CRUD de docentes completamente integrado con el backend.
- En el backend ya existen endpoints relacionados con asistencia bajo `/asistencias`, pero esa historia es independiente de la gestión de profesores.

Por eso, esta primera iteración debe enfocarse en dejar la interfaz lista, funcional y bien estructurada para que luego se conecte con la lógica de backend sin reescribir el flujo desde cero.

---

## 1. Objetivo

Construir la interfaz administrativa para gestionar profesores (docentes) en el panel de administración, con un enfoque visual inspirado en el prototipo local `C:\Users\madr\PrototipoSitioWebEducativo`, pero adaptado a las convenciones reales del proyecto actual.

La meta no es implementar todavía toda la lógica del backend, sino dejar el frontend preparado para:

- crear profesores,
- listarlos,
- editarlos,
- activar/desactivar su acceso,
- y mostrar un estado claro del módulo en la UI.

---

## 2. Alcance del MVP

### Incluye

- Vista de administración para profesores en `/dashboard/admin/profesores`.
- Lista de profesores con estado activo/inactivo.
- Formulario para crear un nuevo profesor.
- Formulario para editar un profesor existente.
- Filtros rápidos por estado.
- Resumen visual con métricas básicas: total, activos, inactivos.
- Estructura de servicio preparada para conectar al backend cuando exista el endpoint.

### No incluye en esta iteración

- Lógica de permisos RBAC real en la UI.
- Integración completa con endpoints reales de backend. Agrega TODOs para implementar después los llamados a los endpoints
- Eliminación definitiva de profesores desde la interfaz.
- Asignación compleja de materias o grados con reglas transversales.
- Cambios en `AppRouter.jsx` o `PortalAdmin.jsx`.

---

## 3. Referencia visual

Se toma como referencia principal la vista de docentes del prototipo local:

- `C:\Users\madr\PrototipoSitioWebEducativo\src\app\components\admin\AdminDocentes.tsx`

### Patrones a reutilizar del prototipo

- Encabezado con botón “Nuevo docente”.
- Tarjetas con información resumida por profesor.
- Modal o panel emergente para crear/editar.
- Filtros de estado: todos / activos / inactivos.
- Uso de chips o badges para mostrar especialidad, materias o grados asignados.

### Adaptación al proyecto real

No se copiará el código del prototipo tal cual. Se traducirá a las convenciones actuales del repo:

- React JS plano, no TypeScript.
- Estilos con CSS manual, no Tailwind.
- Reutilizar clases `.panel`, `.panel-header`, `.panel-title` de `Dashboard.css`.
- Usar variables CSS de `variables.css` en vez de colores hardcodeados.

---

## 4. Diseño de la interfaz

### 4.1. Página principal: AdminProfesores

La vista debe reemplazar el placeholder actual en `Frontend/src/modules/dashboard/pages/admin/AdminProfesores.jsx`.

Debe mostrar:

- un encabezado con el título “Profesores”;
- un botón principal para agregar profesor;
- una sección de métricas rápidas;
- una lista de profesores en formato de tarjetas;
- filtros por estado; y
- un modal o panel para crear/editar.

### 4.2. Formulario de profesor

El formulario debe incluir al menos estos campos, alineados con la estructura real de la base de datos:

- Nombres
- Apellidos
- Correo institucional
- Contraseña inicial (campo temporal, útil para el flujo de creación)
- Estado activo/inactivo

No se debe agregar un campo de “especialidad” en esta versión porque la base de datos actual no tiene una columna para ese dato en las tablas `Usuario` ni `Docente` definidas en `Database/schemas.sql`.

Campos opcionales o de preparación para el futuro:

- asignación de materias o cursos
- visualización de estado de acceso

Estos últimos pueden dejarse como TODOs o como información visual, pero no deben bloquear el MVP si el backend no los soporta aún.

### 4.3. Estado visual de cada profesor

Cada tarjeta debe mostrar:

- iniciales del nombre como avatar simple,
- nombres y apellidos del profesor,
- correo institucional,
- estado activo/inactivo,
- y acciones rápidas para editar o cambiar estado.

---

## 5. Comportamiento de la UI (MVP)

### Crear profesor

Al hacer clic en “Nuevo profesor”:

- se abre un modal o panel con el formulario vacío;
- al completar los campos y guardar, el profesor aparece en la lista.

### Editar profesor

Al hacer clic en editar en una tarjeta:

- se cargan los datos del profesor en el formulario;
- al guardar, se actualizan los datos en la vista.

### Activar / desactivar

Debe existir una acción visible para cambiar el estado del profesor entre activo e inactivo.

### Filtrar

Debe haber al menos tres filtros:

- Todos
- Activos
- Inactivos

### Estado inicial

Mientras el backend no esté listo, la vista puede trabajar con datos locales o mock data. La implementación debe dejar claro que esa fuente es temporal y que el servicio ya está preparado para reemplazarla por llamadas reales.

---

## 6. Estructura de archivos propuesta

### Archivos nuevos o a modificar

```text
Frontend/src/modules/profesores/
  components/
    ProfesorModal.jsx
    ProfesorCard.jsx
  services/
    profesorService.js

Frontend/src/modules/dashboard/pages/admin/
  AdminProfesores.jsx

Frontend/src/styles/
  Profesores.css   (opcional, si se necesitan clases específicas)
```

### Reglas de arquitectura

- `AdminProfesores.jsx` debe ser el componente orquestador de la vista.
- `ProfesorModal.jsx` maneja el formulario de creación/edición.
- `ProfesorCard.jsx` renderiza la tarjeta de cada profesor.
- `profesorService.js` debe encapsular las operaciones de lectura/escritura para facilitar luego la integración con el backend.

---

## 7. Integración con el backend (preparación futura)

Aunque esta iteración es frontend puro, el código debe dejarse preparado para conectar con el backend más adelante.

### Recomendación de diseño

Crear en `profesorService.js` funciones con este contrato conceptual:

```js
listarProfesores()
crearProfesor(data)
actualizarProfesor(id, data)
activarDesactivarProfesor(id, estado)
```

### Reglas de consumo

- No manejar el token manualmente en la vista.
- Reutilizar la instancia de axios ya existente en `Frontend/src/services/api.js`.
- Seguir el patrón de `Frontend/src/modules/auth/services/authService.js`.
- Si el backend aún no está listo, usar un estado local temporal y dejar TODOs claros en el servicio.

### Alineación con el backend actual

La estructura real de persistencia para este módulo es:

- `Usuario`: `nombres`, `apellidos`, `correo`, `password_hash`, `rol`
- `Docente`: `id_docente`, `estado`

Por eso, la interfaz debe enviar y mostrar datos compatibles con esos campos. No debe enviarse un campo `especialidad` ni ningún otro atributo que no exista en el esquema actual.

Además, el backend ya expone rutas de asistencia bajo `/asistencias` para la historia de registrar inasistencias. Esa funcionalidad corresponde a un flujo distinto del CRUD de profesores y debe mantenerse fuera de esta spec, aunque el frontend pueda reutilizar el mismo patrón de consumo más adelante.

---

## 8. Estilo y patrón de implementación

### Reutilización de estilos existentes

- Usar `.panel`, `.panel-header` y `.panel-title` de `Dashboard.css`.
- Reutilizar variables de `variables.css` para colores, radios y sombras.
- No introducir Tailwind ni shadcn en esta iteración.

### Diseño visual

- La UI debe sentirse alineada con el panel administrativo existente del proyecto.
- Se puede usar un estilo limpio y minimalista, similar al prototipo, pero sin romper la estética actual del sistema.

---

## 9. Criterios de aceptación

- [ ] La ruta `/dashboard/admin/profesores` muestra una vista funcional para profesores.
- [ ] Se puede crear un profesor desde la interfaz usando los campos reales del esquema (`nombres`, `apellidos`, `correo`, `password`, `estado`).
- [ ] Se puede editar un profesor desde la interfaz.
- [ ] Se pueden ver los profesores en una lista con estado visible.
- [ ] Existen filtros por estado activos/inactivos/todos.
- [ ] La implementación reutiliza los estilos del panel administrativo actual.
- [ ] No se modifican `AppRouter.jsx` ni `PortalAdmin.jsx`.
- [ ] El código está preparado para reemplazar datos mock por llamadas reales al backend sin reescribir toda la vista.
- [ ] El componente queda listo para ser extendido luego con la lógica de backend del módulo de Profesores.
- [ ] La interfaz no incorpora campos no soportados por la base de datos, como `especialidad`, en esta iteración.

---

## 10. Definition of Done

- [ ] Se reemplaza el placeholder de `AdminProfesores` por una interfaz real y usable.
- [ ] La vista permite crear, listar y editar profesores desde el frontend.
- [ ] El módulo está bien estructurado por componentes y servicio.
- [ ] La implementación es consistente con el diseño visual del prototipo y el sistema actual.
- [ ] Se documenta en standup que la parte de frontend queda lista y que la lógica de backend se dejará para la siguiente fase.
- [ ] PR contra `develop` con revisión previa.
