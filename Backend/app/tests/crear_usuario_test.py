from app.core.database import SessionLocal
from app.models.usuario import Usuario
from app.models.docente import Docente
from app.models.administrador import Administrador
from app.core.security import controlador_contrasena

def crear_admin_real():
    db = SessionLocal()
    try:
        #1. Verificamos si el correo ya existe para no duplicarlo
        correo_test = "admin_real@colegio.edu.co"
        usuario_existente = db.query(Usuario).filter(Usuario.correo==correo_test).first()

        if usuario_existente:
            print(f"El usuario {correo_test} ya existe")
            return

        #2. Generamos hash para la contraseña admin123
        hash_seguro = controlador_contrasena.hashear("admin123")
        print(f"Generando hash... {hash_seguro}")

        #3. Creamos el registro en la tabla maestra 'usuario'
        nuevo_usuario = Usuario(
            nombres="Admin",
            apellidos="Principal",
            correo=correo_test,
            password_hash=hash_seguro, # Guardamos el Hash de verdad
            rol="Administrador"
        )
        db.add(nuevo_usuario)
        db.flush() #Guardar temporalmente

        nuevo_admin = Administrador(
            id_admin=nuevo_usuario.id_usuario
        )
        db.add(nuevo_admin)
        db.commit() #Consolidar los cambios en la base de datos
        print("Usuario admin de prueba inyectado con éxito")

    except Exception as e:
        db.rollback()
        print(f"Error al insertar: {e}")
    finally:
        db.close()

def crear_docente_real():
    db = SessionLocal()
    try:
        #1. Verificamos si el correo ya existe para no duplicarlo
        correo_test = "profesor_real@colegio.edu.co"
        usuario_existente = db.query(Usuario).filter(Usuario.correo==correo_test).first()

        if usuario_existente:
            print(f"El usuario {correo_test} ya existe")
            return
        
        #2. Generamos hash para la contraseña clave123
        hash_seguro = controlador_contrasena.hashear("clave123")
        print(f"Generando hash... {hash_seguro}")

        #3. Creamos el registro en la tabla maestra 'usuario'
        nuevo_usuario = Usuario(
            nombres="Diego",
            apellidos="Maradona",
            correo=correo_test,
            password_hash=hash_seguro, # Guardamos el Hash de verdad
            rol="Docente"
        )
        db.add(nuevo_usuario)
        db.flush() #Guardar temporalmente

        nuevo_docente = Docente(
            id_docente=nuevo_usuario.id_usuario,
            estado="Activo"
        )
        db.add(nuevo_docente)
        db.add(nuevo_docente)
        db.commit() #Consolidar los cambios en la base de datos
        print("Usuario de prueba inyectado con éxito")
    
    except Exception as e:
        db.rollback()
        print(f"Error al insertar: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    crear_docente_real()
    crear_admin_real()