# 🏫 Plataforma Gestión Académica

Sistema de Gestión Académica para instituciones educativas. Centraliza la gestión de notas, control de asistencia, promedios y alertas de rendimiento académico en tiempo real.

## 🛠️ Stack Tecnológico

- **Frontend:** React.js (Vite) -> Desplegado en **Vercel**
- **Backend:** FastAPI (Python) -> Desplegado en **Render**
- **Base de Datos:** PostgreSQL -> Hospedado en **Neon / Supabase**

---

# 🐳 Instalación y Puesta en Marcha con Docker Compose (recomendado)

Levanta base de datos, backend y frontend con un solo comando, sin instalar Python, Node ni PostgreSQL en tu máquina.

## Requisitos previos

- [Docker](https://docs.docker.com/get-docker/) con Docker Compose.
  - **Windows / macOS:** instala [Docker Desktop](https://www.docker.com/products/docker-desktop/) (incluye Docker Compose). En Windows se recomienda el backend WSL2 y dejar Docker Desktop abierto antes de ejecutar los comandos.
  - **Linux:** Docker Engine + el plugin `docker-compose-plugin`.

## 1. Clonar el repositorio

**macOS / Linux (bash):**

```bash
git clone <url-del-repositorio>
cd Sistema-de-seguimiento-academico
```

**Windows (PowerShell o CMD):**

```powershell
git clone <url-del-repositorio>
cd Sistema-de-seguimiento-academico
```

## 2. Levantar los servicios

El comando de Docker Compose es idéntico en Windows, macOS y Linux (bash, PowerShell o CMD). Ejecútalo desde la raíz del proyecto, donde está `docker-compose.yml`:

```bash
docker compose up -d --build
```

Esto levanta:

| Servicio | URL | Notas |
|---|---|---|
| Frontend | http://localhost:5173 | Vite con hot-reload (código montado desde `./Frontend`) |
| Backend | http://localhost:8000 | Uvicorn con `--reload` (código montado desde `./Backend`), docs en `/docs` |
| Base de datos | `localhost:5433` | Postgres, base `gestion_academica`, usuario/contraseña `postgres`/`postgres`. `Database/schemas.sql` se aplica automáticamente la primera vez que se crea el volumen. |

> Si ya tienes Postgres corriendo localmente en el puerto 5432, no hay conflicto: el contenedor de la base de datos se publica en el puerto **5433** del host (por dentro de Docker sigue siendo `db:5432`).

## 3. Crear usuarios de prueba (solo si el proyecto es nuevo)

El volumen de la base de datos queda vacío la primera vez que levantas el proyecto (o después de un `docker compose down -v`). Para poder iniciar sesión, crea los usuarios de prueba dentro del contenedor:

```bash
docker compose run --rm seed
```

Mismo comando en Windows (PowerShell/CMD), macOS o Linux. Esto crea (si aún no existen):

| Rol | Correo | Contraseña |
|---|---|---|
| Docente | `profesor_real@colegio.edu.co` | `clave123` |
| Administrador | `admin_real@colegio.edu.co` | `admin123` |

> El script es idempotente: si el proyecto ya tenía datos de una ejecución anterior, lo omite sin error. No hace falta volver a correrlo en cada `docker compose up`, solo cuando el proyecto es nuevo o reiniciaste el volumen con `-v`.

## Comandos útiles

```bash
docker compose logs -f backend    # logs de un servicio
docker compose down               # detener y eliminar contenedores (conserva los datos de la BD)
docker compose down -v            # además borra el volumen de la base de datos (el próximo `up` requiere volver a correr el seed)
```

> Las credenciales (`SECRET_KEY`, contraseña de Postgres, etc.) están fijadas como valores de desarrollo directamente en `docker-compose.yml`. No están pensadas para producción.

---

# ⚙️ Instalación y Puesta en Marcha manual (sin Docker)

## Requisitos previos

- Python 3.10+
- Node.js 18+ y npm
- PostgreSQL 14+ corriendo localmente (o accesible por red)

## 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd Sistema-de-seguimiento-academico
```

## 2. Base de datos

Crea la base de datos y las tablas usando los scripts de `Database/`:

```bash
psql -U postgres -f Database/create_database.sql
psql -U postgres -d gestion_academica -f Database/schemas.sql
```

> `create_database.sql` elimina (si existe) y vuelve a crear la base `gestion_academica`. Ajusta el usuario (`-U`) y host (`-h`) según tu instalación de PostgreSQL.

## 3. Backend (FastAPI)

```bash
cd Backend
python -m venv .venv
source .venv/bin/activate      # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `Backend/.env` con tus propios valores:

```env
DATABASE_URL=postgresql+psycopg://<usuario>:<contraseña>@localhost:5432/gestion_academica
SECRET_KEY=<una-clave-secreta-propia>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Levanta el servidor:

```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000` (documentación interactiva en `/docs`).

### Usuarios de prueba (opcional)

La base de datos queda vacía tras aplicar `schemas.sql`. Para poder iniciar sesión, genera usuarios de prueba con contraseñas hasheadas correctamente:

```bash
cd Backend
.venv/bin/python crear_usuario_test.py
```

Esto crea (si aún no existen) los siguientes usuarios:

| Rol | Correo | Contraseña |
|---|---|---|
| Docente | `profesor_real@colegio.edu.co` | `clave123` |
| Administrador | `admin_real@colegio.edu.co` | `admin123` |

> El script es idempotente: si el usuario ya existe, lo omite. `Database/prueba_usuarios.sql` también inserta usuarios de ejemplo, pero con `password_hash` ficticios (no funcionan para iniciar sesión); úsalo solo para probar consultas, no login.

## 4. Frontend (React + Vite)

En otra terminal:

```bash
cd Frontend
npm install
npm run dev
```

La aplicación queda disponible en `http://localhost:5173`.

## Resumen

Backend y frontend son procesos independientes: cada uno corre en su propia terminal (pasos 3 y 4). Ambos deben estar activos para que la aplicación funcione de extremo a extremo, ya que el frontend consume la API del backend.

---

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