from datetime import date

from app.core.database import SessionLocal
from app.core.security import controlador_contrasena
from app.models.usuario import Usuario
from app.models.docente import Docente
from app.models.estudiante import Estudiante
from app.models.grado import Grado
from app.models.materia import Materia
from app.models.periodo_academico import PeriodoAcademico
from app.repositories.curso import CursoRepository
from app.services.curso import CursoService
from app.services.calificacion import CalificacionService

CORREO_DOCENTE = "docente_notas@colegio.edu.co"
CORREOS_ESTUDIANTES = [
    ("estudiante1_notas@colegio.edu.co", "Camila", "Ruiz"),
    ("estudiante2_notas@colegio.edu.co", "Andrés", "Gómez"),
    ("estudiante3_notas@colegio.edu.co", "Julián", "Torres"),
]


def obtener_o_crear_usuario(session, correo, nombres, apellidos, rol):
    usuario = session.query(Usuario).filter(Usuario.correo == correo).first()
    if usuario is None:
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


with SessionLocal() as session:
    # 1. Docente y estudiantes de prueba (se reutilizan si ya existen, igual que seed_datos_curso.py)
    docente_usuario = obtener_o_crear_usuario(session, CORREO_DOCENTE, "Laura", "Restrepo", "Docente")
    docente = session.get(Docente, docente_usuario.id_usuario)
    if docente is None:
        docente = Docente(id_docente=docente_usuario.id_usuario, estado="Activo")
        session.add(docente)
        session.flush()

    ids_estudiantes = []
    for correo, nombres, apellidos in CORREOS_ESTUDIANTES:
        usuario_est = obtener_o_crear_usuario(session, correo, nombres, apellidos, "Estudiante")
        estudiante = session.get(Estudiante, usuario_est.id_usuario)
        if estudiante is None:
            estudiante = Estudiante(id_estudiante=usuario_est.id_usuario, estado="Activo")
            session.add(estudiante)
            session.flush()
        ids_estudiantes.append(estudiante.id_estudiante)

    session.commit()

    # 2. Grado, materia y periodo académico Abierto (se reutilizan si ya existen)
    grado = session.query(Grado).filter(Grado.nombre == "6A-Notas").first()
    if grado is None:
        grado = Grado(nombre="6A-Notas")
        session.add(grado)
        session.flush()

    materia = session.query(Materia).filter(Materia.nombre == "Matemáticas-Notas").first()
    if materia is None:
        materia = Materia(nombre="Matemáticas-Notas")
        session.add(materia)
        session.flush()

    periodo = session.query(PeriodoAcademico).filter(PeriodoAcademico.nombre == "2026-1-Notas").first()
    if periodo is None:
        periodo = PeriodoAcademico(nombre="2026-1-Notas", anio=2026, estado="Abierto")
        session.add(periodo)
        session.flush()

    session.commit()

    # 3. Curso real, usando el módulo de Curso ya mergeado (no se inserta a mano por SQL)
    curso_repo = CursoRepository(session)
    curso_service = CursoService(session)

    curso = curso_repo.buscar_por_combinacion(docente.id_docente, grado.id_grado, materia.id_materia, periodo.id_periodo)
    if curso is None:
        curso = curso_service.crear_curso(docente.id_docente, grado.id_grado, materia.id_materia, periodo.id_periodo)

    print(f"Curso de prueba: {curso}")

    # 4. Sección de porcentaje + actividad evaluativa
    calificacion_service = CalificacionService(session)

    seccion = calificacion_service.crear_seccion("Quizzes", 30.0, curso.id_curso)
    print(f"Sección creada: {seccion}")

    actividad = calificacion_service.crear_actividad("Quiz 1 - Fracciones", date(2026, 7, 20), seccion.id_seccion)
    print(f"Actividad creada: {actividad}")

    # 5. Carga masiva de notas para los 3 estudiantes
    notas_iniciales = [
        {"id_estudiante": ids_estudiantes[0], "calificacion": 4.5, "comentario": "Muy bien"},
        {"id_estudiante": ids_estudiantes[1], "calificacion": 3.2, "comentario": None},
        {"id_estudiante": ids_estudiantes[2], "calificacion": 2.8, "comentario": "Repasar fracciones"},
    ]
    notas = calificacion_service.cargar_notas_masivo(actividad.id_actividad, notas_iniciales)
    print(f"Notas cargadas ({len(notas)}):")
    for nota in notas:
        print(f"  {nota}")

    # 6. RN-f: volver a cargar una nota para el mismo estudiante+actividad debe actualizar (upsert), no duplicar
    correccion = [{"id_estudiante": ids_estudiantes[0], "calificacion": 4.8, "comentario": "Corregido tras revisión"}]
    calificacion_service.cargar_notas_masivo(actividad.id_actividad, correccion)

    notas_finales = calificacion_service.listar_notas(id_actividad=actividad.id_actividad)
    print(f"Notas después del upsert ({len(notas_finales)} — debe seguir siendo {len(notas_iniciales)}):")
    for nota in notas_finales:
        print(f"  {nota}")
