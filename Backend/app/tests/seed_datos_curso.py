from app.core.database import SessionLocal
from app.models.docente import Docente
from app.models.estudiante import Estudiante
from app.models.usuario import Usuario
from app.core.security import controlador_contrasena

with SessionLocal() as session:
    docente_usuario = session.query(Usuario).filter(Usuario.correo == "docente@colegio.com").first()
    if docente_usuario is None:
        docente_usuario = Usuario(
            nombres="Ana",
            apellidos="Gómez",
            correo="docente@colegio.com",
            password_hash=controlador_contrasena.hashear("123456"),
            rol="Docente",
        )
        session.add(docente_usuario)
        session.flush()
        docente = Docente(id_docente=docente_usuario.id_usuario, estado="Activo")
        session.add(docente)
    else:
        docente = session.get(Docente, docente_usuario.id_usuario)
        if docente is None:
            docente = Docente(id_docente=docente_usuario.id_usuario, estado="Activo")
            session.add(docente)

    estudiante_usuario = session.query(Usuario).filter(Usuario.correo == "estudiante@colegio.com").first()
    if estudiante_usuario is None:
        estudiante_usuario = Usuario(
            nombres="Luis",
            apellidos="Pérez",
            correo="estudiante@colegio.com",
            password_hash=controlador_contrasena.hashear("123456"),
            rol="Estudiante",
        )
        session.add(estudiante_usuario)
        session.flush()
        estudiante = Estudiante(id_estudiante=estudiante_usuario.id_usuario, estado="Activo")
        session.add(estudiante)
    else:
        estudiante = session.get(Estudiante, estudiante_usuario.id_usuario)
        if estudiante is None:
            estudiante = Estudiante(id_estudiante=estudiante_usuario.id_usuario, estado="Activo")
            session.add(estudiante)

    session.commit()
    print("Datos de prueba sembrados")
