# 🏫 Plataforma Gestión Académica

Sistema de Gestión Académica para instituciones educativas. Centraliza la gestión de notas, control de asistencia, promedios y alertas de rendimiento académico en tiempo real.

## 🛠️ Stack Tecnológico

- **Frontend:** React.js (Vite) -> Desplegado en **Vercel**
- **Backend:** FastAPI (Python) -> Desplegado en **Render**
- **Base de Datos:** PostgreSQL -> Hospedado en **Neon / Supabase**

# 📁 Estructura General del Proyecto

El proyecto está dividido en diferentes carpetas según la responsabilidad de cada una. Esta organización permite mantener una separación clara entre el frontend, el backend, la documentación y los archivos relacionados con la base de datos.

```text
gestion-academica/
│
├── frontend/
│   └── Aplicación cliente desarrollada en React.
│
├── backend/
│   └── API desarrollada con FastAPI y lógica de negocio.
│
├── database/
│   └── Scripts y recursos relacionados con la base de datos.
│
├── .gitignore
│   └── Archivos y carpetas que Git no debe versionar.
│
├── README.md
│   └── Documentación principal del proyecto.
│
└── docker-compose.yml (Opcional)
    └── Configuración para ejecutar los servicios mediante Docker.
```

---

# 📦 Descripción de cada carpeta

## 💻 `frontend/`

Contiene toda la interfaz gráfica del sistema.

Aquí se desarrolla la experiencia del usuario utilizando React, incluyendo las páginas, componentes, estilos y comunicación con el backend.

---

## ⚙️ `backend/`

Contiene la API del sistema.

Aquí se implementa toda la lógica de negocio, autenticación, acceso a la base de datos y servicios necesarios para el funcionamiento de la aplicación.

---

## 🗄️ `database/`

Almacena todos los recursos relacionados con la base de datos.

Ejemplos:

- Script de creación de tablas.
- Datos de prueba.
- Procedimientos almacenados (si existen).
- Backups.
- Diagramas de la base de datos.

Ejemplo de estructura:

```text
database/
│
├── schema.sql
├── inserts.sql
├── backups/
└── diagramas/
```

---


## 🚫 `.gitignore`

Define los archivos y carpetas que Git no debe subir al repositorio.

Ejemplos:

- `node_modules/`
- `venv/`
- `.env`
- Archivos temporales.

---

## 📖 `README.md`

Documento principal del proyecto.

Incluye información como:

- Descripción del sistema.
- Tecnologías utilizadas.
- Instrucciones de instalación.
- Estructura del proyecto.
- Guía de contribución.

---

## 🐳 `docker-compose.yml` *(Opcional)*

Permite levantar todos los servicios del proyecto mediante Docker.

Puede incluir:

- Backend.
- Frontend.
- Base de datos.
- Herramientas adicionales.

---

# 🚀 Organización del proyecto

Cada carpeta tiene una responsabilidad específica:

| Carpeta | Responsabilidad |
|----------|-----------------|
| **frontend/** | Interfaz de usuario desarrollada en React. |
| **backend/** | API y lógica de negocio desarrollada con FastAPI. |
| **database/** | Scripts, diagramas y recursos de la base de datos. |


Esta organización facilita el trabajo colaborativo, mejora el mantenimiento del código y permite escalar el proyecto de forma ordenada.

## 🚀 Reglas de Git para el Equipo

1. El tronco principal es `main`. Nadie sube código aquí directamente.
2. Todo el desarrollo se integra en la rama `develop`.
3. Para trabajar en una tarea, crea una rama desde `develop` usando el prefijo `feat/` o `fix/`.
   - *Ejemplo:* `feat/login-screen`
4. Para subir cambios a `develop`, se requiere abrir un **Pull Request (PR)** y que al menos un compañero lo revise.