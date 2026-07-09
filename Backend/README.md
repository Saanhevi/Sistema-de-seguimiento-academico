# 📁 Estructura del Backend

El backend está desarrollado con **FastAPI** y organizado siguiendo una arquitectura por capas (**Router → Service → Repository**), lo que permite separar responsabilidades y facilitar el mantenimiento del proyecto.

```text
backend/
│
├── app/
│   │
│   ├── main.py
│   │   └── Punto de entrada de la aplicación.
│   │
│   ├── core/
│   │   └── Configuración global del proyecto
│   │      (base de datos, seguridad, variables de entorno y dependencias).
│   │
│   ├── routers/
│   │   └── Endpoints de la API.
│   │      Reciben las peticiones HTTP y llaman a los Services.
│   │
│   ├── services/
│   │   └── Contienen la lógica de negocio del sistema.
│   │
│   ├── repositories/
│   │   └── Gestionan el acceso a la base de datos.
│   │
│   ├── models/
│   │   └── Modelos que representan las tablas de la base de datos.
│   │
│   ├── schemas/
│   │   └── Modelos Pydantic para validar los datos de entrada y salida.
│   │
│   ├── utils/
│   │   └── Funciones auxiliares reutilizables.
│   │
│   └── tests/
│       └── Pruebas unitarias e integrales.
│
├── requirements.txt
│   └── Dependencias del proyecto.
│
├── .env
│   └── Variables de entorno (no debe subirse al repositorio).
│
└── README.md
```

---

# 📦 Responsabilidad de cada carpeta

## 🚀 `app/`

Contiene todo el código fuente del backend.

---

## ⚙️ `core/`

Agrupa la configuración general del proyecto.

Ejemplos:

- Configuración de FastAPI.
- Conexión a la base de datos.
- Seguridad (JWT, hash de contraseñas).
- Variables de entorno.
- Dependencias compartidas.

---

## 🌐 `routers/`

Define los endpoints de la API.

Su responsabilidad es:

- Recibir la petición del cliente.
- Validar los datos recibidos.
- Llamar al Service correspondiente.
- Retornar la respuesta.

**No debe contener lógica de negocio.**

---

## 🧠 `services/`

Implementa toda la lógica de negocio del sistema.

Aquí se realizan validaciones como:

- Verificar permisos.
- Calcular promedios.
- Generar alertas.
- Validar reglas del sistema.
- Coordinar el uso de uno o varios Repositories.

---

## 🗄️ `repositories/`

Es la única capa que interactúa con la base de datos.

Su responsabilidad es realizar operaciones CRUD.

No debe contener lógica de negocio.

---

## 🏛️ `models/`

Representa las entidades del sistema y las tablas de la base de datos mediante el ORM.

---

## 📄 `schemas/`

Define los modelos de validación utilizando Pydantic.

Permite controlar cómo llegan y cómo se envían los datos a través de la API.

---

## 🛠️ `utils/`

Contiene funciones reutilizables que pueden ser utilizadas por diferentes módulos.

Ejemplos:

- Manejo de archivos Excel.
- Cálculo de promedios.
- Generación de tokens.
- Envío de correos.

---

## 🧪 `tests/`

Contiene las pruebas del backend para verificar el correcto funcionamiento de la aplicación.

---

# 🔄 Flujo de una petición

Todas las solicitudes siguen el mismo recorrido:

```text
Cliente
    │
    ▼
Router
    │
    ▼
Service
    │
    ▼
Repository
    │
    ▼
Base de Datos
    │
    ▲
Repository
    │
    ▲
Service
    │
    ▲
Router
    │
    ▲
Cliente
```

Esta estructura mantiene una separación clara de responsabilidades, facilita el trabajo colaborativo y permite escalar el proyecto agregando nuevos módulos sin afectar la organización existente.