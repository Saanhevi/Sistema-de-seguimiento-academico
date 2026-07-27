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
from app.repositories.curso import CursoRepository
from app.services.curso import CursoService
from app.services.calificacion import CalificacionService

DOCENTES = [
    ("docente1_notas@colegio.edu.co", "Ana", "Martínez"),
    ("docente2_notas@colegio.edu.co", "Carlos", "Sánchez"),
]

COURSES = [
    {
        "docente_correo": "docente1_notas@colegio.edu.co",
        "grado": "6A-Notas",
        "materia": "Matemáticas-Notas",
        "periodo": {"nombre": "2026-1-Notas", "anio": 2026},
        "estudiantes": [
            ("estudiante1a_notas@colegio.edu.co", "María", "López"),
            ("estudiante1b_notas@colegio.edu.co", "Javier", "Castro"),
            ("estudiante1c_notas@colegio.edu.co", "Natalia", "Pérez"),
        ],
    },
    {
        "docente_correo": "docente1_notas@colegio.edu.co",
        "grado": "6B-Notas",
        "materia": "Ciencias-Notas",
        "periodo": {"nombre": "2026-2-Notas", "anio": 2026},
        "estudiantes": [
            ("estudiante2a_notas@colegio.edu.co", "Diego", "Ramírez"),
            ("estudiante2b_notas@colegio.edu.co", "Laura", "García"),
            ("estudiante2c_notas@colegio.edu.co", "Mateo", "Vargas"),
        ],
    },
    {
        "docente_correo": "docente2_notas@colegio.edu.co",
        "grado": "7A-Notas",
        "materia": "Historia-Notas",
        "periodo": {"nombre": "2026-3-Notas", "anio": 2026},
        "estudiantes": [
            ("estudiante3a_notas@colegio.edu.co", "Valentina", "Díaz"),
            ("estudiante3b_notas@colegio.edu.co", "Samuel", "Ojeda"),
            ("estudiante3c_notas@colegio.edu.co", "Paula", "Morales"),
        ],
    },
    {
        "docente_correo": "docente2_notas@colegio.edu.co",
        "grado": "7B-Notas",
        "materia": "Inglés-Notas",
        "periodo": {"nombre": "2026-4-Notas", "anio": 2026},
        "estudiantes": [
            ("estudiante4a_notas@colegio.edu.co", "Tomás", "Navarro"),
            ("estudiante4b_notas@colegio.edu.co", "Isabella", "Ruiz"),
            ("estudiante4c_notas@colegio.edu.co", "Hugo", "Cortés"),
        ],
    },
]

SECCIONES = [
    ("Quizzes", 20.0, ["Quiz 1", "Quiz 2", "Quiz 3"]),
    ("Tareas", 30.0, ["Tarea 1", "Tarea 2", "Tarea 3"]),
    ("Parciales", 50.0, ["Parcial 1", "Parcial 2", "Parcial 3"]),
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


def obtener_o_crear_docente(session, correo, nombres, apellidos):
    usuario = obtener_o_crear_usuario(session, correo, nombres, apellidos, "Docente")
    docente = session.get(Docente, usuario.id_usuario)
    if docente is None:
        docente = Docente(id_docente=usuario.id_usuario, estado="Activo")
        session.add(docente)
        session.flush()
    return usuario, docente


def obtener_o_crear_estudiante(session, correo, nombres, apellidos):
    usuario = obtener_o_crear_usuario(session, correo, nombres, apellidos, "Estudiante")
    estudiante = session.get(Estudiante, usuario.id_usuario)
    if estudiante is None:
        estudiante = Estudiante(id_estudiante=usuario.id_usuario, estado="Activo")
        session.add(estudiante)
        session.flush()
    return usuario, estudiante


def obtener_o_crear_grado(session, nombre):
    grado = session.query(Grado).filter(Grado.nombre == nombre).first()
    if grado is None:
        grado = Grado(nombre=nombre)
        session.add(grado)
        session.flush()
    return grado


def obtener_o_crear_materia(session, nombre):
    materia = session.query(Materia).filter(Materia.nombre == nombre).first()
    if materia is None:
        materia = Materia(nombre=nombre)
        session.add(materia)
        session.flush()
    return materia


def obtener_o_crear_periodo(session, nombre, anio):
    periodo = session.query(PeriodoAcademico).filter(PeriodoAcademico.nombre == nombre).first()
    if periodo is None:
        periodo = PeriodoAcademico(nombre=nombre, anio=anio, estado="Abierto")
        session.add(periodo)
        session.flush()
    return periodo


def obtener_o_crear_matricula(session, id_estudiante, id_grado, anio):
    from app.models.matricula import Matricula

    matricula = session.query(Matricula).filter(
        Matricula.id_estudiante == id_estudiante,
        Matricula.id_grado == id_grado,
        Matricula.anio == anio,
    ).first()
    return matricula


with SessionLocal() as session:
    curso_repo = CursoRepository(session)
    curso_service = CursoService(session)
    calificacion_service = CalificacionService(session)

    docentes = {}
    for correo, nombres, apellidos in DOCENTES:
        usuario_docente, docente = obtener_o_crear_docente(session, correo, nombres, apellidos)
        docentes[correo] = {
            "usuario": usuario_docente,
            "docente": docente,
            "cursos": [],
        }

    session.commit()

    for curso_def in COURSES:
        docente_info = docentes[curso_def["docente_correo"]]
        docente_usuario = docente_info["usuario"]

        grado = obtener_o_crear_grado(session, curso_def["grado"])
        materia = obtener_o_crear_materia(session, curso_def["materia"])
        periodo = obtener_o_crear_periodo(session, curso_def["periodo"]["nombre"], curso_def["periodo"]["anio"])
        session.commit()

        curso = curso_repo.buscar_por_combinacion(docente_usuario.id_usuario, grado.id_grado, materia.id_materia, periodo.id_periodo)
        if curso is None:
            curso = curso_service.crear_curso(docente_usuario.id_usuario, grado.id_grado, materia.id_materia, periodo.id_periodo)

        estudiantes_info = []
        for correo, nombres, apellidos in curso_def["estudiantes"]:
            _, estudiante = obtener_o_crear_estudiante(session, correo, nombres, apellidos)
            session.commit()
            if not obtener_o_crear_matricula(session, estudiante.id_estudiante, grado.id_grado, periodo.anio):
                try:
                    curso_service.crear_matricula(estudiante.id_estudiante, grado.id_grado, periodo.anio)
                except Exception:
                    session.rollback()
            estudiantes_info.append(estudiante)

        session.commit()

        curso_info = {
            "curso": curso,
            "grado": grado,
            "materia": materia,
            "periodo": periodo,
            "estudiantes": estudiantes_info,
            "secciones": [],
        }

        for seccion_index, (nombre_seccion, porcentaje, actividades) in enumerate(SECCIONES):
            seccion = session.query(SeccionPorcentaje).filter(
                SeccionPorcentaje.id_curso == curso.id_curso,
                SeccionPorcentaje.nombre_seccion == nombre_seccion,
            ).first()
            if seccion is None:
                seccion = calificacion_service.crear_seccion(nombre_seccion, porcentaje, curso.id_curso, docente_usuario)

            seccion_info = {"seccion": seccion, "actividades": []}
            for actividad_index, nombre_actividad in enumerate(actividades):
                actividad = session.query(ActividadEvaluativa).filter(
                    ActividadEvaluativa.id_seccion == seccion.id_seccion,
                    ActividadEvaluativa.nombre == nombre_actividad,
                ).first()
                if actividad is None:
                    actividad = calificacion_service.crear_actividad(nombre_actividad, date(periodo.anio, 7, 20), seccion.id_seccion, docente_usuario)

                notas_iniciales = []
                for index, estudiante in enumerate(estudiantes_info):
                    calificacion = round(5.0 - 0.3 * index - 0.2 * actividad_index - 0.1 * seccion_index, 2)
                    if calificacion < 0:
                        calificacion = 0.0
                    comentarios = [
                        f"Excelente trabajo en {nombre_actividad}",
                        f"Buen desempeño en {nombre_actividad}",
                        f"Necesita mejorar en {nombre_actividad}",
                    ]
                    notas_iniciales.append(
                        {
                            "id_estudiante": estudiante.id_estudiante,
                            "calificacion": calificacion,
                            "comentario": comentarios[index],
                        }
                    )

                calificacion_service.cargar_notas_masivo(actividad.id_actividad, notas_iniciales, docente_usuario)
                seccion_info["actividades"].append(actividad)

            curso_info["secciones"].append(seccion_info)
        docente_info["cursos"].append(curso_info)

    session.commit()

    print("Resumen final:")
    for docente_correo, info in docentes.items():
        usuario_docente = info["usuario"]
        print(f"Docente: {usuario_docente.correo} ({usuario_docente.nombres} {usuario_docente.apellidos})")
        for curso_info in info["cursos"]:
            curso = curso_info["curso"]
            grado = curso_info["grado"]
            materia = curso_info["materia"]
            periodo = curso_info["periodo"]
            print(f"  Curso {curso.id_curso}: grado={grado.nombre}, materia={materia.nombre}, periodo={periodo.nombre}")
            print("    Estudiantes:")
            for estudiante in curso_info["estudiantes"]:
                usuario_est = session.get(Usuario, estudiante.id_estudiante)
                print(f"      {usuario_est.correo} - {usuario_est.nombres} {usuario_est.apellidos}")
            print("    Secciones y actividades:")
            for seccion_info in curso_info["secciones"]:
                seccion = seccion_info["seccion"]
                print(f"      Sección: {seccion.nombre_seccion} ({seccion.porcentaje}%)")
                for actividad in seccion_info["actividades"]:
                    print(f"        Actividad: {actividad.nombre} (id {actividad.id_actividad})")
    print("Datos finales cargados correctamente.")
