import math
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.actividad_evaluativa import ActividadEvaluativa
from app.models.curso import Curso
from app.models.estudiante import Estudiante
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

    def _validar_pertenencia_curso(self, curso: Curso, usuario: Usuario) -> None:
        # RN-03: un Docente solo puede operar sobre los cursos que dicta él mismo;
        # Administrador no tiene esta restricción.
        if usuario.rol == "Docente" and curso.id_docente != usuario.id_usuario:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso sobre este curso")

    # --- Secciones ---

    def crear_seccion(self, nombre_seccion: str, porcentaje: float, id_curso: int, usuario: Usuario) -> SeccionPorcentaje:
        nombre_limpio = (nombre_seccion or "").strip()
        if not nombre_limpio:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de la sección no puede estar vacío")

        if porcentaje is None or not math.isfinite(porcentaje) or porcentaje <= 0 or porcentaje > 100:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El porcentaje debe ser un número entre 0 y 100")

        # RN-b: id_curso debe existir
        curso = self.curso_repo.buscar_por_id(id_curso)
        if not curso:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curso no encontrado")

        self._validar_pertenencia_curso(curso, usuario)

        # RN-b (opcional): avisar si la suma de porcentajes del curso supera 100%, sin bloquear
        secciones_existentes = self.seccion_repo.listar(id_curso=id_curso)
        suma_actual = sum(float(seccion.porcentaje) for seccion in secciones_existentes) + float(porcentaje)

        seccion = SeccionPorcentaje(nombre_seccion=nombre_limpio, porcentaje=porcentaje, id_curso=id_curso)
        seccion = self.seccion_repo.crear(seccion)

        if suma_actual > 100:
            seccion.advertencia = f"Las secciones de este curso suman {suma_actual:.2f}%, superan el 100%."

        return seccion

    def listar_secciones(self, id_curso: int | None = None) -> list[SeccionPorcentaje]:
        return self.seccion_repo.listar(id_curso=id_curso)

    # --- Actividades ---

    def crear_actividad(self, nombre: str, fecha: date, id_seccion: int, usuario: Usuario) -> ActividadEvaluativa:
        nombre_limpio = (nombre or "").strip()
        if not nombre_limpio:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de la actividad no puede estar vacío")

        # RN-c: id_seccion debe existir
        seccion = self.seccion_repo.buscar_por_id(id_seccion)
        if not seccion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sección no encontrada")

        self._validar_pertenencia_curso(seccion.curso, usuario)

        actividad = ActividadEvaluativa(nombre=nombre_limpio, fecha=fecha, id_seccion=id_seccion)
        return self.actividad_repo.crear(actividad)

    def listar_actividades(self, id_seccion: int | None = None) -> list[ActividadEvaluativa]:
        return self.actividad_repo.listar(id_seccion=id_seccion)

    # --- Notas ---

    def _validar_calificacion(self, calificacion: float) -> None:
        # RN-a: la calificación debe estar entre 0.00 y 5.00 (y no puede ser NaN/Infinity)
        if calificacion is None or not math.isfinite(calificacion) or calificacion < 0 or calificacion > 5:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La calificación debe estar entre 0.00 y 5.00")

    def _validar_estudiante(self, id_estudiante: int) -> None:
        # RN-e: id_estudiante debe existir, tener rol Estudiante y tener fila en Estudiante
        # (Nota.id_estudiante tiene FK contra estudiante, no contra usuario)
        usuario = self.session.get(Usuario, id_estudiante)
        estudiante = self.session.get(Estudiante, id_estudiante)
        if usuario is None or usuario.rol != "Estudiante" or estudiante is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El estudiante debe existir y tener rol Estudiante")

    def _validar_periodo_abierto(self, actividad: ActividadEvaluativa) -> None:
        # RN-d: solo se pueden crear/cargar notas si el período del curso está 'Abierto'
        periodo_estado = actividad.seccion.curso.periodo.estado
        if periodo_estado != "Abierto":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El período académico de este curso no está abierto")

    def _bloquear_nota(self, id_actividad: int, id_estudiante: int) -> None:
        # RN-f: Nota no tiene constraint único en (id_actividad, id_estudiante) en el esquema;
        # se usa un advisory lock transaccional para serializar el upsert entre requests
        # concurrentes sin tener que modificar Database/schemas.sql.
        self.session.execute(
            text("SELECT pg_advisory_xact_lock(:id_actividad, :id_estudiante)"),
            {"id_actividad": id_actividad, "id_estudiante": id_estudiante},
        )

    def _preparar_nota(self, id_actividad: int, id_estudiante: int, calificacion: float, comentario: str | None) -> Nota:
        self._bloquear_nota(id_actividad, id_estudiante)

        nota_existente = self.nota_repo.buscar_por_actividad_y_estudiante(id_actividad, id_estudiante)
        if nota_existente:
            nota_existente.calificacion = calificacion
            nota_existente.comentario = comentario
            self.session.flush()
            return nota_existente

        nota = Nota(
            id_actividad=id_actividad,
            id_estudiante=id_estudiante,
            calificacion=calificacion,
            comentario=comentario,
        )
        return self.nota_repo.agregar(nota)

    def crear_nota(self, id_actividad: int, id_estudiante: int, calificacion: float, comentario: str | None, usuario: Usuario) -> Nota:
        actividad = self.actividad_repo.buscar_por_id(id_actividad)
        if not actividad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")

        self._validar_pertenencia_curso(actividad.seccion.curso, usuario)
        self._validar_calificacion(calificacion)
        self._validar_estudiante(id_estudiante)
        self._validar_periodo_abierto(actividad)

        nota = self._preparar_nota(id_actividad, id_estudiante, calificacion, comentario)
        self.session.commit()
        self.session.refresh(nota)
        return nota

    def cargar_notas_masivo(self, id_actividad: int, notas: list[dict], usuario: Usuario) -> list[Nota]:
        actividad = self.actividad_repo.buscar_por_id(id_actividad)
        if not actividad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actividad no encontrada")

        self._validar_pertenencia_curso(actividad.seccion.curso, usuario)
        self._validar_periodo_abierto(actividad)

        if not notas:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La lista de notas no puede estar vacía")

        # Fase 1: validar todas las filas antes de escribir nada en la BD.
        # Así, si una fila es inválida, el lote completo falla sin dejar commits parciales.
        for item in notas:
            self._validar_calificacion(item["calificacion"])
            self._validar_estudiante(item["id_estudiante"])

        # Fase 2: preparar todas las notas (add/flush, sin commit) y confirmar el lote entero
        # en una sola transacción.
        resultado = [
            self._preparar_nota(id_actividad, item["id_estudiante"], item["calificacion"], item.get("comentario"))
            for item in notas
        ]

        self.session.commit()
        for nota in resultado:
            self.session.refresh(nota)

        return resultado

    def listar_notas(self, id_actividad: int | None, usuario: Usuario) -> list[Nota]:
        # RN-04: un Estudiante solo puede ver sus propias notas
        id_estudiante_filtro = usuario.id_usuario if usuario.rol == "Estudiante" else None
        return self.nota_repo.listar(id_actividad=id_actividad, id_estudiante=id_estudiante_filtro)
