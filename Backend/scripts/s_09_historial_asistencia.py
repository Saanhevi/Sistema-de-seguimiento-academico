import random

from app.core.database import SessionLocal

from app.models.dia_asistible import DiaAsistible
from app.models.curso import Curso
from app.models.matricula import Matricula
from app.models.historial_asistencia import HistorialAsistencia

with SessionLocal() as session:

    dias = (
        session.query(DiaAsistible)
        .order_by(DiaAsistible.id_dia)
        .all()
    )

    print("=== Creando historial de asistencias ===")

    total = 0

    for dia in dias:

        curso = (
            session.query(Curso)
            .filter_by(id_curso=dia.id_curso)
            .first()
        )

        matriculas = (
            session.query(Matricula)
            .filter_by(id_grado=curso.id_grado)
            .all()
        )

        for matricula in matriculas:

            probabilidad = random.random()

            if probabilidad < 0.85:
                estado = "Presente"

            elif probabilidad < 0.93:
                estado = "Retardo"

            elif probabilidad < 0.98:
                estado = "Ausente"

            else:
                estado = "Excusa"

            asistencia = HistorialAsistencia(
                id_dia=dia.id_dia,
                id_estudiante=matricula.id_estudiante,
                estado=estado
            )

            session.add(asistencia)
            total += 1

    session.commit()

print(f"{total} registros de asistencia creados correctamente.")