# Spec de frontend — HU6: Registrar inasistencias

**Owner:** Rafael  
**Historia de usuario:** HU6  
**Descripción:** Como profesor, quiero registrar inasistencias de los estudiantes, para llevar un control de asistencia de mis clases.

---

## 1. Contexto

La historia HU6 corresponde al módulo de asistencias del sistema académico. El backend ya fue adelantado con una estructura funcional orientada a registrar y consultar listas de asistencia por curso y fecha.

### Estado validado del backend

Se validó de forma local que el backend responde correctamente:

- La ruta raíz devuelve `200` con mensaje de estado activo.
- La documentación OpenAPI responde `200` en `/openapi.json`.
- El módulo de asistencias está integrado en el router principal y preparado para recibir peticiones desde el frontend.

### Endpoints esperados para esta HU

- `GET /api/asistencias/listas?id_curso=...&fecha=...`
  - Devuelve la lista de estudiantes del curso para una fecha específica.
- `PUT /api/asistencias/listas/{id_dia}`
  - Recibe la lista actualizada de asistencias para guardar.
- `GET /api/asistencias/listas/{id_curso}`
  - Devuelve el historial de fechas registradas por curso.
- `GET /api/docente/cursos?id_docente=...`
  - Devuelve los cursos asociados al docente que está autenticado.

---

## 2. Objetivo del frontend

Construir la interfaz del profesor para que pueda:

1. Seleccionar un curso.
2. Elegir una fecha para tomar asistencia.
3. Visualizar la lista de estudiantes del curso.
4. Marcar cada estudiante como Presente, Ausente o Tardanza.
5. Guardar la información en el backend.
6. Ver el historial de fechas registradas para el curso.

La implementación debe reutilizar el diseño del dashboard existente y tomar como referencia la estructura visual del prototipo local, manteniendo una experiencia consistente con el sistema.

---

## 3. Alcance del MVP para HU6

### Incluye

- Vista para docente en la ruta `/dashboard/docente/asistencia`.
- Selector de curso.
- Selector de fecha.
- Tabla de estudiantes con estado editable.
- Botón para guardar asistencia.
- Historial de fechas por curso.
- Integración con los servicios del backend mediante `axios` y `api.js`.

### No incluye en este sprint

- Justificación de inasistencias.
- Reportes PDF o exportación.
- Notificaciones a acudientes.
- Estadísticas o gráficos.
- Funcionalidad de eliminación de registros (corresponde a otra HU).

---

## 4. Estructura propuesta del frontend

Se recomienda conservar y completar la estructura ya iniciada en el proyecto:

```text
Frontend/src/modules/asistencias/
  components/
    AsistenciaTable.jsx
    CursoSelector.jsx
    HistorialDias.jsx
  services/
    asistenciaService.js
  styles/
    Asistencia.css

Frontend/src/modules/dashboard/pages/docente/
  DocenteAsistencia.jsx
```

### Responsabilidades

- `DocenteAsistencia.jsx`: coordina la vista completa, carga los cursos, gestiona la fecha seleccionada y maneja los estados de carga/error.
- `CursoSelector.jsx`: permite elegir el curso del docente.
- `HistorialDias.jsx`: permite elegir una fecha existente o crear una nueva para la asistencia.
- `AsistenciaTable.jsx`: renderiza la tabla de estudiantes y permite cambiar los estados.
- `asistenciaService.js`: encapsula la comunicación con la API.

---

## 5. Requisitos funcionales

### 5.1 Carga inicial

Al entrar a la vista del docente:

- Se deben cargar los cursos asociados al docente autenticado.
- Si no hay cursos, se debe mostrar un mensaje claro.
- Si ocurre un error al cargar los cursos, se debe mostrar un mensaje de error y mantener la vista estable.

### 5.2 Selección de curso

Al seleccionar un curso:

- Se debe cargar el historial de fechas asociadas a ese curso.
- La vista debe quedar preparada para mostrar la lista de asistencia de una fecha concreta.

### 5.3 Selección de fecha

Al seleccionar una fecha:

- Si la fecha ya existe en el historial, se debe cargar la información registrada.
- Si la fecha no existe, el sistema debe crear la estructura inicial para esa fecha y pre-cargar los estudiantes del curso con estado inicial `Presente`.

### 5.4 Edición de asistencia

En la tabla de estudiantes:

- Cada estudiante debe tener un selector de estado.
- Los estados permitidos son: `Presente`, `Ausente` y `Tardanza`.
- El cambio debe reflejarse inmediatamente en la interfaz.

### 5.5 Guardar asistencia

Al presionar el botón Guardar:

- Se deben enviar los registros actualizados al backend.
- Si la operación es exitosa, se debe mostrar un mensaje de confirmación.
- Si falla, se debe mostrar un mensaje de error sin romper la experiencia.

---

## 6. Requisitos de experiencia de usuario

- La interfaz debe sentirse cercana al dashboard existente y al prototipo visual.
- Debe usar estilos consistentes con el sistema actual, sin introducir Tailwind.
- La vista debe ser clara y responsiva para escritorio.
- Los mensajes de éxito o error deben ser visibles, pero no invasivos.
- La interacción debe ser sencilla para un docente que desea registrar asistencia rápidamente.

---

## 7. Requisitos técnicos

### 7.1 Servicios

Los servicios deben reutilizar el cliente central de la API en:

- `Frontend/src/services/api.js`

Se recomienda que los métodos del módulo de asistencias queden en:

- `Frontend/src/modules/asistencias/services/asistenciaService.js`

### 7.2 Formato de datos

#### Respuesta esperada al cargar la lista

```json
{
  "id_dia": 1,
  "grado": "10°",
  "materia": "Matemáticas",
  "fecha": "2026-07-23",
  "asistencias": [
    {
      "id_estudiante": 12,
      "nombres": "Carlos",
      "apellidos": "Rojas",
      "estado": "Presente"
    }
  ]
}
```

#### Payload para guardar

```json
[
  {
    "id_estudiante": 12,
    "estado": "Ausente"
  }
]
```

### 7.3 Manejo de estados

La vista debe manejar al menos estos estados:

- `loading`
- `error`
- `success`
- `listaAsistencia`
- `cursos`
- `dias`

---

## 8. Criterios de aceptación

- [ ] El docente puede acceder a la vista de asistencia desde el dashboard.
- [ ] El docente puede seleccionar un curso.
- [ ] El docente puede visualizar la lista de estudiantes para una fecha.
- [ ] El docente puede cambiar el estado de cada estudiante.
- [ ] El docente puede guardar la asistencia correctamente.
- [ ] La interfaz muestra mensajes claros de error o éxito.
- [ ] La implementación está alineada con el diseño del prototipo y el dashboard existente.

---

## 9. Definition of Done

- [ ] La vista de asistencia está implementada para docentes.
- [ ] El flujo completo de carga, edición y guardado funciona con el backend.
- [ ] Los servicios están aislados y reutilizables.
- [ ] El código queda preparado para futuras mejoras del módulo de asistencias.
- [ ] La implementación está lista para revisión en la rama de trabajo correspondiente.
