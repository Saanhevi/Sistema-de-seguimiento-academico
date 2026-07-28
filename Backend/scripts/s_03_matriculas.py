from app.models.estudiante import Estudiante
from app.models.grado import Grado
from app.models.matricula import Matricula

from app.core.database import SessionLocal

ANIO = 2026

with SessionLocal() as session:

    estudiantes = (
        session.query(Estudiante)
        .order_by(Estudiante.id_estudiante)
        .all()
    )

    grados = (
        session.query(Grado)
        .order_by(Grado.id_grado)
        .all()
    )

    if len(grados) != 5:
        raise Exception("Debe haber exactamente 5 grados creados.")

    estudiantes_por_grado = len(estudiantes) // len(grados)

    indice = 0

    print("=== Creando matrículas ===")

    for grado in grados:

        for _ in range(estudiantes_por_grado):

            estudiante = estudiantes[indice]

            matricula = Matricula(
                id_estudiante=estudiante.id_estudiante,
                id_grado=grado.id_grado,
                anio=ANIO
            )

            session.add(matricula)

            print(
                f"Estudiante {estudiante.id_estudiante} -> "
                f"{grado.nombre}"
            )

            indice += 1

    session.commit()

print("Matrículas creadas correctamente.")