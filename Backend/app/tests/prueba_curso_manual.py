from app.core.database import SessionLocal
from app.models.usuario import Usuario
from app.models.docente import Docente
from app.models.estudiante import Estudiante
from app.services.curso import CursoService
from sqlalchemy import select

with SessionLocal() as session:
    service = CursoService(session)

    docente = session.execute(select(Docente)).scalars().first()
    estudiante = session.execute(select(Estudiante)).scalars().first()

    if docente is None or estudiante is None:
        print("No hay docentes o estudiantes cargados en la base de datos para probar el flujo.")
    else:
        grado = service.crear_grado("10°")
        materia = service.crear_materia("Matemáticas")
        periodo = service.crear_periodo("Primer Periodo", 2026, "Abierto")
        curso = service.crear_curso(docente.id_docente, grado.id_grado, materia.id_materia, periodo.id_periodo)
        matricula = service.crear_matricula(estudiante.id_estudiante, grado.id_grado, 2026)

        print({
            "grado": grado.id_grado,
            "materia": materia.id_materia,
            "periodo": periodo.id_periodo,
            "curso": curso.id_curso,
            "matricula": matricula.id_matricula,
        })
