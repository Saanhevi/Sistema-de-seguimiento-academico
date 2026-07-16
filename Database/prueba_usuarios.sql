INSERT INTO usuario (nombres, apellidos, correo, password_hash, rol)
VALUES
('Samuel', 'Herrera', 'samuel@unal.edu.co', 'hash123', 'Administrador'),

('Juan', 'Perez', 'juan@colegio.edu.co', 'hash456', 'Docente'),

('Maria', 'Gomez', 'maria@colegio.edu.co', 'hash789', 'Estudiante'),

('Carlos', 'Lopez', 'carlos@gmail.com', 'hash999', 'Acudiente');

INSERT INTO administrador (id_admin)
VALUES (1);

INSERT INTO docente (id_docente, estado)
VALUES (2,'Activo');

INSERT INTO estudiante (id_estudiante, estado)
VALUES (3,'Activo');

INSERT INTO acudiente (id_acudiente)
VALUES (4);