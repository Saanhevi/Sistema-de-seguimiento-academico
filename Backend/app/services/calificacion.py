from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.actividad_evaluativa import ActividadEvaluativa
from app.models.nota import Nota
from app.models.seccion_porcentaje import SeccionPorcentaje
from app.models.usuario import Usuario
from app.repositories.actividad_evaluativa import ActividadEvaluativaRepository
from app.repositories.curso import CursoRepository
from app.repositories.nota import NotaRepository
from app.repositories.seccion_porcentaje import SeccionPorcentajeRepository


class CalificacionService:

    def __init__(self, session: Session):
        self.session = session
        self.curso_repo = CursoRepository(session)
        self.seccion_repo = SeccionPorcentajeRepository(session)
        self.actividad_repo = ActividadEvaluativaRepository(session)
        self.nota_repo = NotaRepository(session)

    # --- Secciones ---

    def crear_seccion(self, nombre_seccion: str, porcentaje: float, id_curso: int) -> SeccionPorcentaje:
        nombre_limpio = (nombre_seccion or "").strip()
        if not nombre_limpio:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de la sección no puede estar vacío")

        if porcentaje is None or porcentaje <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El porcentaje debe ser mayor a 0")

        # RN-b: id_curso debe existir
        curso = self.curso_repo.buscar_por_id(id_curso)
        if not curso:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")

        # RN-b (opcional): avisar si la suma de porcentajes del curso supera 100%, sin bloquear
        secciones_existentes = self.seccion_repo.listar(id_curso=id_curso)
        suma_actual = sum(float(seccion.porcentaje) for seccion in secciones_existentes) + float(porcentaje)
        if suma_actual > 100:
            print(f"Aviso: las secciones del curso {id_curso} suman {suma_actual}%, superan el 100%")

        seccion = SeccionPorcentaje(nombre_seccion=nombre_limpio, porcentaje=porcentaje, id_curso=id_curso)
        return self.seccion_repo.crear(seccion)

    def listar_secciones(self, id_curso: int | None = None) -> list[SeccionPorcentaje]:
        return self.seccion_repo.listar(id_curso=id_curso)

    # --- Actividades ---

    def crear_actividad(self, nombre: str, fecha: date, id_seccion: int) -> ActividadEvaluativa:
        nombre_limpio = (nombre or "").strip()
        if not nombre_limpio:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de la actividad no puede estar vacío")

        # RN-c: id_seccion debe existir
        seccion = self.seccion_repo.buscar_por_id(id_seccion)
        if not seccion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sección no encontrada")

        actividad = ActividadEvaluativa(nombre=nombre_limpio, fecha=fecha, id_seccion=id_seccion)
        return self.actividad_repo.crear(actividad)

    def listar_actividades(self, id_seccion: int | None = None) -> list[ActividadEvaluativa]:
        return self.actividad_repo.listar(id_seccion=id_seccion)

    # --- Notas ---

    def _validar_calificacion(self, calificacion: float) -> None:
        # RN-a: la calificación debe estar entre 0.00 y 5.00
        if calificacion is None or calificacion < 0 or calificacion > 5:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La calificación debe estar entre 0.00 y 5.00")

    def _validar_estudiante(self, id_estudiante: int) -> None:
        # RN-e: id_estudiante debe existir y tener rol Estudiante
        usuario = self.session.get(Usuario, id_estudiante)
        if usuario is None or usuario.rol != "Estudiante":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El estudiante debe existir y tener rol Estudiante")

    def _validar_periodo_abierto(self, actividad: ActividadEvaluativa) -> None:
        # RN-d: solo se pueden crear/cargar notas si el período del curso está 'Abierto'
        periodo_estado = actividad.seccion.curso.periodo.estado
        if periodo_estado != "Abierto":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El período académico de este curso no está abierto")

    def _guardar_nota(self, id_actividad: int, id_estudiante: int, calificacion: float, comentario: str | None) -> Nota:
        # RN-f: no hay constraint único en BD -> se hace upsert desde el service
        nota_existente = self.nota_repo.buscar_por_actividad_y_estudiante(id_actividad, id_estudiante)
        if nota_existente:
            nota_existente.calificacion = calificacion
            nota_existente.comentario = comentario
            return self.nota_repo.actualizar(nota_existente)

        nota = Nota(
            id_actividad=id_actividad,
            id_estudiante=id_estudiante,
            calificacion=calificacion,
            comentario=comentario,
        )
        return self.nota_repo.crear(nota)

    def crear_nota(self, id_actividad: int, id_estudiante: int, calificacion: float, comentario: str | None = None) -> Nota:
        actividad = self.actividad_repo.buscar_por_id(id_actividad)
        if not actividad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")

        self._validar_calificacion(calificacion)
        self._validar_estudiante(id_estudiante)
        self._validar_periodo_abierto(actividad)

        return self._guardar_nota(id_actividad, id_estudiante, calificacion, comentario)

    def cargar_notas_masivo(self, id_actividad: int, notas: list[dict]) -> list[Nota]:
        actividad = self.actividad_repo.buscar_por_id(id_actividad)
        if not actividad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")

        self._validar_periodo_abierto(actividad)

        resultado = []
        for item in notas:
            id_estudiante = item["id_estudiante"]
            calificacion = item["calificacion"]
            comentario = item.get("comentario")

            self._validar_calificacion(calificacion)
            self._validar_estudiante(id_estudiante)

            resultado.append(self._guardar_nota(id_actividad, id_estudiante, calificacion, comentario))

        return resultado

    def listar_notas(self, id_actividad: int | None = None) -> list[Nota]:
        return self.nota_repo.listar(id_actividad=id_actividad)
