CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL, 
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL, 
    rol VARCHAR(20) NOT NULL CHECK (
        rol IN ('Administrador', 'Docente', 'Acudiente', 'Estudiante')
    )
);

CREATE TABLE IF NOT EXISTS Administrador (
    id_admin INTEGER PRIMARY KEY,
    
    FOREIGN KEY (id_admin)
        REFERENCES  Usuario(id_usuario)
);

CREATE TABLE IF NOT EXISTS Docente (
    id_docente INTEGER PRIMARY KEY, 
    estado VARCHAR(20) NOT NULL CHECK (
        estado IN ('Activo', 'Inactivo')
    ),
    FOREIGN KEY (id_docente)
        REFERENCES Usuario(id_usuario)
);

CREATE TABLE IF NOT EXISTS Estudiante (
    id_estudiante INTEGER PRIMARY KEY,
    estado VARCHAR(20) NOT NULL CHECK (
        estado IN ('Activo', 'Inactivo')
    ),

    FOREIGN KEY (id_estudiante)
        REFERENCES Usuario(id_usuario)
);

CREATE TABLE IF NOT EXISTS Acudiente (
    id_acudiente INTEGER PRIMARY KEY,

    FOREIGN KEY (id_acudiente)
        REFERENCES Usuario(id_usuario)
);


CREATE TABLE IF NOT EXISTS EstudianteAcudiente (
    id_estudiante INTEGER,
    id_acudiente INTEGER,

    PRIMARY KEY(id_estudiante, id_acudiente),

    FOREIGN KEY (id_estudiante)
        REFERENCES Estudiante(id_estudiante),

    FOREIGN KEY (id_acudiente)
        REFERENCES Acudiente(id_acudiente)
 
);

CREATE TABLE IF NOT EXISTS Materia (
    id_materia INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL 

);

CREATE TABLE IF NOT EXISTS Grado (
    id_grado INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    nombre VARCHAR(10) NOT NULL 

);

CREATE TABLE IF NOT EXISTS Matricula (
    id_matricula INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_estudiante INTEGER NOT NULL,
    id_grado INTEGER NOT NULL,
    anio INTEGER NOT NULL, 

    FOREIGN KEY (id_estudiante) 
        REFERENCES Estudiante(id_estudiante),
    
    FOREIGN KEY (id_grado) 
        REFERENCES Grado(id_grado),

    UNIQUE (id_estudiante, anio)
);

CREATE TABLE IF NOT EXISTS PeriodoAcademico(
    id_periodo INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    nombre VARCHAR(20) NOT NULL,
    anio INTEGER NOT NULL,
    estado VARCHAR(20) NOT NULL CHECK(
        estado IN ('Abierto', 'Cerrado')
    )

);

CREATE TABLE IF NOT EXISTS Curso (
    id_curso INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    id_docente INTEGER NOT NULL,
    id_grado INTEGER NOT NULL,
    id_materia INTEGER NOT NULL,
    id_periodo INTEGER NOT NULL,

    FOREIGN KEY (id_docente)
        REFERENCES Docente(id_docente),

    FOREIGN KEY (id_grado)
        REFERENCES Grado(id_grado),

    FOREIGN KEY (id_materia)
        REFERENCES Materia(id_materia),

    FOREIGN KEY (id_periodo)
        REFERENCES PeriodoAcademico(id_periodo),

    UNIQUE (id_docente, id_grado, id_materia, id_periodo)
);

CREATE TABLE IF NOT EXISTS Alerta (
    id_alerta INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_estudiante INTEGER NOT NULL,
    id_curso INTEGER , -- Puede ser null y no estar asociada a un curso directamente
    tipo VARCHAR(100) NOT NULL,
    mensaje VARCHAR(200) NOT NULL,
    nivel VARCHAR(10) NOT NULL CHECK (
        nivel IN ('Bajo', 'Medio', 'Alto')
    ),
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    estado VARCHAR(20) NOT NULL CHECK(
        estado IN ('Pendiente', 'Vista', 'Atendida')
    ),

    FOREIGN KEY (id_estudiante)
        REFERENCES Estudiante(id_estudiante),

    FOREIGN KEY (id_curso) 
        REFERENCES Curso(id_curso)

);

CREATE TABLE IF NOT EXISTS DiaAsistible (
    id_dia INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_curso INTEGER NOT NULL,
    fecha DATE NOT NULL,

    FOREIGN KEY (id_curso)
        REFERENCES Curso(id_curso)

);

CREATE TABLE IF NOT EXISTS HistorialAsistencia (
    id_dia INTEGER NOT NULL,
    id_estudiante INTEGER NOT NULL, 
    estado VARCHAR(20) NOT NULL CHECK (
        estado IN ('Presente', 'Ausente', 'Retardo', 'Excusa')
    ), 

    PRIMARY KEY (id_dia, id_estudiante),

    FOREIGN KEY (id_dia) 
        REFERENCES DiaAsistible(id_dia),

    FOREIGN KEY (id_estudiante) 
        REFERENCES Estudiante(id_estudiante)
);

CREATE TABLE IF NOT EXISTS SeccionPorcentaje (
    id_seccion INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    nombre_seccion VARCHAR(50) NOT NULL, 
    porcentaje NUMERIC(5,2) NOT NULL,
    id_curso INTEGER NOT NULL, 

    FOREIGN KEY (id_curso) 
        REFERENCES Curso(id_curso)
);

CREATE TABLE IF NOT EXISTS ActividadEvaluativa (
    id_actividad INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    nombre VARCHAR(50) NOT NULL, 
    fecha DATE NOT NULL,
    id_seccion INTEGER NOT NULL, 

    FOREIGN KEY (id_seccion) 
        REFERENCES SeccionPorcentaje(id_seccion)

);

CREATE TABLE IF NOT EXISTS Nota (
    id_nota INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_actividad INTEGER NOT NULL,
    id_estudiante INTEGER NOT NULL, 
    calificacion NUMERIC(3,2) NOT NULL, 
    comentario VARCHAR(100),

    FOREIGN KEY (id_actividad)
        REFERENCES ActividadEvaluativa(id_actividad),
    
    FOREIGN KEY (id_estudiante) 
        REFERENCES Estudiante(id_estudiante)

);