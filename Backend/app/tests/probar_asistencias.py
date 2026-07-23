from app.core.database import SessionLocal
from app.models.usuario import Usuario
from app.models.docente import Docente
from app.models.estudiante import Estudiante
from app.models.grado import Grado
from app.models.materia import Materia
from app.models.periodo_academico import PeriodoAcademico
from app.models.curso import Curso
from app.models.matricula import Matricula


def poblar_asistencias():

    db = SessionLocal()

    try:

        # ===========================
        # DOCENTE
        # ===========================

        usuario_docente = Usuario(
            nombres="Carlos",
            apellidos="Rodriguez",
            correo="carlos@colegio.edu.co",
            password_hash="123456",
            rol="Docente"
        )

        db.add(usuario_docente)
        db.flush()

        docente = Docente(
            id_docente=usuario_docente.id_usuario,
            estado="Activo"
        )

        db.add(docente)

        # ===========================
        # ESTUDIANTES
        # ===========================

        estudiantes = []

        datos = [
            ("Samuel", "Herrera", "samuel@calegio.edu.co"),
            ("Laura", "Gomez", "laura@calegio.edu.co"),
            ("Juan", "Perez", "juan@calegio.edu.co"),
            ("Sofia", "Ramirez", "sofia@calegio.edu.co"),
            ("Andres", "Lopez", "andres@calegio.edu.co"),
        ]

        for nombres, apellidos, correo in datos:

            usuario = Usuario(
                nombres=nombres,
                apellidos=apellidos,
                correo=correo,
                password_hash="123456",
                rol="Estudiante"
            )

            db.add(usuario)
            db.flush()

            estudiante = Estudiante(
                id_estudiante=usuario.id_usuario,
                estado="Activo"
            )

            db.add(estudiante)
            estudiantes.append(estudiante)

        # ===========================
        # GRADO
        # ===========================

        grado = Grado(
            nombre="10-01"
        )

        db.add(grado)
        db.flush()

        # ===========================
        # MATERIA
        # ===========================

        materia = Materia(
            nombre="Matemáticas"
        )

        db.add(materia)
        db.flush()

        # ===========================
        # PERIODO
        # ===========================

        periodo = PeriodoAcademico(
            nombre="Primer Periodo",
            anio=2026,
            estado="Abierto"
        )

        db.add(periodo)
        db.flush()

        # ===========================
        # CURSO
        # ===========================

        curso = Curso(
            id_docente=docente.id_docente,
            id_grado=grado.id_grado,
            id_materia=materia.id_materia,
            id_periodo=periodo.id_periodo
        )

        db.add(curso)
        db.flush()

        # ===========================
        # MATRICULAS
        # ===========================

        for estudiante in estudiantes:

            matricula = Matricula(
                id_estudiante=estudiante.id_estudiante,
                id_grado=grado.id_grado,
                anio=2026
            )

            db.add(matricula)

        db.commit()

        print("Datos de prueba insertados correctamente.")
        print(f"id_curso = {curso.id_curso}")

    except Exception as e:
        db.rollback()
        print(e)

    finally:
        db.close()

poblar_asistencias()