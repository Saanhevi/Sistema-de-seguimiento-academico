from datetime import date, timedelta

from app.models.curso import Curso
from app.models.dia_asistible import DiaAsistible

from app.core.database import SessionLocal

DIAS_POR_CURSO = 10
FECHA_INICIAL = date(2026, 2, 2)

with SessionLocal() as session:

    cursos = (
        session.query(Curso)
        .order_by(Curso.id_curso)
        .all()
    )

    print("=== Creando días asistibles ===")

    total = 0

    for curso in cursos:

        for i in range(DIAS_POR_CURSO):

            dia = DiaAsistible(
                id_curso=curso.id_curso,
                fecha=FECHA_INICIAL + timedelta(days=i * 7)
            )

            session.add(dia)
            total += 1

        print(
            f"Curso {curso.id_curso}: "
            f"{DIAS_POR_CURSO} días creados."
        )

    session.commit()

print(f"{total} días asistibles creados correctamente.")