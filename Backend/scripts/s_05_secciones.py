from app.models.curso import Curso
from app.models.seccion_porcentaje import SeccionPorcentaje

from app.core.database import SessionLocal

secciones = [
    {
        "nombre": "Tareas",
        "porcentaje": 20.00
    },
    {
        "nombre": "Quices",
        "porcentaje": 20.00
    },
    {
        "nombre": "Parcial",
        "porcentaje": 30.00
    },
    {
        "nombre": "Proyecto Final",
        "porcentaje": 30.00
    }
]

with SessionLocal() as session:

    cursos = (
        session.query(Curso)
        .order_by(Curso.id_curso)
        .all()
    )

    print("=== Creando secciones ===")

    for curso in cursos:

        for datos in secciones:

            seccion = SeccionPorcentaje(
                nombre_seccion=datos["nombre"],
                porcentaje=datos["porcentaje"],
                id_curso=curso.id_curso
            )

            session.add(seccion)

        print(f"Curso {curso.id_curso}: 4 secciones creadas")

    session.commit()

print("Secciones creadas correctamente.")