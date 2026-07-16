from app.models.usuario import Usuario
from app.models.administrador import Administrador
from app.models.docente import Docente
from app.models.acudiente import Acudiente 
from app.models.estudiante import Estudiante
from app.core.database import SessionLocal
from app.repositories.usuario import UsuarioRepository
from app.core.security import controlador_contrasena

usuarios = [
    {
        "nombres": "Samuel Andres",
        "apellidos": "Herrera Villero",
        "correo": "samuel.herrera@colegio.edu.co",
        "password": "Admin123!",
        "rol": "Administrador"
    },
    {
        "nombres": "Laura",
        "apellidos": "Gomez Perez",
        "correo": "laura.gomez@colegio.edu.co",
        "password": "Admin123!",
        "rol": "Administrador"
    },
    {
        "nombres": "Carlos",
        "apellidos": "Rodriguez Diaz",
        "correo": "carlos.rodriguez@colegio.edu.co",
        "password": "Docente123!",
        "rol": "Docente"
    },
    {
        "nombres": "Mariana",
        "apellidos": "Lopez Torres",
        "correo": "mariana.lopez@colegio.edu.co",
        "password": "Docente123!",
        "rol": "Docente"
    },
    {
        "nombres": "Juan",
        "apellidos": "Martinez Ruiz",
        "correo": "juan.martinez@colegio.edu.co",
        "password": "Docente123!",
        "rol": "Docente"
    },
    {
        "nombres": "Sofia",
        "apellidos": "Castro Silva",
        "correo": "sofia.castro@colegio.edu.co",
        "password": "Docente123!",
        "rol": "Docente"
    },
    {
        "nombres": "David",
        "apellidos": "Ramirez Moreno",
        "correo": "david.ramirez@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Camila",
        "apellidos": "Vargas Romero",
        "correo": "camila.vargas@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Andres",
        "apellidos": "Morales Rojas",
        "correo": "andres.morales@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Valentina",
        "apellidos": "Garcia Pinto",
        "correo": "valentina.garcia@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Miguel",
        "apellidos": "Suarez Medina",
        "correo": "miguel.suarez@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Daniela",
        "apellidos": "Ortega Gil",
        "correo": "daniela.ortega@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Felipe",
        "apellidos": "Pineda Cruz",
        "correo": "felipe.pineda@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Natalia",
        "apellidos": "Hernandez Lara",
        "correo": "natalia.hernandez@colegio.edu.co",
        "password": "Estudiante123!",
        "rol": "Estudiante"
    },
    {
        "nombres": "Jorge",
        "apellidos": "Sanchez Cardenas",
        "correo": "jorge.sanchez@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Paula",
        "apellidos": "Navarro Fuentes",
        "correo": "paula.navarro@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Luis",
        "apellidos": "Cifuentes Leon",
        "correo": "luis.cifuentes@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Isabella",
        "apellidos": "Mendoza Rios",
        "correo": "isabella.mendoza@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Diego",
        "apellidos": "Velasquez Arias",
        "correo": "diego.velasquez@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    },
    {
        "nombres": "Sara",
        "apellidos": "Quintero Vega",
        "correo": "sara.quintero@colegio.edu.co",
        "password": "Acudiente123!",
        "rol": "Acudiente"
    }
]

with SessionLocal() as session: 
    repositorio_usuario = UsuarioRepository(session)
    
    for datos in usuarios:
        usuario = Usuario(
            nombres = datos["nombres"],
            apellidos = datos["apellidos"],
            correo = datos["correo"],
            password_hash = controlador_contrasena.hashear(datos["password"]),
            rol = datos["rol"]  
        )
        
        if (usuario.rol == "Administrador"):
            repositorio_usuario.crear(usuario)
            rol_usuario = Administrador(
                id_admin = usuario.id_usuario
            )
            
        elif (usuario.rol == "Estudiante"):
            repositorio_usuario.crear(usuario)
            rol_usuario = Estudiante(
                id_estudiante = usuario.id_usuario,
                estado = "Activo"
            )
            
        elif (usuario.rol == "Acudiente"):
            repositorio_usuario.crear(usuario)
            rol_usuario = Acudiente(
                id_acudiente = usuario.id_usuario
            )
            
        elif (usuario.rol == "Docente"):
            repositorio_usuario.crear(usuario)
            rol_usuario = Docente(
                id_docente = usuario.id_usuario,
                estado = "Activo"
            )
        else: 
            print(f"Error en el rol {usuario.rol}")
            continue
        
        session.add(rol_usuario)
        
    session.commit()
