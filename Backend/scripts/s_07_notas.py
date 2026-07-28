import random

from app.core.database import SessionLocal

from app.models.actividad_evaluativa import ActividadEvaluativa
from app.models.seccion_porcentaje import SeccionPorcentaje
from app.models.curso import Curso
from app.models.matricula import Matricula
from app.models.nota import Nota

comentarios = [
    "Excelente trabajo.",
    "Buen desempeño.",
    "Debe mejorar.",
    "Participó activamente.",
    "Entrega incompleta.",
    "Muy buen trabajo.",
    "Presentó algunas dificultades.",
    "Cumplió con los objetivos.",
    "Necesita reforzar los temas.",
    None
]

with SessionLocal() as session:

    actividades = (
        session.query(ActividadEvaluativa)
        .order_by(ActividadEvaluativa.id_actividad)
        .all()
    )

    print("=== Creando notas ===")

    total = 0

    for actividad in actividades:

        seccion = (
            session.query(SeccionPorcentaje)
            .filter_by(id_seccion=actividad.id_seccion)
            .first()
        )

        curso = (
            session.query(Curso)
            .filter_by(id_curso=seccion.id_curso)
            .first()
        )

        matriculas = (
            session.query(Matricula)
            .filter_by(id_grado=curso.id_grado)
            .all()
        )

        for matricula in matriculas:

            probabilidad = random.random()

            if probabilidad < 0.10:
                nota = round(random.uniform(1.0, 2.9), 1)

            elif probabilidad < 0.40:
                nota = round(random.uniform(3.0, 3.9), 1)

            else:
                nota = round(random.uniform(4.0, 5.0), 1)

            registro = Nota(
                id_actividad=actividad.id_actividad,
                id_estudiante=matricula.id_estudiante,
                calificacion=nota,
                comentario=random.choice(comentarios)
            )

            session.add(registro)
            total += 1

    session.commit()

print(f"{total} notas creadas correctamente.")