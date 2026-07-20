**Requerimientos del Sistema**

# **Contexto**

Plataforma web para colegios públicos de bachillerato. Centraliza el registro de notas y asistencia, calcula promedios automáticamente y emite alertas tempranas de riesgo académico. Tres roles: Administrador, Profesor y Estudiante.

# **Requerimientos Funcionales**

**Autenticación y acceso**

* **RF-01**  Inicio de sesión con correo y contraseña para los tres roles.

* **RF-02**  Recuperación y cambio de contraseña seguros.

* **RF-03**  Cada rol accede únicamente a la información que le corresponde (principio de mínima exposición).

**Administrador institucional**

* **RF-04**  Crear, editar y eliminar cuentas de estudiantes y profesores.

* **RF-05**  Crear y gestionar cursos, grados y materias; asociar materias a grados.

* **RF-06**  Asignar materias a profesores y estudiantes a cursos.

* **RF-07**  Promover estudiantes al siguiente grado al cierre del año escolar.

* **RF-08**  Bloquear la edición de notas al cerrar un periodo o el año escolar.

* **RF-09**  Configurar periodos académicos (apertura y cierre).

**Profesor**

* **RF-10**  Registrar, modificar y eliminar notas de sus materias mientras el periodo esté activo. Cada nota incluye: actividad, porcentaje, calificación (0–5) y comentario opcional.

* **RF-11**  Importar notas masivamente desde archivo Excel (.xlsx); el sistema valida el formato y reporta errores.

* **RF-12**  Registrar y corregir asistencia por sesión; el sistema impide registros duplicados para la misma sesión.

* **RF-13**  Visualizar panel del curso: promedio grupal, lista de estudiantes en riesgo, asistencia vs. notas y alertas activas.

* **RF-14**  Añadir estudiantes a sus materias por nombre.

**Estudiante**

* **RF-15**  Consultar en tiempo real sus calificaciones por materia (actividad, porcentaje, nota, comentario y promedio actual).

* **RF-16**  Consultar su historial de asistencia acumulada por materia y periodo.

* **RF-17**  Recibir alertas automáticas cuando su rendimiento o asistencia estén en riesgo.

**Cálculo automático y alertas**

* **RF-18**  Calcular promedio por materia (ponderado), promedio general del estudiante y promedio grupal del curso. Se recalcula en cada cambio de nota.

* **RF-19**  Generar alertas automáticas cuando: (a) el promedio de un estudiante baja de 3.0, (b) acumula inasistencias críticas, o (c) se detecta tendencia negativa sostenida.

**Historial y reportes**

* **RF-20**  Guardar el historial completo de calificaciones y asistencia por periodo y año; no se permite modificar registros de períodos cerrados.

* **RF-21**  Exportar reportes en PDF: por estudiante, por curso, por materia y por institución.

* **RF-22**  Registrar en bitácora toda modificación de datos críticos (quién, cuándo, qué cambió).

**Panel administrativo**

* **RF-23**  Visualizar métricas institucionales: promedio por curso/grado, indicadores de riesgo agregados y estadísticas de inasistencia.

# **Requerimientos No Funcionales**

**Seguridad**

* **RNF-01**  Contraseñas almacenadas con hashing robusto (bcrypt o equivalente). Comunicación exclusivamente por HTTPS.

* **RNF-02**  Protección contra vulnerabilidades OWASP Top 10 (inyección SQL, XSS, CSRF, etc.).

* **RNF-03**  Control de acceso por roles (RBAC); ningún usuario puede operar fuera de su rol.

* **RNF-04**  Bitácora de auditoría inmutable para cambios en notas y asistencia.

**Privacidad**

* **RNF-05**  Cumplimiento de normativas de protección de datos personales de menores. Datos usados exclusivamente para los fines del sistema.

**Disponibilidad y rendimiento**

* **RNF-06**  Disponibilidad ≥ 99% en horario escolar. Despliegue en infraestructura cloud con tolerancia a fallos.

* **RNF-07**  Soporte de al menos 100 usuarios concurrentes sin degradación perceptible. Tiempo de respuesta \< 3 s en operaciones críticas.

**Usabilidad y accesibilidad**

* **RNF-08**  Interfaz responsive; funciona en computador, tableta y celular sin pérdida de funcionalidad.

* **RNF-09**  Cumplimiento de WCAG 2.1 nivel AA (contraste, etiquetas, navegación por teclado).

* **RNF-10**  Navegación intuitiva; un usuario nuevo debe poder completar las tareas principales sin capacitación extensa.

**Mantenibilidad y escalabilidad**

* **RNF-11**  Arquitectura de tres capas (presentación / lógica / datos) que permita escalar módulos de forma independiente.

* **RNF-12**  Código versionado en Git con integración continua (CI) y pruebas automatizadas unitarias y de integración.

# **Reglas de Negocio**

* **RN-01**  Las notas solo se pueden crear o modificar mientras el periodo académico esté abierto.

* **RN-02**  Al cerrar un periodo o el año escolar, las notas quedan bloqueadas de forma permanente.

* **RN-03**  Solo el profesor asignado a una materia puede modificar sus notas.

* **RN-04**  Un estudiante solo puede acceder a su propia información académica.

* **RN-05**  La asistencia se registra una única vez por sesión; el sistema rechaza duplicados.

* **RN-06**  Toda materia debe estar asociada a un grado o curso; no se permiten materias sin asignación.

* **RN-07**  Las alertas académicas son generadas automáticamente por el sistema; no se crean de forma manual.

* **RN-08**  Cada modificación de nota o asistencia dispara el recálculo inmediato de promedios e indicadores de riesgo.

# **Stack Tecnológico**

* **—**  Frontend: JavaScript \+ React (SPA responsive).

* **—**  Backend: FastAPI (Python) con autenticación JWT.

* **—**  Base de datos: MySQL.

* **—**  Control de versiones: GitHub \+ GitHub Actions (CI/CD).