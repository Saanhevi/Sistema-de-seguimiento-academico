from datetime import date

from app.core.database import SessionLocal
from app.core.security import controlador_contrasena
from app.models.usuario import Usuario
from app.models.docente import Docente
from app.models.estudiante import Estudiante
from app.models.grado import Grado
from app.models.materia import Materia
from app.models.periodo_academico import PeriodoAcademico
from app.models.seccion_porcentaje import SeccionPorcentaje
from app.models.actividad_evaluativa import ActividadEvaluativa
from app.models.dia_asistible import DiaAsistible
from app.models.historial_asistencia import HistorialAsistencia
from app.models.alerta import Alerta

from app.services.calificacion import CalificacionService
from app.services.asistencia import AsistenciaService
from app.repositories.alerta import AlertaRepository


def crear_usuario(session, correo, nombres, apellidos, rol):
    usuario = Usuario(
        nombres=nombres,
        apellidos=apellidos,
        correo=correo,
        password_hash=controlador_contrasena.hashear("clave123"),
        rol=rol,
    )
    session.add(usuario)
    session.flush()
    return usuario


def test_alertas_por_promedio():
    session = SessionLocal()
    try:
        # Crear docente, estudiante y entidades mínimas
        docente_u = crear_usuario(session, "doc@test.com", "Doc", "T", "Docente")
        docente = Docente(id_docente=docente_u.id_usuario, estado="Activo")
        session.add(docente)

        estudiante_u = crear_usuario(session, "est@test.com", "Est", "T", "Estudiante")
        estudiante = Estudiante(id_estudiante=estudiante_u.id_usuario, estado="Activo")
        session.add(estudiante)

        grado = Grado(nombre="1A")
        session.add(grado)
        materia = Materia(nombre="Mat")
        session.add(materia)
        periodo = PeriodoAcademico(nombre="2026-1", anio=2026, estado="Abierto")
        session.add(periodo)
        session.flush()

        curso = session.execute(
            "SELECT * FROM curso WHERE 1=0"
        )  # no-op to keep style; create curso via ORM below
        from app.models.curso import Curso
        curso = Curso(id_docente=docente.id_docente, id_grado=grado.id_grado, id_materia=materia.id_materia, id_periodo=periodo.id_periodo)
        session.add(curso)
        session.flush()

        seccion = SeccionPorcentaje(nombre_seccion="Quizzes", porcentaje=100.0, id_curso=curso.id_curso)
        session.add(seccion)
        session.flush()

        actividad = ActividadEvaluativa(nombre="A1", fecha=date(2026,7,20), id_seccion=seccion.id_seccion)
        session.add(actividad)
        session.flush()

        session.commit()

        calif_service = CalificacionService(session)

        # Cargar una nota que deje promedio 3.5 -> debe crear alerta 'Medio'
        notas = [{"id_estudiante": estudiante.id_estudiante, "calificacion": 3.5, "comentario": ""}]
        calif_service.cargar_notas_masivo(actividad.id_actividad, notas, usuario=docente_u)

        alerta = session.query(Alerta).filter(Alerta.id_estudiante == estudiante.id_estudiante).order_by(Alerta.id_alerta.desc()).first()
        assert alerta is not None
        assert alerta.nivel == "Medio"

        # Cargar otra nota (misma actividad para facilitar) que baje promedio a 2.5 -> alerta 'Alto'
        notas2 = [{"id_estudiante": estudiante.id_estudiante, "calificacion": 2.5, "comentario": ""}]
        calif_service.cargar_notas_masivo(actividad.id_actividad, notas2, usuario=docente_u)

        alerta2 = session.query(Alerta).filter(Alerta.id_estudiante == estudiante.id_estudiante).order_by(Alerta.id_alerta.desc()).first()
        assert alerta2 is not None
        assert alerta2.nivel == "Alto"

    finally:
        session.rollback()
        session.close()


def test_alertas_solo_del_periodo_abierto():
    session = SessionLocal()
    try:
        docente_u = crear_usuario(session, "doc_unique@test.com", "Doc2", "T", "Docente")
        docente = Docente(id_docente=docente_u.id_usuario, estado="Activo")
        session.add(docente)

        estudiante_u = crear_usuario(session, "est_unique@test.com", "Est3", "T", "Estudiante")
        estudiante = Estudiante(id_estudiante=estudiante_u.id_usuario, estado="Activo")
        session.add(estudiante)

        grado = Grado(nombre="2A")
        session.add(grado)
        materia = Materia(nombre="Biología")
        session.add(materia)

        periodo_abierto = PeriodoAcademico(nombre="2026-2", anio=2026, estado="Abierto")
        periodo_cerrado = PeriodoAcademico(nombre="2025-2", anio=2025, estado="Cerrado")
        session.add_all([periodo_abierto, periodo_cerrado])
        session.flush()

        from app.models.curso import Curso
        curso_abierto = Curso(id_docente=docente.id_docente, id_grado=grado.id_grado, id_materia=materia.id_materia, id_periodo=periodo_abierto.id_periodo)
        curso_cerrado = Curso(id_docente=docente.id_docente, id_grado=grado.id_grado, id_materia=materia.id_materia, id_periodo=periodo_cerrado.id_periodo)
        session.add_all([curso_abierto, curso_cerrado])
        session.flush()

        alerta_abierta = Alerta(
            id_estudiante=estudiante.id_estudiante,
            id_curso=curso_abierto.id_curso,
            tipo="Riesgo Académico",
            mensaje="Alerta abierta",
            nivel="Medio",
            fecha=date(2026, 7, 1),
            estado="Pendiente",
        )
        alerta_cerrada = Alerta(
            id_estudiante=estudiante.id_estudiante,
            id_curso=curso_cerrado.id_curso,
            tipo="Riesgo Académico",
            mensaje="Alerta cerrada",
            nivel="Alto",
            fecha=date(2026, 6, 1),
            estado="Pendiente",
        )
        session.add_all([alerta_abierta, alerta_cerrada])
        session.commit()

        repo = AlertaRepository(session)
        alertas = repo.listar_por_estudiante(estudiante.id_estudiante)

        assert [alerta.id_alerta for alerta in alertas] == [alerta_abierta.id_alerta]
    finally:
        session.rollback()
        session.close()


def test_alertas_por_inasistencias():
    session = SessionLocal()
    try:
        estudiante_u = crear_usuario(session, "est2@test.com", "Est2", "T", "Estudiante")
        estudiante = Estudiante(id_estudiante=estudiante_u.id_usuario, estado="Activo")
        session.add(estudiante)

        # Crear dia asistible y 2 ausencias previas
        from app.models.dia_asistible import DiaAsistible
        dia1 = DiaAsistible(id_curso=1, fecha=date(2026,7,1))
        dia2 = DiaAsistible(id_curso=1, fecha=date(2026,7,2))
        dia3 = DiaAsistible(id_curso=1, fecha=date(2026,7,3))
        session.add_all([dia1, dia2, dia3])
        session.flush()

        h1 = HistorialAsistencia(id_dia=dia1.id_dia, id_estudiante=estudiante.id_estudiante, estado="Ausente")
        h2 = HistorialAsistencia(id_dia=dia2.id_dia, id_estudiante=estudiante.id_estudiante, estado="Ausente")
        session.add_all([h1, h2])
        session.flush()
        session.commit()

        asistencia_service = AsistenciaService(session)

        # Ahora actualizamos el tercer día a Ausente mediante el servicio para disparar la alerta
        from app.schemas.asistencia import AsistenciaRequest
        req = [AsistenciaRequest(id_estudiante=estudiante.id_estudiante, estado="Ausente")]
        asistencia_service.actualizar_asistencia(dia3.id_dia, req)

        alerta = session.query(Alerta).filter(Alerta.id_estudiante == estudiante.id_estudiante).order_by(Alerta.id_alerta.desc()).first()
        assert alerta is not None
        assert alerta.nivel == "Alto"

    finally:
        session.rollback()
        session.close()
