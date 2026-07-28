from collections import defaultdict
from sqlalchemy import delete, select, func
from app.models.nota import Nota
from app.models.actividad_evaluativa import ActividadEvaluativa
from app.models.seccion_porcentaje import SeccionPorcentaje
from app.models.curso import Curso
from typing import Optional

class NotaRepository:

    def __init__(self, session):
        self.session = session

    def agregar(self, nota: Nota):
        # No hace commit: el llamador controla el límite de la transacción
        # (necesario para que carga-masiva confirme todo el lote en un solo commit)
        self.session.add(nota)
        self.session.flush()
        return nota

    def listar(self, id_actividad=None, id_estudiante=None, id_docente=None):
        query = select(Nota)

        if id_actividad is not None:
            query = query.where(Nota.id_actividad == id_actividad)
        if id_estudiante is not None:
            query = query.where(Nota.id_estudiante == id_estudiante)
        if id_docente is not None:
            # RN-03: solo las notas de actividades que cuelgan de un curso del docente.
            query = (
                query.join(ActividadEvaluativa, ActividadEvaluativa.id_actividad == Nota.id_actividad)
                .join(SeccionPorcentaje, SeccionPorcentaje.id_seccion == ActividadEvaluativa.id_seccion)
                .join(Curso, Curso.id_curso == SeccionPorcentaje.id_curso)
                .where(Curso.id_docente == id_docente)
            )

        return self.session.execute(query).scalars().all()

    def buscar_por_id(self, id_nota):
        query = select(Nota).where(Nota.id_nota == id_nota)
        return self.session.execute(query).scalars().first()

    def buscar_por_actividad_y_estudiante(self, id_actividad, id_estudiante):
        query = select(Nota).where(
            Nota.id_actividad == id_actividad,
            Nota.id_estudiante == id_estudiante,
        )
        return self.session.execute(query).scalars().first() 
    def _consultar_filas_materia(
        self,
        id_materia: int,
        id_periodo: int,
        id_estudiante: int | None = None,
        id_docente: int | None = None,
    ):
        """
        Filas (id_estudiante, calificacion, id_seccion, porcentaje) de una materia.

        El filtro por id_periodo es lo que evita mezclar periodos y años distintos en
        el mismo promedio (H10). El de id_docente aplica RN-03 cuando quien consulta
        es un Docente; para un Administrador llega en None y no se acota.
        """
        query = (
            self.session.query(
                Nota.id_estudiante,
                Nota.calificacion,
                SeccionPorcentaje.id_seccion,
                SeccionPorcentaje.porcentaje,
            )
            .join(ActividadEvaluativa, Nota.id_actividad == ActividadEvaluativa.id_actividad)
            .join(SeccionPorcentaje, ActividadEvaluativa.id_seccion == SeccionPorcentaje.id_seccion)
            .join(Curso, SeccionPorcentaje.id_curso == Curso.id_curso)
            .filter(
                Curso.id_materia == id_materia,
                Curso.id_periodo == id_periodo,
            )
        )

        if id_estudiante is not None:
            query = query.filter(Nota.id_estudiante == id_estudiante)
        if id_docente is not None:
            query = query.filter(Curso.id_docente == id_docente)

        return query.all()

    @staticmethod
    def _promedio_ponderado(filas) -> Optional[float]:
        """
        Σ(nota_seccion * porcentaje) / Σ(porcentaje) sobre tuplas
        (calificacion, id_seccion, porcentaje).

        Las actividades de una misma sección se promedian entre sí antes de ponderar,
        para que tener 10 talleres no pese más que tener 2 (H10). Devuelve None si no
        hay nada que promediar: 0.0 es una calificación válida y no puede usarse como
        marcador de «sin datos» (H13).

        Ojo: el promedio se normaliza sobre las secciones que ya tienen nota, así que
        un corte incompleto se reporta como si fuera el definitivo de la materia.
        """
        secciones = defaultdict(lambda: {"notas": [], "porcentaje": 0.0})

        for calificacion, id_seccion, porcentaje in filas:
            secciones[id_seccion]["notas"].append(float(calificacion))
            secciones[id_seccion]["porcentaje"] = float(porcentaje)

        suma_ponderada = 0.0
        suma_porcentajes = 0.0

        for info in secciones.values():
            nota_seccion = sum(info["notas"]) / len(info["notas"])
            suma_ponderada += nota_seccion * info["porcentaje"]
            suma_porcentajes += info["porcentaje"]

        if suma_porcentajes <= 0:
            return None

        return round(suma_ponderada / suma_porcentajes, 2)

    def obtener_promedio_estudiante_materia(
        self,
        id_estudiante: int,
        id_materia: int,
        id_periodo: int,
        id_docente: int | None = None,
    ) -> Optional[float]:
        filas = self._consultar_filas_materia(
            id_materia, id_periodo, id_estudiante=id_estudiante, id_docente=id_docente
        )
        return self._promedio_ponderado([(calif, id_sec, porc) for _, calif, id_sec, porc in filas])

    def obtener_promedios_por_estudiante_materia(
        self, id_materia: int, id_docente: int | None, id_periodo: int
    ) -> dict[int, float]:
        """
        Promedio ponderado de cada estudiante de la materia (HU8).

        Es también la fuente del promedio grupal, para que el valor que el docente ve
        por estudiante y el agregado del curso salgan del mismo cálculo y no puedan
        divergir.
        """
        filas = self._consultar_filas_materia(id_materia, id_periodo, id_docente=id_docente)

        por_estudiante = defaultdict(list)
        for id_estudiante, calificacion, id_seccion, porcentaje in filas:
            por_estudiante[id_estudiante].append((calificacion, id_seccion, porcentaje))

        promedios = {}
        for id_estudiante, filas_estudiante in por_estudiante.items():
            promedio = self._promedio_ponderado(filas_estudiante)
            if promedio is not None:
                promedios[id_estudiante] = promedio

        return promedios

    def obtener_promedio_grupal_materia(
        self, id_materia: int, id_docente: int | None, id_periodo: int
    ) -> Optional[float]:
        """
        Media de los promedios individuales, no de las notas sueltas: quien tiene 10
        actividades no debe pesar más que quien tiene 2 (H10).

        Promedia los valores ya redondeados que se le muestran al docente, para que
        sumar la columna de promedios y dividir dé exactamente el promedio grupal de
        la pantalla.
        """
        promedios = self.obtener_promedios_por_estudiante_materia(id_materia, id_docente, id_periodo)

        if not promedios:
            return None

        return round(sum(promedios.values()) / len(promedios), 2)

    def borrar_por_actividad(self, id_actividad: int):
        # Borra todas las notas asociadas a una actividad con una sola sentencia.
        self.session.execute(
            delete(Nota).where(Nota.id_actividad == id_actividad)
        )
        self.session.flush()

    def borrar_por_actividades(self, id_actividades: list[int]):
        if not id_actividades:
            return
        self.session.execute(
            delete(Nota).where(Nota.id_actividad.in_(id_actividades))
        )
        self.session.flush()