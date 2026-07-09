# 🏫 Plataforma Gestión Académica

Sistema de Gestión Académica para instituciones educativas. Centraliza la gestión de notas, control de asistencia, promedios y alertas de rendimiento académico en tiempo real.

## 🛠️ Stack Tecnológico

- **Frontend:** React.js (Vite) -> Desplegado en **Vercel**
- **Backend:** FastAPI (Python) -> Desplegado en **Render**
- **Base de Datos:** PostgreSQL -> Hospedado en **Neon / Supabase**

## 📂 Estructura del Proyecto (Monorepo)

- `/frontend`: Código de la interfaz de usuario (React).
- `/backend`: Código de la API y lógica de negocio (FastAPI).

## 🚀 Reglas de Git para el Equipo

1. El tronco principal es `main`. Nadie sube código aquí directamente.
2. Todo el desarrollo se integra en la rama `develop`.
3. Para trabajar en una tarea, crea una rama desde `develop` usando el prefijo `feat/` o `fix/`.
   - *Ejemplo:* `feat/login-screen`
4. Para subir cambios a `develop`, se requiere abrir un **Pull Request (PR)** y que al menos un compañero lo revise.