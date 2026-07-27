# Spec — HU7: Consultar mis inasistencias

**Owner:** Rafael  
**Historia de usuario:** HU7  
**Descripción:** Como estudiante, quiero consultar mis inasistencias registradas, para conocer mi estado de asistencia.

---

## 1. Contexto

La historia HU7 complementa a HU6 y se enfoca en el rol de estudiante. El backend ya expone un endpoint preparado para consultar las asistencias de un estudiante y el frontend cuenta con una base de navegación y estructura de módulos para integración.

### Estado actual validado

- El backend ya tiene un endpoint para consultar asistencias del estudiante: `GET /api/asistencias/mis-asistencias`.
- El módulo de asistencia ya existe en el frontend y se encuentra preparado para extenderse hacia la vista de estudiante.
- La API responde correctamente en el entorno local.

---

## 2. Objetivo

Desarrollar una experiencia para que un estudiante pueda:

1. Ingresar a la vista de asistencias desde su dashboard.
2. Visualizar un listado de sus inasistencias registradas.
3. Ver la materia, la fecha y el estado de asistencia correspondiente.
4. Consultar la información de forma clara y ordenada.

La solución debe ser coherente con el diseño del dashboard actual y con la referencia del prototipo local en `C:\Users\madr\PrototipoSitioWebEducativo`.

---

## 3. Alcance del MVP para HU7

### Incluye

- Vista para estudiante en la ruta `/dashboard/estudiante/asistencia`.
- Consulta de las asistencias registradas para el estudiante autenticado.
- Visualización de:
  - materia
  - fecha
  - estado
- Integración con el endpoint del backend.
- Manejo de estados de carga y error.

### No incluye

- Justificación de inasistencias.
- Descarga de reportes.
- Notificaciones a acudientes.
- Filtros avanzados por curso o periodo.

---

## 4. Requisitos funcionales

### 4.1 Vista del estudiante

Al ingresar a la vista de asistencia:

- Se debe cargar automáticamente la información del estudiante autenticado.
- Se debe consultar la lista de asistencias asociadas a ese estudiante.
- Si no hay registros, se debe mostrar un mensaje claro.

### 4.2 Listado de asistencias

Cada registro debe mostrar:

- `materia`
- `fecha`
- `estado`

### 4.3 Ordenamiento

Los registros deben mostrarse de forma descendente por fecha, para que las asistencias más recientes aparezcan primero.

### 4.4 Manejo de errores

Si la consulta falla:

- Se debe mostrar un mensaje de error amigable.
- La interfaz debe mantenerse estable.

---

## 5. Requisitos técnicos

### 5.1 Backend

Se debe asegurar que el endpoint real del backend cumpla con el contrato esperado:

- `GET /api/asistencias/mis-asistencias`
- Debe recibir el `id_estudiante` como parámetro de consulta.
- Debe devolver una lista de objetos con el siguiente formato:

```json
[
  {
    "materia": "Matemáticas",
    "fecha": "2026-07-23",
    "estado": "Ausente"
  }
]
```

### 5.2 Frontend

Se debe implementar una vista en:

- `Frontend/src/modules/dashboard/pages/estudiante/EstudianteAsistencia.jsx`

Se recomienda reutilizar:

- `Frontend/src/modules/asistencias/services/asistenciaService.js`
- `Frontend/src/modules/asistencias/styles/Asistencia.css`

### 5.3 Autenticación

La vista debe usar el usuario autenticado del contexto para identificar al estudiante y consultar sus datos.

---

## 6. Estructura propuesta

```text
Frontend/src/modules/
  asistencias/
    services/
      asistenciaService.js
    styles/
      Asistencia.css
  dashboard/pages/estudiante/
    EstudianteAsistencia.jsx
```

### Responsabilidades

- `EstudianteAsistencia.jsx`: coordina la carga de datos y renderiza la vista.
- `asistenciaService.js`: encapsula la consulta al endpoint del backend.
- `Asistencia.css`: reutiliza estilos del módulo existente para mantener consistencia visual.

---

## 7. Criterios de aceptación

- [ ] El estudiante puede ingresar a la vista de asistencia.
- [ ] El sistema consulta las asistencias del estudiante autenticado.
- [ ] Se muestra la materia, la fecha y el estado de cada registro.
- [ ] Los registros aparecen ordenados por fecha descendente.
- [ ] Si no hay datos, se muestra un mensaje claro.
- [ ] Si hay error, se muestra un mensaje de error adecuado.
- [ ] La interfaz conserva la identidad visual del dashboard y del prototipo.

---

## 8. Definition of Done

- [ ] Backend y frontend de HU7 quedan alineados con el contrato real del proyecto.
- [ ] La vista de estudiante funciona correctamente para el flujo principal.
- [ ] El código queda preparado para futuras ampliaciones del módulo de asistencias.
- [ ] La implementación está lista para revisión.
