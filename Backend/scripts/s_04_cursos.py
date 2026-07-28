from app.models.docente import Docente
from app.models.grado import Grado
from app.models.materia import Materia
from app.models.periodo_academico import PeriodoAcademico
from app.models.curso import Curso

from app.core.database import SessionLocal

with SessionLocal() as session:

    docentes = (
        session.query(Docente)
        .order_by(Docente.id_docente)
        .all()
    )

    grados = (
        session.query(Grado)
        .order_by(Grado.id_grado)
        .all()
    )

    materias = (
        session.query(Materia)
        .order_by(Materia.id_materia)
        .all()
    )

    periodo = (
        session.query(PeriodoAcademico)
        .filter_by(estado="Abierto")
        .first()
    )

    if periodo is None:
        raise Exception("No existe un período académico abierto.")

    indice_docente = 0

    print("=== Creando cursos ===")

    for grado in grados:

        for materia in materias:

            docente = docentes[indice_docente]

            curso = Curso(
                id_docente=docente.id_docente,
                id_grado=grado.id_grado,
                id_materia=materia.id_materia,
                id_periodo=periodo.id_periodo
            )

            session.add(curso)

            print(
                f"{grado.nombre:<4}"
                f" | {materia.nombre:<20}"
                f" | Docente {docente.id_docente}"
            )

            indice_docente += 1

            if indice_docente == len(docentes):
                indice_docente = 0

    session.commit()

print("Cursos creados correctamente.")