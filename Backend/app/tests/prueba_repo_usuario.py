from app.repositories.usuario import UsuarioRepository
from app.core.database import SessionLocal
from app.models.usuario import Usuario
from sqlalchemy import select

def llamar_tabla(session):
    query = select(Usuario)
    resultados = session.execute(query).scalars()
    
    print("Tabla Usuario")
    for resultado in resultados:
        print(resultado)

    print()
    
with SessionLocal() as session:
    llamar_tabla(session)
         
    repositorio = UsuarioRepository(session) # Se le entrega la session
    
    print(f"ID 2 : {repositorio.buscar_por_id(2)} \n")

    # Se prueba creando un nuevo usuario
    
    nuevo_usuario = Usuario(
        nombres = "Samuel", 
        apellidos = "Herrera", 
        correo="saherrerav@unal.edu.co", 
        password_hash = "Hahssha",
        rol = "Administrador"
        )
    
    repositorio.crear(nuevo_usuario)
    
    llamar_tabla(session)
    
    # Se prueba actualizando ese usuario
    usuario_actualizar = repositorio.buscar_por_correo("saherrerav@unal.edu.co")
    usuario_actualizar.rol = "Docente"
    
    print("Se ha actualizado el usuario \n")
    llamar_tabla(session)
    
    # Se prueba eliminando ese usuario
    usuario_a_borrar = repositorio.buscar_por_correo("saherrerav@unal.edu.co")
    repositorio.eliminar(usuario_a_borrar)
    
    print("Se ha borrador el usuario \n")
    llamar_tabla(session)