# 📁 Estructura del Frontend

El frontend está organizado siguiendo una arquitectura **basada en módulos (Feature-Based Architecture)**. Cada módulo representa una funcionalidad del sistema y contiene todos los archivos relacionados con ella (páginas, componentes, servicios, hooks y estilos).

Esta organización facilita el mantenimiento del proyecto, reduce conflictos entre los integrantes del equipo y permite escalar la aplicación de forma ordenada.

```text
frontend/
│
├── public/
│   └── Archivos públicos (favicon, imágenes estáticas, etc.).
│
├── src/
│
│   ├── assets/
│   │   └── Recursos estáticos globales como imágenes, íconos y fuentes.
│   │
│   ├── components/
│   │   └── Componentes reutilizables en toda la aplicación.
│   │      Ejemplo:
│   │      - Button
│   │      - Input
│   │      - Modal
│   │      - Navbar
│   │      - Sidebar
│   │      - Loader
│   │
│   ├── modules/
│   │
│   │   ├── auth/
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   ├── hooks/
│   │   │   └── styles/
│   │   │
│   │   ├── dashboard/
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   ├── hooks/
│   │   │   └── styles/
│   │   │
│   │   ├── estudiantes/
│   │   ├── profesores/
│   │   ├── cursos/
│   │   ├── materias/
│   │   ├── notas/
│   │   ├── asistencias/
│   │   ├── alertas/
│   │   └── estadisticas/
│   │
│   ├── services/
│   │   └── Configuración global para consumir la API.
│   │
│   ├── context/
│   │   └── Contextos globales de React (ej. autenticación).
│   │
│   ├── routes/
│   │   └── Configuración de las rutas de la aplicación.
│   │
│   ├── utils/
│   │   └── Funciones auxiliares reutilizables.
│   │
│   ├── styles/
│   │   └── Estilos globales de la aplicación.
│   │
│   ├── App.jsx
│   └── main.jsx
│
├── package.json
└── vite.config.js
```

---

# 📦 Estructura de un módulo

Todos los módulos siguen la misma estructura para mantener consistencia en el proyecto.

Ejemplo:

```text
modules/
└── notas/
    │
    ├── pages/
    ├── components/
    ├── services/
    ├── hooks/
    └── styles/
```

### 📄 pages/

Contiene las páginas principales del módulo.

Cada archivo representa una vista que puede ser navegada mediante las rutas del sistema.

Ejemplos:

- ListaNotas.jsx
- RegistrarNota.jsx
- EditarNota.jsx

---

### 🧩 components/

Contiene componentes exclusivos del módulo.

Estos componentes **no deben utilizarse en otros módulos**, ya que fueron creados para resolver necesidades específicas de esa funcionalidad.

Ejemplos:

- TablaNotas.jsx
- FormularioNota.jsx
- CardPromedio.jsx
- ImportarExcel.jsx

---

### 🌐 services/

Contiene las funciones encargadas de comunicarse con el backend.

Aquí se realizan las peticiones HTTP (GET, POST, PUT, DELETE) utilizando la API del sistema.

Ejemplo:

```javascript
obtenerNotas()
crearNota()
actualizarNota()
eliminarNota()
```

---

### 🪝 hooks/

Contiene hooks personalizados de React.

Permiten reutilizar lógica del módulo y mantener los componentes más limpios.

Ejemplo:

```javascript
useNotas()
```

---

### 🎨 styles/

Contiene los estilos específicos del módulo.

Los estilos que solo pertenecen a esta funcionalidad deben almacenarse aquí.

---

# 📌 Componentes Globales vs Componentes del Módulo

## src/components/

Se utiliza para componentes reutilizables en toda la aplicación.

Ejemplos:

- Button
- Input
- Modal
- Navbar
- Sidebar
- Loader
- Tabla Genérica

Estos componentes pueden ser utilizados por cualquier módulo.

---

## modules/*/components/

Se utiliza para componentes exclusivos de un módulo.

Ejemplos del módulo de notas:

- TablaNotas
- FormularioNota
- CardPromedio
- ImportarExcel

Estos componentes únicamente deben utilizarse dentro de su propio módulo.

---

# 🚀 Ventajas de esta arquitectura

- Organización clara del proyecto.
- Cada funcionalidad está aislada en su propio módulo.
- Facilita el trabajo colaborativo entre los integrantes del equipo.
- Reduce conflictos al trabajar en Git.
- Permite escalar el sistema agregando nuevos módulos sin modificar la estructura existente.
- Favorece la reutilización de componentes y la separación de responsabilidades.