from app.core.database import SessionLocal
from app.core.security import controlador_contrasena
from app.models.usuario import Usuario
from app.models.docente import Docente
from app.models.estudiante import Estudiante
from app.models.grado import Grado
from app.models.materia import Materia
from app.models.periodo_academico import PeriodoAcademico
from app.models.curso import Curso
from app.models.matricula import Matricula
from datetime import date
from app.models.seccion_porcentaje import SeccionPorcentaje
from app.models.actividad_evaluativa import ActividadEvaluativa
from app.models.dia_asistible import DiaAsistible
from app.models.historial_asistencia import HistorialAsistencia


def crear_o_actualizar_usuario(session, correo, nombres, apellidos, rol, estado=None):
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
    else:
        usuario.nombres = nombres
        usuario.apellidos = apellidos
        usuario.rol = rol
    if rol == "Docente" and estado is not None:
        docente = session.get(Docente, usuario.id_usuario)
        if docente is None:
            docente = Docente(id_docente=usuario.id_usuario, estado=estado)
            session.add(docente)
        else:
            docente.estado = estado
    if rol == "Estudiante" and estado is not None:
        estudiante = session.get(Estudiante, usuario.id_usuario)
        if estudiante is None:
            estudiante = Estudiante(id_estudiante=usuario.id_usuario, estado=estado)
            session.add(estudiante)
        else:
            estudiante.estado = estado
    return usuario


def crear_alertas_seed():
    with SessionLocal() as session:
        docente_usuario = crear_o_actualizar_usuario(
            session,
            "alerta_docente@colegio.edu.co",
            "Alerta",
            "Docente",
            "Docente",
            estado="Activo",
        )
        estudiante_usuario = crear_o_actualizar_usuario(
            session,
            "alerta_estudiante@colegio.edu.co",
            "Estudiante",
            "Prueba",
            "Estudiante",
            estado="Activo",
        )

        grado = session.query(Grado).filter(Grado.nombre == "8A").first()
        if grado is None:
            grado = Grado(nombre="8A")
            session.add(grado)
            session.flush()

        materia = session.query(Materia).filter(Materia.nombre == "Matemáticas").first()
        if materia is None:
            materia = Materia(nombre="Matemáticas")
            session.add(materia)
            session.flush()

        periodo = session.query(PeriodoAcademico).filter(
            PeriodoAcademico.nombre == "2026-1",
            PeriodoAcademico.anio == 2026,
        ).first()
        if periodo is None:
            periodo = PeriodoAcademico(nombre="2026-1", anio=2026, estado="Abierto")
            session.add(periodo)
            session.flush()

        curso = session.query(Curso).filter(
            Curso.id_docente == docente_usuario.id_usuario,
            Curso.id_grado == grado.id_grado,
            Curso.id_materia == materia.id_materia,
            Curso.id_periodo == periodo.id_periodo,
        ).first()
        if curso is None:
            curso = Curso(
                id_docente=docente_usuario.id_usuario,
                id_grado=grado.id_grado,
                id_materia=materia.id_materia,
                id_periodo=periodo.id_periodo,
            )
            session.add(curso)
            session.flush()

        matricula = session.query(Matricula).filter(
            Matricula.id_estudiante == estudiante_usuario.id_usuario,
            Matricula.id_grado == grado.id_grado,
            Matricula.anio == periodo.anio,
        ).first()
        if matricula is None:
            matricula = Matricula(
                id_estudiante=estudiante_usuario.id_usuario,
                id_grado=grado.id_grado,
                anio=periodo.anio,
            )
            session.add(matricula)

        seccion = session.query(SeccionPorcentaje).filter(
            SeccionPorcentaje.id_curso == curso.id_curso,
            SeccionPorcentaje.nombre_seccion == "Quizzes",
        ).first()
        if seccion is None:
            seccion = SeccionPorcentaje(nombre_seccion="Quizzes", porcentaje=30.0, id_curso=curso.id_curso)
            session.add(seccion)
            session.flush()

        actividad = session.query(ActividadEvaluativa).filter(
            ActividadEvaluativa.id_seccion == seccion.id_seccion,
            ActividadEvaluativa.nombre == "Quiz 1",
        ).first()
        if actividad is None:
            actividad = ActividadEvaluativa(nombre="Quiz 1", fecha=date(2026, 7, 20), id_seccion=seccion.id_seccion)
            session.add(actividad)

        dia = session.query(DiaAsistible).filter(
            DiaAsistible.id_curso == curso.id_curso,
            DiaAsistible.fecha == date(2026, 7, 20),
        ).first()
        if dia is None:
            dia = DiaAsistible(id_curso=curso.id_curso, fecha=date(2026, 7, 20))
            session.add(dia)
            session.flush()

        asistencia = session.query(HistorialAsistencia).filter(
            HistorialAsistencia.id_dia == dia.id_dia,
            HistorialAsistencia.id_estudiante == estudiante_usuario.id_usuario,
        ).first()
        if asistencia is None:
            asistencia = HistorialAsistencia(id_dia=dia.id_dia, id_estudiante=estudiante_usuario.id_usuario, estado="Presente")
            session.add(asistencia)

        session.commit()
        print("Usuarios y datos de prueba creados:")
        print("  docente: alerta_docente@colegio.edu.co / clave123")
        print("  estudiante: alerta_estudiante@colegio.edu.co / clave123")
        print("Curso y datos de prueba listos para alertas")


if __name__ == "__main__":
    crear_alertas_seed()
