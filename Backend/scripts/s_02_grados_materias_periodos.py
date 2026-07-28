from app.models.grado import Grado
from app.models.materia import Materia
from app.models.periodo_academico import PeriodoAcademico

from app.core.database import SessionLocal

grados = [
    "6°",
    "7°",
    "8°",
    "9°",
    "10°"
]

materias = [
    "Matemáticas",
    "Español",
    "Inglés",
    "Biología",
    "Química",
    "Física",
    "Ciencias Sociales",
    "Informática"
]

periodo = {
    "nombre": "2026",
    "anio": 2026,
    "estado": "Abierto"
}

with SessionLocal() as session:

    print("=== Creando grados ===")

    for nombre in grados:
        session.add(
            Grado(
                nombre=nombre
            )
        )

    print("=== Creando materias ===")

    for nombre in materias:
        session.add(
            Materia(
                nombre=nombre
            )
        )

    print("=== Creando período académico ===")

    session.add(
        PeriodoAcademico(
            nombre=periodo["nombre"],
            anio=periodo["anio"],
            estado=periodo["estado"]
        )
    )

    session.commit()

print("Grados, materias y período creados correctamente.")