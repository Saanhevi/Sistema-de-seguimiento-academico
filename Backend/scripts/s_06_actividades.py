from datetime import date, timedelta

from app.models.seccion_porcentaje import SeccionPorcentaje
from app.models.actividad_evaluativa import ActividadEvaluativa

from app.core.database import SessionLocal

with SessionLocal() as session:

    secciones = (
        session.query(SeccionPorcentaje)
        .order_by(SeccionPorcentaje.id_seccion)
        .all()
    )

    print("=== Creando actividades evaluativas ===")

    fecha_base = date(2026, 2, 2)

    for seccion in secciones:

        if seccion.nombre_seccion == "Tareas":

            nombres = [
                "Tarea 1",
                "Tarea 2",
                "Tarea 3"
            ]

        elif seccion.nombre_seccion == "Quices":

            nombres = [
                "Quiz 1",
                "Quiz 2",
                "Quiz 3"
            ]

        elif seccion.nombre_seccion == "Parcial":

            nombres = [
                "Parcial"
            ]

        elif seccion.nombre_seccion == "Proyecto Final":

            nombres = [
                "Proyecto Final"
            ]

        else:
            continue

        for i, nombre in enumerate(nombres):

            actividad = ActividadEvaluativa(
                nombre=nombre,
                fecha=fecha_base + timedelta(days=i * 14),
                id_seccion=seccion.id_seccion
            )

            session.add(actividad)

        print(
            f"Sección {seccion.id_seccion} ({seccion.nombre_seccion}) -> "
            f"{len(nombres)} actividades"
        )

    session.commit()

print("Actividades evaluativas creadas correctamente.")