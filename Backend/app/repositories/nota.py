from sqlalchemy import select, func
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
    def obtener_promedio_estudiante_materia(self, id_estudiante: int, id_materia: int, id_periodo: int) -> Optional[float]:
        from app.models.actividad_evaluativa import ActividadEvaluativa
        from app.models.seccion_porcentaje import SeccionPorcentaje
        from app.models.curso import Curso
        from collections import defaultdict

        # 1. Consulta: Traer la calificación, el ID de la sección y su porcentaje
        # CORRECCIÓN H10: Agregamos filtro explícito de id_periodo
        resultados = (
            self.session.query(
                Nota.calificacion,
                SeccionPorcentaje.id_seccion,
                SeccionPorcentaje.porcentaje
            )
            .join(ActividadEvaluativa, Nota.id_actividad == ActividadEvaluativa.id_actividad)
            .join(SeccionPorcentaje, ActividadEvaluativa.id_seccion == SeccionPorcentaje.id_seccion)
            .join(Curso, SeccionPorcentaje.id_curso == Curso.id_curso)
            .filter(
                Nota.id_estudiante == id_estudiante,
                Curso.id_materia == id_materia,
                Curso.id_periodo == id_periodo
            )
            .all()
        )

        if not resultados:
            return None

        # 2. CORRECCIÓN H10: Lógica matemática para promedio ponderado
        # Estructura para agrupar: {id_seccion: {'notas': [], 'porcentaje': float}}
        datos_secciones = defaultdict(lambda: {'notas': [], 'porcentaje': 0.0})

        for calif, id_sec, porc in resultados:
            if calif is not None:
                datos_secciones[id_sec]['notas'].append(float(calif))
                datos_secciones[id_sec]['porcentaje'] = float(porc)

        suma_ponderada = 0.0
        suma_porcentajes = 0.0

        # 3. Calcular el promedio ponderado exacto
        for id_sec, info in datos_secciones.items():
            if info['notas']:
                # Primero se promedian las actividades dentro de un mismo corte/sección
                nota_seccion = sum(info['notas']) / len(info['notas'])
                porcentaje = info['porcentaje']
                
                suma_ponderada += nota_seccion * porcentaje
                suma_porcentajes += porcentaje

        # 4. Fórmula Final
        if suma_porcentajes > 0:
            promedio_final = suma_ponderada / suma_porcentajes
            return round(promedio_final, 2)
        
        return None
    def obtener_promedio_grupal_materia(self, id_materia: int, id_docente: int | None, id_periodo: int) -> Optional[float]:
        from app.models.actividad_evaluativa import ActividadEvaluativa
        from app.models.seccion_porcentaje import SeccionPorcentaje
        from app.models.curso import Curso
        from collections import defaultdict

        # 1. Consulta base: traemos también id_estudiante, id_seccion y porcentaje
        # CORRECCIÓN H10: Agregamos filtro explícito de id_periodo
        query = (
            self.session.query(
                Nota.id_estudiante,
                Nota.calificacion,
                SeccionPorcentaje.id_seccion,
                SeccionPorcentaje.porcentaje
            )
            .join(ActividadEvaluativa, Nota.id_actividad == ActividadEvaluativa.id_actividad)
            .join(SeccionPorcentaje, ActividadEvaluativa.id_seccion == SeccionPorcentaje.id_seccion)
            .join(Curso, SeccionPorcentaje.id_curso == Curso.id_curso)
            .filter(
                Curso.id_materia == id_materia,
                Curso.id_periodo == id_periodo
            )
        )

        # 2. CORRECCIÓN H7: Filtro opcional de docente (ignorado si es Administrador)
        if id_docente is not None:
            query = query.filter(Curso.id_docente == id_docente)

        resultados = query.all()

        if not resultados:
            return None

        # 3. CORRECCIÓN H10: Lógica matemática para promedio ponderado por estudiante
        # Estructura: {id_estudiante: {id_seccion: {'notas': [], 'porcentaje': float}}}
        datos_estudiantes = defaultdict(lambda: defaultdict(lambda: {'notas': [], 'porcentaje': 0.0}))

        for id_est, calif, id_sec, porc in resultados:
            if calif is not None:
                datos_estudiantes[id_est][id_sec]['notas'].append(float(calif))
                datos_estudiantes[id_est][id_sec]['porcentaje'] = float(porc)

        promedios_estudiantes = []

        # 4. Calcular el promedio ponderado exacto de cada estudiante
        for id_est, secciones in datos_estudiantes.items():
            suma_ponderada = 0.0
            suma_porcentajes = 0.0
            
            for id_sec, info in secciones.items():
                if info['notas']:
                    # Primero se promedian las actividades dentro de un mismo corte/sección
                    nota_seccion = sum(info['notas']) / len(info['notas'])
                    porcentaje = info['porcentaje']
                    
                    suma_ponderada += nota_seccion * porcentaje
                    suma_porcentajes += porcentaje
            
            # Promedio definitivo del estudiante 
            # Fórmula: Σ(nota_seccion * porcentaje) / Σ(porcentaje)
            if suma_porcentajes > 0:
                promedio_estudiante = suma_ponderada / suma_porcentajes
                promedios_estudiantes.append(promedio_estudiante)

        # 5. Calcular el promedio grupal
        if not promedios_estudiantes:
            return None

        # El promedio grupal es la media de los promedios individuales
        promedio_grupal = sum(promedios_estudiantes) / len(promedios_estudiantes)
        return round(promedio_grupal, 2)

    def borrar_por_actividad(self, id_actividad: int):
        # Borra todas las notas asociadas a una actividad
        notas = self.listar(id_actividad=id_actividad)
        for nota in notas:
            self.session.delete(nota)
        self.session.flush()