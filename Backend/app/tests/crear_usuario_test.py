import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.database import SessionLocal, Base, engine
from app.models.usuario import Usuario
from app.models.docente import Docente
from app.models.administrador import Administrador
from app.core.security import controlador_contrasena


def crear_admin_real():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        correo_test = "admin_real@colegio.edu.co"
        usuario_existente = db.query(Usuario).filter(Usuario.correo == correo_test).first()

        if usuario_existente:
            print(f"El usuario {correo_test} ya existe")
            return

        hash_seguro = controlador_contrasena.hashear("admin123")
        print(f"Generando hash... {hash_seguro}")

        nuevo_usuario = Usuario(
            nombres="Admin",
            apellidos="Principal",
            correo=correo_test,
            password_hash=hash_seguro,
            rol="Administrador",
        )
        db.add(nuevo_usuario)
        db.flush()

        nuevo_admin = Administrador(id_admin=nuevo_usuario.id_usuario)
        db.add(nuevo_admin)
        db.commit()
        print("Usuario admin de prueba inyectado con éxito")

    except Exception as e:
        db.rollback()
        print(f"Error al insertar: {e}")
    finally:
        db.close()


def crear_docente_real():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        correo_test = "profesor_real@colegio.edu.co"
        usuario_existente = db.query(Usuario).filter(Usuario.correo == correo_test).first()

        if usuario_existente:
            print(f"El usuario {correo_test} ya existe")
            return

        hash_seguro = controlador_contrasena.hashear("clave123")
        print(f"Generando hash... {hash_seguro}")

        nuevo_usuario = Usuario(
            nombres="Diego",
            apellidos="Maradona",
            correo=correo_test,
            password_hash=hash_seguro,
            rol="Docente",
        )
        db.add(nuevo_usuario)
        db.flush()

        nuevo_docente = Docente(id_docente=nuevo_usuario.id_usuario, estado="Activo")
        db.add(nuevo_docente)
        db.commit()
        print("Usuario de prueba inyectado con éxito")

    except Exception as e:
        db.rollback()
        print(f"Error al insertar: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    crear_docente_real()
    crear_admin_real()